import Player
import Tiles

import pygame
import os
import hashlib

#IT MAY BE BETTHER TO CACHE THE GAME INSTEAD OF GIVINT IT AS AN ARG
class Map:
    def get_map_folder(self):
        asset_folder = os.path.join(os.path.dirname(__file__), "assets")
        map_folder = os.path.join(asset_folder, "maps")
        abs_map_folder = os.path.abspath(map_folder)
        return abs_map_folder

    def draw(self, game):
        if self.map_data:
            for i in range(self.map_size):
                for j in range(self.map_size):
                    self.map_data.board[i][j].draw(game, self.offset)

    def load_map(self, args):
        map_name = args[0]
        map_hash = args[1]
        map_path = os.path.join(self.map_folder, map_name)

        if os.path.exists(map_path):
            with open(map_path, 'r') as f:
                local_map_hash = hashlib.sha256(f.read().encode()).hexdigest()
                if local_map_hash == map_hash:
                    self.map_data = MapData.from_file(map_path)
                    self.is_playing = True
                    self.create_player()
                else:
                    print("You don't have this map or your map is incompatible")
    
    def create_player(self):
        if self.game.team == "RED":
            self.game.player      = Player.Player(True, self.game, self.game.map.map_data.starting_red)
            self.game.coop_player = Player.Player(True, self.game, self.game.map.map_data.starting_blue)
        else:
            self.game.player      = Player.Player(True, self.game, self.game.map.map_data.starting_blue)
            self.game.coop_player = Player.Player(True, self.game, self.game.map.map_data.starting_red)

    def __init__(self, game):
        self.map_size = 16
        self.cell_size = 48
        self.offset = (800 - self.cell_size * self.map_size) / 2 #OFFSET ON EACH SIDE OF THE MAP
        self.map_folder = self.get_map_folder()
        self.map_data = None
        self.is_playing = False

        self.game = game

class MapData:
    def __init__(self, author, board, starting_red, starting_blue):
        self.author = author
        self.board = board
        self.starting_red  = starting_red
        self.starting_blue = starting_blue

    def from_file(path):
        import json
        with open(path, 'r') as f:
            json_data = f.read()
            data = json.loads(json_data)
            
            author = data["author"]
            board_data = data["board"]
            starting_red  = (0,0)
            starting_blue = (0,0)
            
            board = [[0 for _ in range(16)] for _ in range(16)]

            for i in range(16): #x
                for j in range(16): #y
                    board[i][j] = Tiles.from_json_data(board_data[i][j])
    
            #TODO: MOVE IT TO ITS OWN FUNCTION
            #LINKED PRESSURE PLATES TO DOORS AFTER ALL TILES ARE PLACED ON THE BOARD
            for i in range(16):
                for j in range(16):
                    tile = board[i][j]
                    if isinstance(tile, Tiles.Pressure_plate):
                        if tile.linked_door_pos != (-1,-1):
                            door = board[tile.linked_door_pos[1]][tile.linked_door_pos[0]]
                            tile.link_to_door(door)

                    if isinstance(tile, Tiles.Starting_tile):
                        if tile.team == "RED":
                            starting_red = (tile.x, tile.y)
                        elif tile.team == "BLUE":
                            starting_blue = (tile.x, tile.y)

            print("Map loaded")
            return MapData(author, board, starting_red, starting_blue)

    def save_map(self):
        import json
        tiles_data = [[0 for _ in range(16)] for _ in range(16)]
        for i in range(16):
            for j in range(16):
                tiles_data[i][j] = self.board[i][j].to_json_data()

        json_data = json.dumps({"author":self.author, "board":tiles_data})
        with open("assets/maps/md", 'w') as f:
            f.write(json_data)
