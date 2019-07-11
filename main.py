import Client
import Map
import Player
import Tiles

import pygame
import argparse
from pygame.locals import *

class Game:
    def __init__(self,w,h, args):
        self.w,self.h = w,h
        self.win = pygame.display.set_mode((self.w,self.h))
        self.game_socket = Client.GameSocket(args.ip, args.port)

        self.map = Map.Map(self)
        self.network_manager = Client.NetworkManger(self)

        self.team = None
        self.player = None
        self.coop_player = None

        self.clock = pygame.time.Clock()
        self.tick = 0.0

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            self.tick += dt
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.map.map_data:
                        self.player.on_key_pressed()

            self.network_manager.update_network()
            self.update()
            self.draw()
        self.close()

    def update(self):
        if self.tick >= 500:
            if self.map.is_playing:
                self.player.update()
            self.tick = 0

    def draw(self):
        self.win.fill((0,0,0))
        self.map.draw(self)
        if self.map.is_playing: #IF A MAP IS LOADED
            self.player.draw()
            self.coop_player.draw()

        pygame.display.update()

    def close(self):
        self.game_socket.Listener.running = False
        pygame.quit()
        quit(0)

parser = argparse.ArgumentParser(description="Server")
parser.add_argument('--port', type=int,default=25565,help='the port you want to use for the server')
parser.add_argument('--ip',   type=str,default="127.0.0.1",help='the port you want to use for the server')
args = parser.parse_args()

game = Game(800,800, args)
game.run()
