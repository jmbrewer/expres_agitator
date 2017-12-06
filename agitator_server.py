import socket
from xmlrpc.server import SimpleXMLRPCServer
import json
from expres_agitator import Agitator

class SocketServer:
    host = None
    port = None

    def __init__(self, host, port):
        self.set_host(host)
        self.set_port(port)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))

        while True: 
            sock.listen(1)
            conn, addr = sock.accept()
            print('Connection from: {}'.format(addr))
            serve_data(conn)

class AgitatorRPCServer(SimpleXMLRPCServer):

    def __init__(self, *args, comport='COM5', **kwargs):
        super().__init__(*args, **kwargs)
        self.agitator = Agitator(comport)
        self.register_instance(self.agitator)

if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    import serial
    import serial.tools.list_ports

    parser = ArgumentParser(description='Start a server for the agitator')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('-p', '--port', default=5000)
    parser.add_argument('-c', '--comport', default=None)
    args = parser.parse_args()

    if args.comport is None:
        for port in serial.tools.list_ports.comports():
            try:
                print('No COM Port listed')
                print('Trying port {}'.format(port))
                agitator = Agitator(port.device)
                del agitator
                print('Success!')
                args.comport = port.device
                break
            except (OSError, serial.SerialException):
                print('Port failed...')
        else:
            print('Could not find Agitator COM Port. Exiting...')
            sys.exit(0)

    server = AgitatorRPCServer((args.host, args.port), comport=args.comport, allow_none=True)
    print('Starting server on http://{}:{}'.format(args.host, args.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard Interrupt received. Exiting...')
        sys.exit(0)