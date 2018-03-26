# import jsonrpclib.SimpleJSONRPCServer.SimpleJSONRPCServer as JSONRPCServer
# import jsonrpcserver.methods.Methods as JSONRPCServer
from xmlrpc.server import SimpleXMLRPCServer as RPCServer
from expres_agitator import Agitator

__DEFAULT_HOST__ = 'expres2.lowell.edu'
__DEFAULT_PORT__ = 5001
__DEFAULT_COMPORT__ = 'COM13'

class AgitatorServer(RPCServer):
    """
        Extension of builtin Python XMLRPC Server that registers an instance
        of the Agitator class (with the given COM port) at the given host and
        port.
    """
    def __init__(self, host, port, *args, comport=__DEFAULT_COMPORT__, **kwargs):
        super().__init__((host, port), *args, **kwargs)
        agitator = Agitator(comport)
        self.register_instance(agitator)

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

    # if args.comport is None:
    #     print('No COM Port listed')
    #     for port in serial.tools.list_ports.comports():
    #         agitator = None
    #         try:
    #             print('Trying port {}.'.format(port.device), end=' ')
    #             agitator = Agitator(port.device)
    #             del agitator
    #             print('Success!')
    #             args.comport = port.device
    #             break
    #         except (OSError, serial.SerialException):
    #             print('Serial connection failed...')
    #             del agitator
    #         except Exception as err:
    #             print('Unexpected error while connecting: {}'.format(err))
    #             del agitator
    #     else:
    #         print('Could not find Agitator COM Port. Exiting...')
    #         sys.exit(0)
    for _ in range(3):
        try:
            server = AgitatorServer(args.host, args.port,
                                    comport=args.comport,
                                    allow_none=True)
            break
        except Exception as err:
            print('Error while connecting to agitator: {}'.format(err))
            args.comport = input('Please enter new COM Port: ')
    else:
        print('Maximum three connection tries exceeded. Exiting...')
        sys.exit(0)

    print('Starting agitator server on http://{}:{}'.format(args.host, args.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Keyboard Interrupt received. Closing server and exiting...')
        sys.exit(0)