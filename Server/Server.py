import socket
from threading import Thread
import select
import argparse
import curses

class ClientThread(Thread):
    clients = []
    def __init__(self, ip, port, clientsocket, drawer):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        self.running = True
        self.drawer = drawer

        self.drawer.addstr("[+] Nouveau Thread pour le client {}:{}".format(self.ip, self.port))
        ClientThread.clients.append(self)
        self.drawer.addstr("[!] {} clients connectés".format(len(ClientThread.clients)))

    def run(self):
        while self.running:
            ready = select.select([self.clientsocket], [], [], 0.05)
            if ready[0]:
                r = self.clientsocket.recv(4096).decode()
                if r.strip(' ') != "" and r != "stop":
                    self.drawer.addstr("-> {}".format(r))
                    for client in ClientThread.clients:
                        if client is not self:
                            client.clientsocket.send("{}:{} {}".format(self.ip,self.port,r).encode())#RENVOIE LE MESSAGE A TOUS LES AUTRES CLIENTS

                else:
                    self.drawer.addstr("[-] Déconnexion du client {}:{}".format(self.ip, self.port))
                    ClientThread.clients.remove(self)
                    self.running = False

class ServerDrawer(Thread):
    def __init__(self, server):
        self.stdscr = curses.initscr()
        Thread.__init__(self)
        self.current_input = ""
        self.size = self.stdscr.getmaxyx()
        self.current_row = 0

        self.server = server
        self.running = True

    def addstr(self, text):
        self.clear_input()
        self.stdscr.addstr("{}\n".format(str(text)))
        self.current_row += 1
        self.draw_input()
        self.stdscr.refresh()

    def clear_input(self):
        self.stdscr.move(self.current_row,0)
        self.stdscr.clrtoeol()

    def draw_input(self):
        self.stdscr.addstr(self.current_input)

    def send_command(self):
        self.addstr("")
        self.server.command(self.current_input.lower())
        self.current_input = ""
        self.clear_input()
        self.stdscr.move(self.current_row, 0)

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

    def run(self):
        while self.running:
            self.socket.listen(5)
            connexions, wlist, xlist = select.select([self.socket], [], [], 0.05)

            for connexion in connexions:
                (clientsocket, (ip,port)) = self.socket.accept()
                newthread = ClientThread(ip, port, clientsocket, self.drawer)
                newthread.start()
                self.drawer.addstr("[!] En écoute")

    def CloseServer(self):
        self.drawer.addstr("[!] Fermeture du serveur")
        self.drawer.running = False
        self.running = False
        for client in ClientThread.clients:
            client.running = False
        self.socket.close()
    
    def command(self, command):
        commands = {
                "quit": self.CloseServer
        }

        if command in commands:
            commands[command]()
        elif command != "":
            self.drawer.addstr("Invalid command")


parser = argparse.ArgumentParser(description="Server")
parser.add_argument('--port', type=int,default=50,help='the port you want to use for the server')
args = parser.parse_args()

server = Server(args.port)
server.run()
