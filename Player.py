import pygame

class Player:
    def __init__(self, local, offset, size):
        self.x, self.y = 0,0
        self.size = size
        self.draw_offset = offset
        self.local = local

    def update(self):
        pass

    def draw(self, game):
        pygame.draw.rect(game.win, (255,0,0), (self.x*self.size+self.draw_offset,self.y*self.size+self.draw_offset, self.size, self.size))
