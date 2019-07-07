import pygame
import json

def from_json_data(json_data):
    tile_type = {
        "blank": Tile,
        "wall": Wall,
        "ground": Ground,
        "door": Door
    }

    data = json.loads(json_data)
    t = tile_type[data["type"]](data["x"], data["y"], 48)
    return t

class Tile:
    color = (255,255,255)
    def __init__(self,x,y,size):
        self.x,self.y = x,y
        self.size = size
        self.collide = False

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Tile.color,(self.x * self.size + offset, self.y * self.size + offset, self.size, self.size),1)

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": "blank"
            })
        return json_data
    
    #CALLED WHEN A PLAYER GOES ON THIS TILE
    def on_step(self):
        pass

    #CALLED WHEN A PLAYER LEAVE THIS TILE
    def on_leave(self):
        pass

class Ground(Tile):
    color = (255,248,220)
    def __init__(self,x,y,size):
        Tile.__init__(self,x,y,size)
        self.collide = False

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Ground.color,(self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": "ground"
            })
        return json_data

    def on_step(self):
        print("step on me")
    def on_leave(self):
        print("leaving me")

class Wall(Tile):
    color = (255,0,255)
    def __init__(self,x,y,size):
        Tile.__init__(self,x,y,size)
        self.collide = True

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Wall.color, (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": "wall"
            })
        return json_data

    def on_step(self):
        pass

    def on_leave(self):
        pass

class Door(Tile):
    color = (150,200,180)
    opened_color = (200,200,180)
    def __init__(self, x,y,size):
        Tile.__init__(self, x,y,size)
        self.collide = False
    
    def toggle(self):
        self.collide = not self.collide

    def draw(self, game, offset):
        color = Door.opened_color if self.collide else Door.color
        pygame.draw.rect(game.win, color, (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": "door"
            })
        return json_data

    def on_step(self):pass
    def on_leave(self):pass
