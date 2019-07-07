from threading import Thread
import socket

class GameSocket(Thread):
    def create_socket(self, ip, port):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((ip, port))
        return connection

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = self.create_socket(self.ip, self.port)
        self.Listener = Listener(self.socket)
        self.Listener.start()
    

class Listener(Thread):
    def __init__(self, socket):
        self.socket = socket
        self.running = True
        Thread.__init__(self)

    def run(self):
        while self.running:
            pass

