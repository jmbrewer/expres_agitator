from xmlrpc.client import ServerProxy

class RPCClient(ServerProxy):
    """
        Wrapper for ServerProxy that allow instantiation with only the host
        name and port value.
    """
    def __init__(self, host, port):
        self.url = 'http://{}:{}'.format(host, port)
        super().__init__(self.url)

if __name__ == '__main__':
    from argparse import ArgumentParser
    from time import sleep

    parser = ArgumentParser(description='Start a client connection to the agitator')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-t', '--time', type=float, default=60)
    args = parser.parse_args()

    agitator = RPCClient(args.host, args.port)
    agitator.start_agitation(args.time)
    sleep(time)
    agitator.stop_agitation()

