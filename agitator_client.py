from xmlrpc.client import ServerProxy

class AgitatorServer(ServerProxy):
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
    parser.add_argument('--host', default='localhost')
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-t', '--time', type=float, default=60)
    args = parser.parse_args()

    agitator = AgitatorServer(args.host, args.port)
    agitator.start(args.time)
    sleep(args.time)
    agitator.stop()
