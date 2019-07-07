import Client

import pygame
from pygame.locals import *
import hashlib
import os

class Game:
    def __init__(self,w,h):
        self.w,self.h = w,h
        self.win = pygame.display.set_mode((self.w,self.h))
        self.game_socket = Client.GameSocket("127.0.0.1", 25565)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.update_network()
            self.draw()
        self.close()

    def load_new_map(self, args):
        map_name = args[0]
        map_hash = args[1]
        asset_folder = os.path.join(os.path.dirname(__file__), "assets")
        map_folder = os.path.join(asset_folder, "maps")
        abs_map_folder = os.path.abspath(map_folder)
        files = os.listdir(map_folder)

        if map_name in files:
            map_path = os.path.join(abs_map_folder, map_name)
            with open(map_path, 'r') as f:
                local_map_hash = hashlib.sha256(f.read().encode()).hexdigest()
                if local_map_hash == map_hash:
                    print("right map")
                else:
                    print("wrong map")

    
    def eval_message(self, message):
        commands = {
                "map_hash": self.load_new_map
        }

        message_name = message.split(' ')[0]
        message_args = message.split(' ')[1:]

        if message_name in commands:
            commands[message_name](message_args)

    def update_network(self):
        last_message = self.game_socket.Listener.get_last_message()
        if last_message:
            self.eval_message(last_message)

    def draw(self):
        self.win.fill((0,0,0))
        pygame.display.update()

    def close(self):
        self.game_socket.Listener.running = False
        pygame.quit()
        quit(0)

game = Game(800,800)
game.run()


"""
TODO:
    Map loading needs to be in its on class
    All network stuff needs to be in its on class
    Drawing needs to be in its on class
"""
