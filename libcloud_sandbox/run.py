from optparse import OptionParser

from tornadorpc import start_server

from libcloud_sandbox.server import Handler
from libcloud_sandbox.utils import get_and_setup_logger

def main():
    usage = 'usage: %prog --config=<path to config file>'
    parser = OptionParser(usage=usage)
    parser.add_option("--port", dest='port', default=6969,
                  help='Port to listen on', metavar='PORT')

    (options, args) = parser.parse_args()

    logger = get_and_setup_logger()
    Handler.logger = logger
    start_server(handlers=Handler, port=options.port)

main()
