import Player
import Tiles
import GameState

import pygame
import os
import hashlib

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
                    self.map_data = MapData.from_file(map_path, self.game)
                    self.is_playing = True
                    self.game.game_state = GameState.IN_GAME
                    self.game.game_socket.send_message("game_started")
                    self.create_player()
                else:
                    print("You don't have this map or your map is incompatible")

    def create_player(self):
        if self.game.team == "RED":
            self.game.player      = Player.Player(True, self.game, self.game.map.map_data.starting_red, (255,0,0))
            self.game.coop_player = Player.Player(False, self.game, self.game.map.map_data.starting_blue,(0,0,255))
        else:
            self.game.player      = Player.Player(True, self.game, self.game.map.map_data.starting_blue,(0,0,255))
            self.game.coop_player = Player.Player(False, self.game, self.game.map.map_data.starting_red, (255,0,0))

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

    def link_special_tiles(game, board):
        starting_red  = (0,0)
        starting_blue = (0,0)
        for i in range(16):
            for j in range(16):
                tile = board[i][j]
                tile.detect_sprite(board)
                if isinstance(tile, Tiles.Pressure_plate):
                    if tile.linked_door_pos != (-1,-1):
                        door = board[tile.linked_door_pos[1]][tile.linked_door_pos[0]]
                        tile.link_to_door(door)

                if isinstance(tile, Tiles.Teleporter):
                    if tile.linked_teleporter_pos != (-1,-1):
                        teleporter = board[tile.linked_teleporter_pos[1]][tile.linked_teleporter_pos[0]]
                        tile.link_to_teleporter(teleporter)

                if isinstance(tile, Tiles.Starting_tile):
                    if tile.team == "RED":
                        starting_red = (tile.x, tile.y)
                    elif tile.team == "BLUE":
                        starting_blue = (tile.x, tile.y)

                if isinstance(tile, Tiles.End_Tile):
                    if tile.other_end_tile_pos != (-1,-1):
                        other_end_tile = board[tile.other_end_tile_pos[1]][tile.other_end_tile_pos[0]]
                        tile.set_other_end_tile(other_end_tile)

                if isinstance(tile, Tiles.End_Tile):
                    tile.server_socket = game.game_socket.socket
        return board,starting_red,starting_blue

    def from_file(path, game):
        import json
        with open(path, 'r') as f:
            json_data = f.read()
            data = json.loads(json_data)

            author = data["author"]
            board_data = data["board"]

            board = [[0 for _ in range(16)] for _ in range(16)]

            for i in range(16): #x
                for j in range(16): #y
                    board[i][j] = Tiles.from_json_data(board_data[i][j])

            board,starting_red,starting_blue = MapData.link_special_tiles(game, board)

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
