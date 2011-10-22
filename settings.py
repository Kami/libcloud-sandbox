LOG_FORMAT = '%(asctime)s %(levelname)s (%(ip)s - %(session_id)s) - %(message)s'

SALT = 'asd390hhhhh87a'
IS_DEV = True
CODE_EXECUTE_TIMEOUT = 5

try:
    from local_settings import *
except:
    print 'ERROR: Failed to import local settings!'
    import traceback
    import sys
    traceback.print_stack()
    sys.exit(1)
