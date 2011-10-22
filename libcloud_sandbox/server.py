import sys
import time
import logging
from hashlib import md5

from tornadorpc import async
from tornadorpc import config as trpcconfig
from tornado.ioloop import IOLoop
from tornadorpc.json import JSONRPCHandler
from celery.exceptions import TimeLimitExceeded

from libcloud_sandbox.constants import VALID_VERSIONS
from libcloud_sandbox.settings import SALT, IS_DEV
from libcloud_sandbox.settings import CODE_EXECUTE_TIMEOUT
from libcloud_sandbox.tasks.code_execute import execute


if IS_DEV:
    trpcconfig.short_errors = False
else:
    trpcconfig.verbose = False
    trpcconfig.short_errors = True


def require_valid_session_id(func):
    def wrapped(self, session_id, *args, **kwargs):
        if not session_id:
            return "Error: Missing session id"
        else:
            return func(self, *args, **kwargs)

    wrapped.__doc__ = func.__doc__
    wrapped.__dict__ = func.__dict__
    return wrapped

class Handler(JSONRPCHandler):
    logger = None

    def start(self):
        session_id = self._generate_session_id()
        self._log_msg('New client connected', session_id=session_id)
        return session_id

    def use(self, session_id, version):
        if version not in VALID_VERSIONS:
            return ('Invalid version %s.\nValid versions are: %s.' %
                   (version, ', '.join(VALID_VERSIONS)))
        else:
            # TODO: active_version
            return 'Version %s activated.' % (version)

    def info(self):
        msg = 'Type "help", "copyright", "credits" or "license" for more information.'
        return "Python %s (libcloud sandbox) on %s\n%s" % (sys.version[0:5],
                                                           sys.platform, msg)

    @async
    def evaluate(self, session_id, code):
        def callback(result):
            if isinstance(result, Exception):
                if isinstance(result, TimeLimitExceeded):
                    result = 'Error: Code execution timed out'
                else:
                    result = 'Error: Code execution failed'
            self.result(result)

        task = execute.apply_async(kwargs={'session_id': session_id,
                                           'code': code},
                                   connect_timeout=2, callback=callback)
        self._wait_for_result(task=task, callback=callback, timeout=5)

    def _wait_for_result(self, task, callback, timeout=CODE_EXECUTE_TIMEOUT):
        if timeout == 0:
            # celery y deadlock me?!?
            task.revoke()
            callback(TimeLimitExceeded())
        elif not task.ready():
            wait = 0.5
            IOLoop.instance().add_timeout(time.time() + wait,
                  lambda: self._wait_for_result(task, callback, timeout - wait))
        else:
            result = task.result
            callback(result)

    def _log_msg(self, msg, level=logging.INFO, session_id=None):
        extra = {'ip': self.request.remote_ip, 'session_id': session_id}
        self.logger.log(level, msg, extra=extra)

    def _ban_client(self, ip):
        pass

    def _generate_session_id(self):
        timestr = str(time.time())
        ip_address = self.request.remote_ip
        browser = self.request.headers.get('User-Agent', '')
        parts = [SALT, timestr, ip_address, browser]
        session_id = md5(':'.join(parts)).hexdigest()
        return session_id
