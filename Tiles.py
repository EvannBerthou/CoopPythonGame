import pygame
import json
import os

def from_json_data(json_data):
    tile_type = {
        "Empty": Empty,
        "wall": Wall,
        "ground": Ground,
        "door": Door,
        "plate": Pressure_plate,
        "starting": Starting_tile
    }

    data = json.loads(json_data)
    t = tile_type[data["type"]](data)
    return t

def load_tiles_folder():
    self_folder = os.path.abspath(os.path.dirname(__file__))
    asset_folder = os.path.join(self_folder, "assets")
    tiles_folder = os.path.join(asset_folder, "Tiles")
    return tiles_folder


class Tile:
    def __init__(self, data):
        self.x,self.y = data["x"], data["y"]
        self.size = 48
        self.collide = False
        self.tiles_folder = load_tiles_folder()

    def draw(self, game, offset): pass
    def to_json_data(self): pass    
    #CALLED WHEN A PLAYER GOES ON THIS TILE
    def on_step(self): pass
    #CALLED WHEN A PLAYER LEAVE THIS TILE
    def on_leave(self):pass
    def toggle(self):pass

class Empty(Tile):
    color = (255,255,255)
    tile_type = "Empty"
    def __init__(self,data):
        Tile.__init__(self, data)

    def draw(self, game, offset):
        pygame.draw.rect(game.win, Empty.color,(self.x * self.size + offset, self.y * self.size + offset, self.size, self.size),1)

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Empty.tile_type
            })
        return json_data

class Ground(Tile):
    color = (255,248,220)
    tile_type = "ground"

    def get_sprite_count(self):
        tile_folder = os.path.join(self.tiles_folder, "Ground")
        return len(os.listdir(tile_folder))

    def load_sprite(self, sprite_id):
        tile_folder = os.path.join(self.tiles_folder, "Ground")
        sprite_name = os.path.join(tile_folder, "{}.jpg".format(sprite_id))
        sprite = pygame.image.load(sprite_name)
        return sprite

    def __init__(self,data):
        Tile.__init__(self,data)
        self.collide = False
        self.sprite_id = 0
        self.max_sprite = self.get_sprite_count()
        self.sprite = self.load_sprite(data["sprite_id"] if "sprite_id" in data else 0)

    def draw(self, game, offset):
        game.win.blit(self.sprite, (self.x * self.size + offset, self.y * self.size + offset))

    def toggle(self):
        self.sprite_id = (self.sprite_id + 1) % self.max_sprite
        self.sprite = self.load_sprite(self.sprite_id)

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Ground.tile_type,
            "sprite_id": self.sprite_id
            })
        return json_data

    def on_step(self):pass
    def on_leave(self):pass

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
        if self.player_on == 0 and self.linked_door:
            self.linked_door.toggle()
        self.player_on += 1
    
    def on_leave(self):
        self.player_on -= 1
        if self.player_on == 0 and self.linked_door:
            self.linked_door.toggle()

class Starting_tile(Tile):
    blue = (0,0,200)
    red  = (200,0,0)
    color = red
    tile_type = "starting"
    def __init__(self,data):
        Tile.__init__(self,data)
        self.team = data["default"] if "default" in data else "RED"
        self.collide = False

    def toggle(self):
        if self.team == "RED": self.team = "BLUE"
        else: self.team = "RED"

    def draw(self, game, offset):
        color = Starting_tile.red if self.team == "RED" else Starting_tile.blue
        pygame.draw.rect(game.win, color, (self.x * self.size + offset, self.y * self.size + offset, self.size, self.size))

    def to_json_data(self):
        json_data = json.dumps({
            "x":int(self.x),
            "y":int(self.y),
            "type": Starting_tile.tile_type,
            "default": self.team
            })
        return json_data

    def on_step(self):pass
    def on_leave(self):pass
