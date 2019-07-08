from threading import Thread
import socket
import select
import sys
import struct

class GameSocket(Thread):
    def create_socket(self, ip, port):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((ip, port))
        return connection

    def send_message(self, message):
        self.socket.sendall(message.encode())

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
        self.data_size = 0

    def recv(self):
        raw_data_size = self.recvall(4)
        if raw_data_size:
            data_size = struct.unpack('>I', raw_data_size)[0]
            return self.recvall(data_size).decode()

    def recvall(self, size):
        data = b''
        while len(data) < size:
            packet = self.socket.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data


    def run(self):
        while self.running:
            ready = select.select([self.socket], [], [], 0.05)
            if ready[0]:
                data = self.recv()
                if data:
                    self.last_messages.append(data)

    def get_last_message(self):
        if len(self.last_messages) > 0:
            last_message = self.last_messages[-1]
            self.last_messages.remove(self.last_messages[-1])
            return last_message

class NetworkManger:
    def __init__(self, game):
        self.game = game

    def eval_message(self, message):
        commands = {
                "disconnect": self.disconnect,
                "map_hash": self.game.map.load_map,
                "player_sync": self.game.coop_player.sync
        }

        parts = message.split(' ')
        message_name = parts[0]
        message_args = parts[1:]

        if message_name in commands:
            commands[message_name](message_args)
        # else:
            # print("unknown message recieved : {}".format(message_name))
            # print(message_args)

    def update_network(self):
        last_message = self.game.game_socket.Listener.get_last_message()
        if last_message:
            self.eval_message(last_message)

    def disconnect(self, reason):
        reason = " ".join(reason)
        print("Connection to the server closed")
        print(reason)
        self.game.close()
