import Tiles

import os
import argparse
import pygame
from pygame.locals import *

pygame.init()

class Info_Text:
    def __init__(self, x,y, font_size):
        self.x, self.y = x,y
        self.font = pygame.font.SysFont("Arial", font_size)
        self.set_text("")

    def set_text(self, text):
        self.text_to_render = self.font.render(text, 1, (255,255,255))

    def draw(self, game):
        game.win.blit(self.text_to_render, (self.x, self.y))


class Button:
    def __init__(self, x,y,size,tile, btn_type,id):
        self.x,self.y = x,y
        self.size = size
        self.selected = False
        self.tile = tile
        self.btn_type = btn_type
        self.id = id

    def draw(self, game):
        if isinstance(self.tile, type):
            color = self.tile.color
            pygame.draw.rect(game.win, color, (self.x, self.y, self.size, self.size))
            if self.selected:
                pygame.draw.rect(game.win, (150,150,0), (self.x, self.y, self.size, self.size), 3)

        elif isinstance(self.tile, pygame.Surface): #If it's a sprite
            game.win.blit(self.tile, (self.x, self.y))
            if self.selected:
                pygame.draw.rect(game.win, (255,255,255), (self.x, self.y, self.size, self.size), 3)

    def is_hovered(self):
        mouse_position = pygame.mouse.get_pos()
        return (self.x + self.size > mouse_position[0] > self.x
                and self.y + self.size > mouse_position[1] > self.y)

    def is_clicked(self):
        mouse_button_down = pygame.mouse.get_pressed()
        return mouse_button_down[0] and self.is_hovered()

    def click(self, game):
        if self.btn_type == "toolbar":
            game.linking = False
            if game.selected_button: game.selected_button.selected = False
            game.selected_button = self
            self.selected = True
            if game.selected_variant: game.selected_variant.selected = False
            game.info_text.set_text("{} tile selected".format(self.tile.tile_type))
            game.tile_variants = game.load_tile_variants()
            game.selected_variant = None

        elif self.btn_type == "variant":
            if game.selected_variant: game.selected_variant.selected = False
            self.selected = True
            game.selected_variant = self

