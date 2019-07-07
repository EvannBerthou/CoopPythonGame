import Client
import Map
import Player

import pygame
from pygame.locals import *

class Game:
    def __init__(self,w,h):
        self.w,self.h = w,h
        self.win = pygame.display.set_mode((self.w,self.h))
        self.game_socket = Client.GameSocket("127.0.0.1", 25565)

        self.map = Map.Map()
        self.network_manager = Client.NetworkManger(self)
        self.player = Player.Player(True, self)
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        dt = self.clock.tick(60) / 1000
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.map.map_data:
                        self.player.on_key_pressed()

            self.network_manager.update_network()
            self.draw()
        self.close()

    def draw(self):
        self.win.fill((0,0,0))
        self.map.draw(self)

        if self.map.map_data: #IF A MAP IS LOADED
            self.player.draw()

        pygame.display.update()

    def close(self):
        self.game_socket.Listener.running = False
        pygame.quit()
        quit(0)

game = Game(800,800)
game.run()


"""
TODO:
"""
