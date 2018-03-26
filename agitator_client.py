from xmlrpc.client import ServerProxy

__DEFAULT_HOST__ = 'expres2.lowell.edu'
__DEFAULT_PORT__ = 5001

class AgitatorProxy(ServerProxy):
    """
        Wrapper for ServerProxy that allow instantiation with only the host
        name and port value.
    """
    def __init__(self, host, port, **kwargs):
        self.url = 'http://{}:{}'.format(host, port)
        super().__init__(self.url, **kwargs)

if __name__ == '__main__':
    from argparse import ArgumentParser
    from time import sleep

    parser = ArgumentParser(description='Start a client connection to the agitator')
    parser.add_argument('--host', default=__DEFAULT_HOST__)
    parser.add_argument('-p', '--port', type=int, default=__DEFAULT_PORT__)
    parser.add_argument('-t', '--time', type=float, default=10)
    args = parser.parse_args()

    agitator = AgitatorProxy(args.host, args.port)
    agitator.start(args.time)
    sleep(args.time)
    agitator.stop()
