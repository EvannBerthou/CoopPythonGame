import pygame
import json

def from_json_data(json_data):
    tile_type = {
        "blank": Tile,
        "wall": Wall,
        "ground": Ground,
        "door": Door,
        "plate": Pressure_plate
    }

    data = json.loads(json_data)
    t = tile_type[data["type"]](data)
    return t

class Tile:
    color = (255,255,255)
    tile_type = "blank"
    def __init__(self, data):
        self.x,self.y = data["x"], data["y"]
        self.size = 48
        self.collide = False

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Tile.color,(self.x * self.size + offset, self.y * self.size + offset, self.size, self.size),1)

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Tile.tile_type
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
    tile_type = "ground"
    def __init__(self,data):
        Tile.__init__(self,data)
        self.collide = False

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Ground.color,(self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Ground.tile_type
            })
        return json_data

    def on_step(self):
        print("step on me")
    def on_leave(self):
        print("leaving me")

class Wall(Tile):
    color = (255,0,255)
    tile_type = "wall"
    def __init__(self,data):
        Tile.__init__(self,data)
        self.collide = True

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Wall.color, (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Wall.tile_type
            })
        return json_data

    def on_step(self):
        pass

    def on_leave(self):
        pass

class Door(Tile):
    color = (255,0,0)
    opened_color = (0,255,0)
    tile_type = "door"
    def __init__(self,data):
        Tile.__init__(self,data)
        self.collide = data["default"] if "default" in data else True
    
    def toggle(self):
        print(self.collide, not self.collide)
        self.collide = not self.collide

    def draw(self, game, offset):
        color = Door.color if self.collide else Door.opened_color
        pygame.draw.rect(game.win, color, (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Door.tile_type,
            "default": int(self.collide)
            })
        return json_data

    def on_step(self):pass
    def on_leave(self):pass

class Pressure_plate(Tile):
    color = (0,255,150)
    tile_type = "plate"
    def __init__(self,data):
        Tile.__init__(self,data)
        self.collide = False
        self.linked_door_pos = self.get_linked_door_pos(data)
        self.linked_door = None
        self.player_on = 0

    def get_linked_door_pos(self, data):
        if "linked_door_x" in data:
            door_x = data["linked_door_x"]
            door_y = data["linked_door_y"]
            return (door_x, door_y)
        else:
            return (-1,-1)

    def link_to_door(self, door):
        self.linked_door = door

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Pressure_plate.color, (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Pressure_plate.tile_type,
            "linked_door_x": self.linked_door.x if self.linked_door else -1,
            "linked_door_y": self.linked_door.y if self.linked_door else -1
            })
        return json_data

    def on_step(self):
        if self.player_on == 0:
            self.linked_door.toggle()
        self.player_on += 1
    
    def on_leave(self):
        self.player_on -= 1
        if self.player_on == 0:
            self.linked_door.toggle()
