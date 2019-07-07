import pygame
import json

def from_json_data(json_data):
    data = json.loads(json_data)
    t = Tile(data["x"], data["y"], 48)
    return t

class Tile:
    def __init__(self,x,y,size):
        self.x,self.y = x,y
        self.size = size

    def draw(self, game, offset):
        pygame.draw.rect(game.win, (255,255,255), (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size), 1)

    def to_json_data(self):
        json_data = json.dumps({"x":int(self.x),"y":int(self.y)})
        return json_data
    