class Game:
    def __init__(self,w,h, map_name):
        self.w,self.h = w,h
        self.win = pygame.display.set_mode((self.w, self.h))
        self.running = True
        self.grid_size = 16
        self.cell_size = 48
        self.offset = (self.w - (self.grid_size * self.cell_size)) / 2

        self.map_folder = self.get_map_folder()
        self.map_name = map_name
        self.board = None
        if os.path.exists(os.path.join(self.map_folder, self.map_name)):
            self.board = self.load_map_file()
        else:
            self.board = self.create_board()

        self.toolbar = self.create_toolbar()
        self.selected_button = self.toolbar[0]
        self.tile_variants = self.load_tile_variants()
        self.selected_variant = None

        self.linking_tile = None
        self.linking = False

        self.info_text = Info_Text(self.offset, self.h - 50, 24)

        self.end_tiles = []

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    self.on_key_pressed()
                    self.toolbar_shortcut(event.scancode)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        self.on_click()
                if pygame.mouse.get_pressed()[2]:
                    self.on_click()
            self.draw()
        pygame.quit()

    def toolbar_shortcut(self, key):
        if key >= 10 and key < 20:
            toolbar_id = key - 10
            mods = pygame.key.get_mods()
            if mods & KMOD_LSHIFT:
                if toolbar_id < len(self.tile_variants):
                    self.tile_variants[toolbar_id].click(self)
            else:
                if toolbar_id < len(self.toolbar):
                    self.toolbar[toolbar_id].click(self)

    def on_key_pressed(self):
        keyboard_state = pygame.key.get_pressed()
        if keyboard_state[K_s]:
            self.save_map()

    def on_click(self):
        mouse_position = pygame.mouse.get_pos()
        board_x = int((mouse_position[0] - self.offset) // self.cell_size)
        board_y = int((mouse_position[1] - self.offset) // self.cell_size)

        if board_x < 0 or board_x >= 16 or board_y < 0 or board_y >= 16: #IF OUTISDE THE BOARD
            for btn in self.toolbar + self.tile_variants:
                if btn.is_clicked():
                    btn.click(self)
        else:
            if self.linking:
                self.link_tiles(board_x, board_y)
                return

            #CREATE A NEW TILE
            if not isinstance(self.board[board_y][board_x], self.selected_button.tile):
                self.remove(self.board[board_y][board_x])
                self.board[board_y][board_x] = self.selected_button.tile({"x":board_x,"y":board_y})
                if self.selected_variant:
                    self.board[board_y][board_x].sprite = self.selected_variant.tile
                    self.board[board_y][board_x].sprite_id = self.selected_variant.id
                else:
                    self.board[board_y][board_x].detect_sprite(self.board)
                if isinstance(self.board[board_y][board_x], Tiles.End_Tile):
                    self.add_end_tile(board_y,board_x)
            #IF THE CLICKED TILE TYPE IS THE SAME AS THE TOOLBAR TILE TYPE
            else:
                tile = self.board[board_y][board_x]
                if self.selected_variant:
                    tile.sprite = self.selected_variant.tile
                tile.toggle(self.board)
                self.special_tiles(tile)

    def remove(self, tile):
        if isinstance(tile, Tiles.End_Tile):
            self.end_tiles.remove(tile)
            if len(self.end_tiles) > 0:
                self.end_tiles[0].unlink()

    def add_end_tile(self, board_y, board_x):
        if len(self.end_tiles) == 2:
            self.info_text.set_text("There is already 2 End Tiles on the board")
            self.board[board_y][board_x] = Tiles.Empty({"x":board_x,"y":board_y})
            return

        self.end_tiles.append(self.board[board_y][board_x])

        if len(self.end_tiles) == 2:
            self.end_tiles[0].set_other_end_tile(self.end_tiles[1])
            self.end_tiles[1].set_other_end_tile(self.end_tiles[0])

    def special_tiles(self,tile):
        if isinstance(tile, Tiles.Pressure_plate):
            self.linking_tile = tile
            self.linking = True
            self.info_text.set_text("Click on the door you want the plate to be linked to")

        if isinstance(tile, Tiles.Teleporter):
            self.linking_tile = tile
            self.linking = True
            self.info_text.set_text("Click on the teleporter you want the teleporter to be linked to")

    def link_tiles(self, board_x, board_y):
        tile = self.board[board_y][board_x]

        if isinstance(tile, Tiles.Door):
            self.link_plate_to_door(tile)
        elif isinstance(self.linking_tile, Tiles.Pressure_plate):
            self.info_text.set_text("You can only link a plate to a door")

        if isinstance(tile, Tiles.Teleporter):
            self.link_teleporters(self.linking_tile, tile)
        elif isinstance(self.linking_tile, Tiles.Teleporter):
            self.info_text.set_text("You can only link 2 teleporters")
            self.board[board_y][board_x] = Tiles.Empty({"x":board_x,"y":board_y})

        self.linking = False



    def link_plate_to_door(self, door):
        door_pos = (door.x, door.y)
        door = self.board[door_pos[1]][door_pos[0]]
        self.linking_tile.link_to_door(door)
        self.info_text.set_text("Plate linked to door")

    def link_teleporters(self, tep1, tep2):
        tep1.link_to_teleporter(tep2)
        tep2.link_to_teleporter(tep1)
        self.info_text.set_text("Teleporters linked")


    def draw(self):
        self.win.fill((0,0,0))
        self.draw_grid()
        self.draw_toolbar()
        self.draw_variants()
        self.info_text.draw(self)
        pygame.display.update()

    def create_board(self):
        return [[Tiles.Empty({"x":i,"y":j}) for i in range(self.grid_size)] for j in range(self.grid_size)]

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.board[i][j].draw(self, self.offset)

    def create_toolbar(self):
        tiles_id = {
            0: Tiles.Empty,
            1: Tiles.Wall,
            2: Tiles.Ground,
            3: Tiles.Door,
            4: Tiles.Pressure_plate,
            5: Tiles.Starting_tile,
            6: Tiles.Teleporter,
            7: Tiles.End_Tile
        }
        start_y = self.grid_size * self.cell_size + self.offset + 16

        buttons = []

        for i in range(len(tiles_id)):
            tile = tiles_id[i]
            buttons.append(Button(i * self.cell_size + self.offset, start_y, self.cell_size, tile, "toolbar", i))
        buttons[0].selected = True
        return buttons

    def draw_toolbar(self):
        for btn in self.toolbar:
            if btn.is_hovered(): btn.color = (255,0,0)
            else: btn.color = (0,255,0)
            btn.draw(self)

    def draw_variants(self):
        for btn in self.tile_variants:
            btn.draw(self)

    def load_tile_variants(self):
        start_y = self.grid_size * self.cell_size + self.offset + 16
        x_offset = len(self.toolbar) * self.cell_size + 32
        buttons = []
        for i,sprite in enumerate(self.selected_button.tile.load_all_sprites()):
            buttons.append(Button(i * (self.cell_size + 5) + self.offset + x_offset,start_y, self.cell_size, sprite, "variant", i))
        return buttons

    def get_map_folder(self):
        asset_folder = os.path.join(os.path.dirname(__file__), "assets")
        map_folder = os.path.join(asset_folder, "maps")
        abs_map_folder = os.path.abspath(map_folder)
        return abs_map_folder

    def relink(self, board):
        for i in range(16):
            for j in range(16):
                tile = board[i][j]
                if isinstance(tile, Tiles.Teleporter):
                    if tile.linked_teleporter_pos != (-1,-1):
                        tile.link_to_teleporter(board[tile.linked_teleporter_pos[1]][tile.linked_teleporter_pos[0]])
                if isinstance(tile, Tiles.Pressure_plate):
                    if tile.linked_door_pos != (-1,-1):
                        tile.link_to_door(board[tile.linked_door_pos[1]][tile.linked_door_pos[0]])
                if isinstance(tile, Tiles.End_Tile):
                    if tile.other_end_tile_pos != (-1,-1):
                        tile.set_other_end_tile(board[tile.other_end_tile_pos[1]][tile.other_end_tile_pos[0]])

    def load_map_file(self):
        import json
        path = os.path.join(self.map_folder, self.map_name)
        with open(path, 'r') as f:
            json_data = f.read()
            data = json.loads(json_data)
            board_data = data["board"]
            board = [[0 for _ in range(16)] for _ in range(16)]
            for i in range(16): #x
                for j in range(16): #y
                    board[i][j] = Tiles.from_json_data(board_data[i][j])

            self.relink(board)

            print("Map loaded")
            return board

    def save_map(self):
        self.info_text.set_text("Saving map...")
        import json
        tiles_data = [[0 for _ in range(16)] for _ in range(16)]
        for i in range(16):
            for j in range(16):
                tiles_data[i][j] = self.board[i][j].to_json_data()

        json_data = json.dumps({"author":"random", "board":tiles_data})
        file_path = os.path.join(self.map_folder, self.map_name)
        with open(file_path, 'w') as f:
            f.write(json_data)

        self.info_text.set_text("Map saved")


parser = argparse.ArgumentParser(description="Map Creator")
parser.add_argument('--name', type=str,default="map",help='the name of the map')
args = parser.parse_args()

game = Game(800,900, args.name)
game.run()
