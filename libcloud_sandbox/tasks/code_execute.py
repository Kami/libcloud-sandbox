"""
Based on "Try Python RPC Interpreter". For more info see NOTICE.
"""
import gc
import sys
import types
from StringIO import StringIO

from celery.task import task

from libcloud_sandbox.settings import CODE_EXECUTE_TIMEOUT
from libcloud_sandbox.settings import SESSION_TIMEOUT
from libcloud_sandbox.db import get_old_commands, write_code, expire_key


# list of disabled modules
modules = ['os', 'posixpath', 'subprocess', 'linecache', 'io', 'trace', 'rexec'
           'posix', 'popen2', 'urllib', 'shutil', 'glob', 'UserDict', 'copy_reg',
           'posixpath', 'sys', 'sys', 'socket', 'fnmatch', 'imghdr', 'macpath',
           'stat', 'ctypes', 'ctypes.util', 'urllib2', 'binhex', 'pyclbr', 'mailcap',
           'compiler.pycodegen', 'locale', 'webbrowser', 'getopt', 'getpass', 'cgi',
           'pdb', 'cgitb', 'uu', 'compileall', 'CGIHTTPServer', 'linecache', 'mailbox',
           'genericpath', 'pipes', 'mimify', 'symtable', 'unittest', 'SimpleHTTPServer'
           'tarfile', 'tabnanny', 'timeit', 'dircache', 'nntplib', 'whichdb', 'filecmp',
           'inspect', 'tempfile', 'site', 'UserString', 'mhlib', 'sndhdr', 'cProfile'
           'ftplib', 'shlex', 'smtpd', 'email.utils', 'py_compile', 'imputils', 'bdb'
           'xml', 'xml.sax', 'xml.sax.saxutils', 'pkgutil', 'asyncore', 'commands', 'mimetools'
           'httplib', 'macurl2path', 'ntpath', 'pty', 'SimpleXMLRPCServer', 'optparse',
           'base64', 'threading', 'posixfile', 'mimetypes', 'DocXMLRPCServer'
           'platform', 'compiler.pyassem', 'compiler.pycodegen', 'compiler.symbols',
           'compiler', 'bsddb', 'tokenize', 'SocketServer', 'calendar', 'copy', 'dbhash',
           'encodings', 'runpy', 'sgmllib', 'poplib', 'decimal', 'xmllib', 'aifc', 'test',
           'code', 'tabnanny', 'keyword', 'inspect', 'formatter', 'doctest', 'mhlib', 'UserString',
           'token', 'email', 'json', 'telnetlib', 'BaseHTTPServer', 'StringIO', 'imputil', 'rfc822',
           'contextlib', 'quopri', 'pydoc', 'dis', 'wsgiref', 'modulefinder',
           're', 'imp', '__builtin__']


def check_env(env, modules):
    "prevent exec('import x'.replace('x', 'os'))"
    module_emsg = "For security reason you can't import '%s' module"
    fun_emsg = "For security reason you can't import functions from '%s' module"
    file_emsg = "For security reason you can't open files"
    for k, v in env.items():
        if type(v) == types.ModuleType and v.__name__ in modules:
            return module_emsg % v.__name__
        elif type(v) == types.FileType and not v.__class__ == StringIO:
            return file_emsg
        elif type(v) == types.BuiltinFunctionType and v.__module__ in modules:
            if v.__module__ == 'posix':
                module = 'os'
            elif v.__module__ == 'posixpath':
                module = 'path'
            else:
                module = v.__module__
            return fun_emsg % module

# TODO: Use pysandbox / pypy sandbox
@task(time_limit=CODE_EXECUTE_TIMEOUT)
def execute(session_id, code):
    global modules
    logger = execute.get_logger()

    if code.strip() == '':
        return ''

    def no_import(module):
        raise 'For security reason you can\'t use __import__'

    def no_open(filename, mode='r'):
        raise 'For security reason you can open files'

    try:
        env = {'__import__': no_import, 'open': no_open, 'file': no_open}

        # Replay old commands
        old_commands = get_old_commands(key=session_id)
        old_code = '\n'.join(old_commands)

        fake_stdout = StringIO()
        __stdout = sys.stdout
        sys.stdout = fake_stdout

        exec(old_code, env)

        # don's show output from previous session
        fake_stdout.seek(0)
        fake_stdout.truncate()

        ret = eval(code, env)
        result = fake_stdout.getvalue()
        sys.stdout = __stdout
        msg = check_env(env, modules)

        if msg:
            return msg

        if ret:
            result += str(ret)

        return result
    except Exception, e:
        logger.error('Replaying history failed: %s', str(e))

        try:
            # Execute the new code
            exec(code, env)
        except:
            sys.stdout = __stdout
            import traceback
            buff = StringIO()
            traceback.print_exc(file=buff)

            # Remove the stack trace
            stack = buff.getvalue().replace('"<string>"', '"<JSON-RPC>"').split('\n')
            return '\n'.join([stack[0]] + stack[3:])
        else:
            sys.stdout = __stdout
            msg = check_env(env, modules)

            if msg:
                return msg

            # Save the code so it can be replayed on the next command
            write_code(key=session_id, code=code)
            expire_key(key=session_id, timeout=SESSION_TIMEOUT)

            gc.collect()
            return fake_stdout.getvalue()
