"""
    EXPRES Fiber Agitator Server module

    Provides an XMLRPC server that will send/receive messages
    to/from an Agitator object.
"""
from xmlrpc.server import SimpleXMLRPCServer as RPCServer
from expres_agitator import Agitator


__DEFAULT_HOST__ = "0.0.0.0" # 'expres2.lowell.edu'
__DEFAULT_PORT__ = 5001
__DEFAULT_COMPORT__ = 'COM13'


class AgitatorServer(RPCServer):
    """
        Extension of builtin Python XMLRPC Server that registers an instance
        of the Agitator class (with the given COM port) at the given host and
        port.
    """
    def __init__(self, host=__DEFAULT_HOST__, port=__DEFAULT_PORT__,
                 comport=__DEFAULT_COMPORT__, **kwargs):
        super().__init__((host, port), **kwargs)
        self.agitator = Agitator(comport)
        self.agitator.logger.info('Opening agitator server on http://{}:{}'.format(host, port))
        self.register_instance(self.agitator)

    def serve_forever(self):
        self.agitator.logger.info('Starting agitator server')
        self.kill = False
        while not self.kill:
            self.handle_request()

    def stop(self):
        self.agitator.logger.info('Stopping agitator server')
        self.kill = True


if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    import serial
    import serial.tools.list_ports

    parser = ArgumentParser(description='Start a server for the agitator')
    parser.add_argument('--host', default=__DEFAULT_HOST__)
    parser.add_argument('-p', '--port', type=int, default=__DEFAULT_PORT__)
    parser.add_argument('-c', '--comport', default=__DEFAULT_COMPORT__)
    args = parser.parse_args()
    
    for _ in range(3):
        try:
            server = AgitatorServer(args.host, args.port,
                                    comport=args.comport,
                                    allow_none=True,
                                    logRequests=False)
            break
        except Exception as err:
            print('Error while connecting to agitator: {}'.format(err))
            args.comport = input('Please enter new COM Port: ')
    else:
        print('Maximum three connection tries exceeded. Exiting...')
        sys.exit(0)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Keyboard Interrupt received. Closing server and exiting...')
        server.stop()
        sys.exit(0)