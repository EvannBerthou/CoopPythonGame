import Client

import pygame
from pygame.locals import *


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

            self.draw()

        self.close()

    def draw(self):
        self.win.fill((0,0,0))
        pygame.display.update()

    def close(self):
        self.game_socket.Listener.running = False
        pygame.quit()
        quit(0)

game = Game(800,800)
game.run()
