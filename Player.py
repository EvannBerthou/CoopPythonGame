import pygame
from pygame.locals import *

class Player:
    def __init__(self, local, game):
        self.game = game
        self.x, self.y = 0,0
        self.size = game.map.cell_size
        self.draw_offset = game.map.offset
        self.local = local

    def on_key_pressed(self):
        #GOT PROBLEMS WHEN 2 KEYS ARE PRESSED ON THE SAME FRAME
        if self.local:
            keyboard_state = pygame.key.get_pressed()
            if keyboard_state[K_d]:
                self.x += 1
            if keyboard_state[K_a]:
                self.x -= 1
            if keyboard_state[K_w]:
                self.y -= 1
            if keyboard_state[K_s]:
                self.y += 1
            self.game.game_socket.send_message("player_sync {} {}".format(self.x, self.y))

    def update(self):
        pass

    def sync(self, args):
        self.x = int(args[0])
        self.y = int(args[1])

    def draw(self):
        pygame.draw.rect(self.game.win,(255,0,0),(self.x*self.size+self.draw_offset,self.y*self.size+self.draw_offset, self.size, self.size))
