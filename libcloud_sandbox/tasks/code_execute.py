"""
Based on "Try Python RPC Interpreter". For more info see NOTICE.
"""
import sys
import traceback
from StringIO import StringIO

from celery.task import task
from sandbox import Sandbox, SandboxConfig

from libcloud_sandbox.settings import CODE_EXECUTE_TIMEOUT
from libcloud_sandbox.settings import SESSION_TIMEOUT
from libcloud_sandbox.db import get_old_commands, write_code, expire_key
from libcloud_sandbox.db import write_output_len, get_old_output_len


@task(time_limit=CODE_EXECUTE_TIMEOUT)
def execute(session_id, code):
    global modules

    if code.strip() == '':
        return ''

    buff = StringIO()
    __stdout = sys.stdout
    sys.stdout = buff

    sandbox = Sandbox(SandboxConfig('stdout'))

    old_commands = get_old_commands(key=session_id)
    old_code = '\n'.join(old_commands)

    try:
         sandbox.execute(old_code + '\n' + code)
    except Exception:
        buff = StringIO()
        traceback.print_exc(file=buff)

        # Remove the stack trace
        stack = buff.getvalue().replace('"<string>"', '"<JSON-RPC>"').split('\n')
        return '\n'.join([stack[0]] + stack[3:])
    else:
        full_output = buff.getvalue()
        output_len = get_old_output_len(key=session_id)

        write_code(key=session_id, code=code)
        expire_key(key=session_id, timeout=SESSION_TIMEOUT)

        if output_len:
            buff.seek(int(output_len))
            output = buff.read()
        else:
            output = buff.getvalue()

        write_output_len(key=session_id, output=full_output)
        return output
    finally:
        sys.stdout = __stdout
