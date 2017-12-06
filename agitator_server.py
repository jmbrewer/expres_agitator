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

    parser = ArgumentParser(description='Start a server for the agitator')
    parser.add_argument('type', default='rpc')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('-p', '--port', default=5000)
    args = parser.parse_args()

    if args.type.lower() == 'socket':
        print('SOCKET!')
    elif args.type.lower() == 'rpc':
        with AgitatorRPCServer((args.host, args.port), allow_none=True) as server:
            print('Starting server on http://{}:{}'.format(args.host, args.port))
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print('\nKeyboard Interrupt received. Exiting...')
                sys.exit(0)
    else:
        print('Invalid server type. Closing....')