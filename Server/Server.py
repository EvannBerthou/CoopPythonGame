from CommandMap import CommandMap

import socket
from threading import Thread
import select
import argparse
import curses
import os
import time
import sys
import struct
import json

class ClientThread(Thread):
    clients = []
    def __init__(self, ip, port, socket, drawer, server):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.running = True
        self.drawer = drawer
        self.server = server

        self.drawer.addstr("[+] New Thread for client {}:{}".format(self.ip, self.port))
        ClientThread.clients.append(self)
        self.drawer.addstr("[!] {} online clients".format(len(ClientThread.clients)))
        self.sendall("game_id {}".format(len(ClientThread.clients)))
        server.online_player += 1

    def run(self):
        while self.running:
            ready = select.select([self.socket], [], [], 0.05)
            if ready[0]:
                r = self.socket.recv(2048).decode()
                if r.strip(' ') != "":
                    self.player_message(r)
                    # self.drawer.addstr(r)
                else:
                    #WHEN 1 PLAYER IS DISCONNECTED, DISCONNECT ALL OTHER PLAYERS
                    server.online_player -= 1
                    self.drawer.addstr("[-] Client disconnect {}:{}".format(self.ip, self.port))
                    for client in ClientThread.clients:
                        ClientThread.clients.remove(client)
                        client.running = False

    def sendall(self, data):
        encoded = data.encode()
        data_len = len(encoded)
        msg = struct.pack('>I', data_len) + encoded
        total_sent = 0
        while total_sent < data_len:
            sent = self.socket.send(msg[total_sent:])
            total_sent += sent

    def resend_to_all_players(self, message):
        for client in ClientThread.clients:
            if client is not self:
                client.sendall(message)

    def player_message(self, message):
        commands = {
                "end_game": self.server.end_game,
                "game_started": self.server.on_game_started,
                "chat_message": self.handle_player_chat_message,
        }

        parts = message.split(' ')
        message_name = parts[0]
        message_args = parts[1:]

        if message_name in commands:
            commands[message_name](message_args)
        else:
            self.resend_to_all_players(message)

    def handle_player_chat_message(self, args):
        #start with 1 because 0 is the player name
        self.drawer.addstr(" ".join(args))
        if args[1].startswith("/"):
            name = args[1][1:] #remove the slash
            self.server.command("{} {}".format(name, args[2:]))
            #TODO: If the output is in multiple line (eg list_aliases), only the last line will be sent
            self.sendall("chat_message {}".format(self.drawer.last_message)) #Send the output to the player who performed the command
            self.sendall("chat_message {}".format(" ".join(args)))
        else:
            for client in ClientThread.clients:
                client.sendall("chat_message {}".format(" ".join(args)))

class ServerDrawer(Thread):
    def __init__(self, server):
        self.stdscr = curses.initscr()
        Thread.__init__(self)
        self.current_input = ""
        self.size = self.stdscr.getmaxyx()
        self.current_row = 0

        self.stdscr.scrollok(True)

        self.server = server
        self.running = True

        self.last_message = ""

    def addstr(self, text):
        self.clear_input()
        self.stdscr.addstr("{}\n".format(str(text)))
        self.current_row += 1

        if self.current_row >= self.size[0]:
            self.current_row = self.size[0] - 1

        self.draw_input()
        self.stdscr.refresh()

        self.last_message = text

    def clear_input(self):
        self.stdscr.move(self.current_row,0)
        self.stdscr.clrtoeol()

    def draw_input(self):
        self.stdscr.addstr("-> {}".format(self.current_input))

    def send_command(self):
        self.addstr(self.current_input)
        self.server.command(self.current_input.lower())
        self.current_input = ""
        self.clear_input()
        self.stdscr.move(self.current_row, 0)
        self.draw_input()

    def clear_screen(self, *args):
        self.current_row = 0
        self.stdscr.move(0,0)
        self.stdscr.clrtobot()
        self.draw_input()

    def run(self):
        while self.running:
            key = self.stdscr.getkey()
            if key in ("", "\n"):
                self.send_command()
            else:
                if key in ('KEY_BACKSPACE', '^?', '\x7f'):
                    self.current_input = self.current_input[:-1]
                else:
                    self.current_input += str(key)[0]
                self.clear_input()
                self.draw_input()
        curses.endwin()

class Server:
    def get_map_folder_path(self):
        parent_folder = os.path.join(os.path.dirname(__file__), "..")
        asset_folder = os.path.join(parent_folder, "assets")
        map_folder = os.path.join(asset_folder, "maps")
        abs_map_folder = os.path.abspath(map_folder)
        return abs_map_folder

    def initialize_socket(self):
        s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        self.drawer.addstr("[!] Listening")
        return s

    def __init__(self, port):
        self.drawer = ServerDrawer(self)
        self.drawer.start()
        self.port = port
        self.socket = self.initialize_socket()
        self.running = True

        self.command_map = CommandMap()

        self.online_player = 0

        self.map_folder = self.get_map_folder_path()
        self.start_time = time.time()
        self.loaded_map_name = []
        self.game_ended = False

        self.map_playlist = []

        self.aliases_file_path = self.get_aliases_file_path()
        self.aliases = {}
        self.command_map.execute(self, "load_aliases", "")


    def run(self):
        while self.running:
            self.socket.listen(5)
            connexions, wlist, xlist = select.select([self.socket], [], [], 0.05)

            for connexion in connexions:
                (socket, (ip,port)) = self.socket.accept()
                newthread = ClientThread(ip, port, socket, self.drawer, self)
                newthread.start()
                self.drawer.addstr("[!] Listening")

                if len(ClientThread.clients) > 2:
                    for client in ClientThread.clients[2:]: #from 3rd to last client in the list
                        client.socket.send("disconnect There is already 2 player in the game".encode())
                        client.socket.close()

    def CloseServer(self, *args):
        self.drawer.addstr("[!] Closing server")
        self.drawer.running = False
        self.running = False
        for client in ClientThread.clients:
            client.sendall("disconnect Server closing")
            client.running = False
        self.socket.close()

    def get_aliases_file_path(self):
        file_name = "aliases.json"
        self_file_path = os.path.dirname(__file__)
        file_path = os.path.join(self_file_path, file_name)
        return file_path

    def save_aliases(self):
        json_data = json.dumps(self.aliases)
        with open(self.aliases_file_path, 'w') as f:
            f.write(json_data)

    def get_alias(self, args):
        parts = args.split(' ')
        if parts[0] in self.aliases:
            alias = self.aliases[parts[0]].split(' ')
            alias_name = alias[0]
            alias_args = alias[1:] if len(alias) > 1 else None
            return (alias_name, alias_args)
        return (None, None)

    def command(self, command):
        alias_name,alias_args = self.get_alias(command)
        command_name = command.split(' ')[0]
        args = command.split(' ')[1:]

        if alias_name: command_name = alias_name #Override the alias given by the user with the actual command
        if alias_args: args = alias_args + args #args from the alias + args from the user

        self.command_map.execute(self, command_name, args)

    def send_message_to_all_client(self, message):
        for client in ClientThread.clients:
            client.sendall(message)

    def end_game(self, args):
        if not self.game_ended:
            self.drawer.addstr("Game ended")
            self.game_ended = True
            self.command_map.execute(self, "next_map", "")

    def on_game_started(self, args):
        self.game_started = False

parser = argparse.ArgumentParser(description="Server")
parser.add_argument('--port', type=int,default=25565,help='the port you want to use for the server')
args = parser.parse_args()

server = Server(args.port)
server.run()
