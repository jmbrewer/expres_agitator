import socket
import json

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