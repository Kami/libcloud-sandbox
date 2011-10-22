# General
SALT = 'asd390hhhhh87a'
IS_DEV = True
CODE_EXECUTE_TIMEOUT = 5
SESSION_TIMEOUT = 10 * 60

# Redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0

# Loggijg
LOG_FORMAT = '%(asctime)s %(levelname)s (%(ip)s - %(session_id)s) - %(message)s'

try:
    from local_settings import *
except:
    print 'ERROR: Failed to import local settings!'
    import traceback
    import sys
    traceback.print_stack()
    sys.exit(1)
