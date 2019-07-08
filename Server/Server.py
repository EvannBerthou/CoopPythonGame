import socket
from threading import Thread
import select
import argparse
import curses
import os
import hashlib
import time
import sys
import struct

class ClientThread(Thread):
    clients = []
    def __init__(self, ip, port, socket, drawer):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.running = True
        self.drawer = drawer

        self.drawer.addstr("[+] Nouveau Thread pour le client {}:{}".format(self.ip, self.port))
        ClientThread.clients.append(self)
        self.drawer.addstr("[!] {} clients connectés".format(len(ClientThread.clients)))
        self.sendall("game_id {}".format(len(ClientThread.clients)))

    def run(self):
        while self.running:
            ready = select.select([self.socket], [], [], 0.05)
            if ready[0]:
                r = self.socket.recv(2048).decode()
                if r.strip(' ') != "" and r != "stop":
                    for client in ClientThread.clients:
                        if client is not self:
                            client.sendall(r)
                else:
                    self.drawer.addstr("[-] Déconnexion du client {}:{}".format(self.ip, self.port))
                    ClientThread.clients.remove(self)
                    self.running = False

    def sendall(self, data):
        data = struct.pack('>I', len(data)) + data.encode()
        total_sent = 0
        while total_sent < len(data):
            sent = self.socket.send(data[total_sent:])
            total_sent += sent

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

    def addstr(self, text):
        self.clear_input()
        self.stdscr.addstr("{}\n".format(str(text)))
        self.current_row += 1

        if self.current_row >= self.size[0]:
            self.current_row = self.size[0] - 1

        self.draw_input()
        self.stdscr.refresh()

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
        self.drawer.addstr("[!] En écoute")
        return s

    def __init__(self, port):
        self.drawer = ServerDrawer(self)
        self.drawer.start()
        self.port = port
        self.socket = self.initialize_socket()
        self.running = True

        self.map_folder = self.get_map_folder_path()
        self.start_time = time.time()
        self.loaded_map_name = list()

    def run(self):
        while self.running:
            self.socket.listen(5)
            connexions, wlist, xlist = select.select([self.socket], [], [], 0.05)

            for connexion in connexions:
                (socket, (ip,port)) = self.socket.accept()
                newthread = ClientThread(ip, port, socket, self.drawer)
                newthread.start()
                self.drawer.addstr("[!] En écoute")

                if len(ClientThread.clients) > 2:
                    for client in ClientThread.clients[2:]: #from 3rd to last client in the list
                        client.socket.send("disconnect There is already 2 player in the game".encode())
                        client.socket.close()

    def CloseServer(self, *args):
        self.drawer.addstr("[!] Fermeture du serveur")
        self.drawer.running = False
        self.running = False
        for client in ClientThread.clients:
            client.sendall("disconnect Server closing")
            client.running = False
        self.socket.close()
    
    def player_count(self, *args):
        self.drawer.addstr("{} players conncted".format(len(ClientThread.clients)))

    def uptime(self, *args):
        now = time.time()
        elapse_time = now - self.start_time
        time_format = time.strftime("%M:%S", time.gmtime(elapse_time))
        self.drawer.addstr("{}".format(time_format))

    def command(self, command):
        commands = {
                "quit": self.CloseServer,
                "exit": self.CloseServer,
                "load_map": self.load_map,
                "reload_map": self.reload_map,
                "clear": self.drawer.clear_screen,
                "list": self.player_count,
                "uptime": self.uptime
        }

        command_name = command.split(' ')[0]
        args = command.split(' ')[1:]

        if command_name in commands:
            commands[command_name](args)
        elif command != "":
            self.drawer.addstr("Invalid command")


    def hash_map(self, map_path):
        with open(map_path, 'r') as f:
            map_hash = hashlib.sha256(f.read().encode()).hexdigest()
            return map_hash

    def load_map(self, args):
        if len(ClientThread.clients) != 2:
            self.drawer.addstr("You need to be 2 players in order to play and load a map")
            return

        map_name = args[0]
        map_path = os.path.join(self.map_folder, map_name)
        self.drawer.addstr(map_path)
        if os.path.exists(map_path):
            map_hash = self.hash_map(map_path)
            self.drawer.addstr("Map hash: {}".format(map_hash))
            self.send_message_to_all_client("map_hash {} {}".format(map_name, map_hash))
            self.loaded_map_name.clear()
            self.loaded_map_name.append(map_name)
        else:
            self.drawer.addstr("The map {} does not exist".format(map_name))
            self.loaded_map_path = None

    def reload_map(self, args):
        if self.loaded_map_name:
            self.load_map(self.loaded_map_name)
        else:
            self.drawer.addstr("No map is currently loaded")

    def send_message_to_all_client(self, message):
        for client in ClientThread.clients:
            client.sendall(message)


parser = argparse.ArgumentParser(description="Server")
parser.add_argument('--port', type=int,default=50,help='the port you want to use for the server')
args = parser.parse_args()

server = Server(args.port)
server.run()
