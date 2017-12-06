import socket
from xmlrpc.server import SimpleXMLRPCServer
import json
import sys
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

if __name__ == '__main__':
    from argpargse import ArgumentParser

    parser = ArgumentParser(description='Start a server for the agitator')
    parser.add_argument('type', default='rpc')
    parser.add_argument('-h', '--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=5000)
    args = parser.parse_args()

    if args.type.lower() == 'socket':
        print('SOCKET!')
    elif args.type.lower() == 'rpc':
        print('RPC!')
    else:
        print('Invalid server type. Closing....')