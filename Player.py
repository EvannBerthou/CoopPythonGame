import pygame
from pygame.locals import *

class Player:
    def __init__(self, local, game):
        self.game = game
        self.x, self.y = 0,0
        self.size = game.map.cell_size
        self.draw_offset = game.map.offset
        self.local = local

    def check_border(self, x_move, y_move):
        if self.x + x_move < 0 or self.x + x_move >= 16: return False
        if self.y + y_move < 0 or self.y + y_move >= 16: return False
        return True

    def on_key_pressed(self):
        if self.local:
            keyboard_state = pygame.key.get_pressed()
            x_move = keyboard_state[K_d] - keyboard_state[K_a]
            y_move = keyboard_state[K_s] - keyboard_state[K_w]

            if self.check_border(x_move, y_move):
                self.x += x_move
                self.y += y_move
                self.game.game_socket.send_message("player_sync {} {}".format(self.x, self.y))

    def update(self):
        pass

    def sync(self, args):
        #Set the position of the coop player
        self.x = int(args[0])
        self.y = int(args[1])

    def draw(self):
        pygame.draw.rect(self.game.win,(255,0,0),(self.x*self.size+self.draw_offset,self.y*self.size+self.draw_offset, self.size, self.size))
