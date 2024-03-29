from threading import Thread
import socket
import select
import sys
import struct
import time

class GameSocket:
    def create_socket(ip, port):
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((ip, port))
            return connection
        except:
            print("Could not connection to {}:{}".format(ip,port))
            return None

    def send_message(self, message):
        self.sendall(message)

    def __init__(self, socket):
        self.socket = socket
        self.Listener = Listener(self.socket)
        self.Listener.start()

    def sendall(self, message):
        encoded = message.encode()
        data_len = len(encoded)
        msg = struct.pack('>I', data_len) + encoded
        total_sent = 0
        while total_sent < data_len:
            sent = self.socket.send(encoded[total_sent:])
            total_sent += sent
        time.sleep(0.01) #IT WORKS SOMEHOW BUT ITS PRETTY BAD


class Listener(Thread):
    def __init__(self, socket):
        self.socket = socket
        self.running = True
        Thread.__init__(self)
        self.last_messages = []
        self.data_size = 0

    #WHEN USING TELEPORTERS: SENDING 16 BITS, RECIEVING 32 ????
    def recv(self):
        raw_data_size = self.recvall(4)
        if raw_data_size:
            data_size = struct.unpack('>I', raw_data_size)[0]
            data = self.recvall(data_size)
            if data:
                return data.decode()

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
        self.game_id = -1

    def eval_message(self, message):
        commands = {
                "disconnect": self.disconnect,
                "map_hash": self.game.map.load_map,
                "player_sync": self.sync_player,
                "game_id": self.set_game_id,
                "chat_message": self.send_chat_message,
        }

        parts = message.split(' ')
        message_name = parts[0]
        message_args = parts[1:]

        if message_name in commands:
            commands[message_name](message_args)

    def update_network(self):
        last_message = self.game.game_socket.Listener.get_last_message()
        if last_message:
            self.eval_message(last_message)

    def send_chat_message(self, args):
        msg = " ".join(args)
        self.game.chat_box.add_message(msg)

    def set_game_id(self, args):
        self.game_id = int(args[0])
        self.game.team = "RED" if self.game_id == 1 else "BLUE"

    def sync_player(self, args):
        if self.game.coop_player:
            self.game.coop_player.sync(args)

    def disconnect(self, reason):
        reason = " ".join(reason)
        print("Connection to the server closed")
        print(reason)
        self.game.close()
