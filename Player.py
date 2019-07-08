import pygame
from pygame.locals import *

class Player:
    def __init__(self, local, game):
        self.game = game
        self.x, self.y = 0,0
        self.size = game.map.cell_size
        self.draw_offset = game.map.offset
        self.local = local
    
    #check if the next position is outside the game board
    def check_border(self, x_move, y_move):
        if self.x + x_move < 0 or self.x + x_move >= 16: return False
        if self.y + y_move < 0 or self.y + y_move >= 16: return False
        return True

    #check if the next position is inside a tile which blocks collision
    def check_collision(self, x_move, y_move):
        next_x = self.x + x_move
        next_y = self.y + y_move
        tile = self.game.map.map_data.board[next_y][next_x]
        return not tile.collide

    def move(self, new_x, new_y):
        if self.game.map.is_playing:
            self.game.map.map_data.board[self.y][self.x].on_leave()
            self.x = new_x
            self.y = new_y
            self.game.map.map_data.board[self.y][self.x].on_step()

    def on_key_pressed(self):
        if self.local:
            keyboard_state = pygame.key.get_pressed()
            x_move = keyboard_state[K_d] - keyboard_state[K_a]
            y_move = keyboard_state[K_s] - keyboard_state[K_w]

            if self.check_border(x_move, y_move):
                if self.check_collision(x_move, y_move):
                    self.move(self.x + x_move, self.y + y_move)
                    self.update()

    def update(self):
        self.game.game_socket.send_message("player_sync {} {}".format(self.x, self.y))

    def sync(self, args):
        #TODO: if moving distance is > 2 tiles, move first 1 case then the other instead of teleporting
        #Set the position of the coop player
        try:
            self.move(int(args[0]), int(args[1]))
        except Exception as err:
            print("error while parsing args {} : {}".format(args, err))

    def draw(self):
        pygame.draw.rect(self.game.win,(255,0,0),(self.x*self.size+self.draw_offset,self.y*self.size+self.draw_offset, self.size, self.size))
