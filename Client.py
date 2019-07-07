from threading import Thread
import socket
import select

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
        self.last_messages = []

    def run(self):
        while self.running:
            ready = select.select([self.socket], [], [], 0.05)
            if ready[0]:
                recieved = self.socket.recv(4096).decode()
                if recieved:
                    self.last_messages.append(recieved)

    def get_last_message(self):
        if len(self.last_messages) > 0:
            last_message = self.last_messages[-1]
            self.last_messages.remove(self.last_messages[-1])
            return last_message
