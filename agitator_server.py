# import jsonrpclib.SimpleJSONRPCServer.SimpleJSONRPCServer as JSONRPCServer
# import jsonrpcserver.methods.Methods as JSONRPCServer
from xmlrpc.server import SimpleXMLRPCServer as RPCServer
from expres_agitator import Agitator

class AgitatorServer(RPCServer):
    """
        Extension of builtin Python XMLRPC Server that registers an instance
        of the Agitator class (with the given COM port) at the given host and
        port.
    """
    def __init__(self, host, port, *args, comport='COM5', **kwargs):
        super().__init__((host, port), *args, **kwargs)
        agitator = Agitator(comport)
        self.register_instance(agitator)

if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    import serial
    import serial.tools.list_ports

    parser = ArgumentParser(description='Start a server for the agitator')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-c', '--comport', default=None)
    args = parser.parse_args()

    if args.comport is None:
        print('No COM Port listed')
        for port in serial.tools.list_ports.comports():
            try:
                print('Trying port {}.'.format(port.device), end=' ')
                agitator = Agitator(port.device)
                del agitator
                print('Success!')
                args.comport = port.device
                break
            except (OSError, serial.SerialException):
                print('Failed...')
        else:
            print('Could not find Agitator COM Port. Exiting...')
            sys.exit(0)

    server = AgitatorServer(args.host, args.port,
                            comport=args.comport,
                            allow_none=True)
    print('Starting server on http://{}:{}'.format(args.host, args.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Keyboard Interrupt received. Closing server and exiting...')
        sys.exit(0)