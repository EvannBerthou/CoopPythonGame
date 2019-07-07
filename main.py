import Client
import Map

import pygame
from pygame.locals import *
import hashlib
import os

class Game:
    def get_map_folder(self):
        asset_folder = os.path.join(os.path.dirname(__file__), "assets")
        map_folder = os.path.join(asset_folder, "maps")
        abs_map_folder = os.path.abspath(map_folder)
        return abs_map_folder

    def __init__(self,w,h):
        self.w,self.h = w,h
        self.win = pygame.display.set_mode((self.w,self.h))
        self.game_socket = Client.GameSocket("127.0.0.1", 25565)

        self.map_folder = self.get_map_folder()
        self.map = Map.Map(self.map_folder)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.update_network()
            self.draw()
        self.close()


    
    def eval_message(self, message):
        commands = {
                "map_hash": self.map.load_map
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
        self.map.draw(self)
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
