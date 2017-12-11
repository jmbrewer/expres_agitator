import socket

class SocketClient:
    """
    Parent class that contains methods to communicate through a socket
    """    
    name = 'Unknown Server'
    module = ExpresModule
    connected = False
    host = None
    port = None

    def __init__(self, host, port):
        self.setHost(host)
        self.setPort(port)

    @classmethod
    def setHost(cls, host):
        cls.host = host

    @classmethod
    def setPort(cls, port):
        cls.port = port
    
    @classmethod
    def connect(cls):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((cls.host, cls.port))
            cls.connected = True
            return sock
        except OSError as msg:
            module.logger.error('Cannot connect to {}: {}'.format(cls.name, msg))
            cls.connected = False
            return None

    @classmethod
    def disconnect(cls, a_socket):
        a_socket.close()
        cls.connected = False

    @classmethod
    def sendMessage(cls, msg):
        # send size of message in 4 bytes
        sz = '{length:4d}'.format(length=len(msg))
        sock = cls.connect()
        if sock is not None:
            sock.send(sz.encode('utf-8'))
            sock.send(msg.encode('utf-8'))
            cls.disconnect(sock)
        else:
            module.logger.error('{} connection error while sending'.format(cls.name))

    @classmethod
    def sendRecvMessg(cls, msg):
        # send size of message in 4 bytes, 
        sz = '{length:4d}'.format(length=len(msg))
        sock = cls.connect()
        if cls.connected:
            sock.send(sz.encode('utf-8'))
            sock.send(msg.encode('utf-8'))
            resp = sock.recv(4).decode()
            resp = sock.recv(int(resp)).decode()
            cls.disconnect(sock)
            return resp
        else:
            module.logger.error('{} connection error while receiving'.format(cls.name))
            return {'error': 'cannot connect to {}'.format(cls.name)}

    def preparePayload(self, method, params):
        msg = {'method': method,
               'params': params}
        return json.dumps(msg)  

class AgitatorSocketClient(SocketClient):
    """
    Class containing the client to communicate with the agitator server
    """
    name = 'Agitator'
    module = Agitator

    def __init__(self, host, port):
        super().__init__(host, port)

    def startAgitation(self, exp_time):
        msg = self.preparePayload('start-agitation', {'exp_time': exp_time})
        try:
            self.sendMessage(msg)
        except Exception as err:
            module.logger.error('Unable to start agitation: {}'.format(err))

    def stopAgitation(self, exp_time):
        msg = self.preparePayload('stop-agitation')
        try:
            self.sendMessage(msg)
        except Exception as err:
            module.logger.error('Unable to stop agitation: {}'.format(err))