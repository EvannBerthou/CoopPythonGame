import Tiles

import os
import argparse
import pygame
from pygame.locals import *

class Button:
    def __init__(self, x,y,size,tile):
        self.x,self.y = x,y
        self.size = size
        self.selected = False
        self.tile = tile

    def draw(self, game):
        color = self.tile.color
        pygame.draw.rect(game.win, color, (self.x, self.y, self.size, self.size))
        if self.selected:
            pygame.draw.rect(game.win, (150,150,0), (self.x, self.y, self.size, self.size), 3)

    def is_hovered(self):
        mouse_position = pygame.mouse.get_pos()
        return (self.x + self.size > mouse_position[0] > self.x 
                and self.y + self.size > mouse_position[1] > self.y)

    def is_clicked(self):
        mouse_button_down = pygame.mouse.get_pressed()
        return mouse_button_down[0] and self.is_hovered()

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

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    self.on_key_pressed()
            
            if pygame.mouse.get_pressed()[0]:
                self.on_click()

            self.draw()
        pygame.quit()

    def on_key_pressed(self):
        keyboard_state = pygame.key.get_pressed()
        if keyboard_state[K_s]:
            self.save_map()

    def on_click(self):
        mouse_position = pygame.mouse.get_pos()
        board_x = int((mouse_position[0] - self.offset) // self.cell_size)
        board_y = int((mouse_position[1] - self.offset) // self.cell_size)

        if board_x < 0 or board_x >= 16 or board_y < 0 or board_y >= 16: #IF OUTISDE THE BOARD
            for btn in self.toolbar:
                if btn.is_clicked():
                    if self.selected_button: self.selected_button.selected = False
                    self.selected_button = btn
                    btn.selected = True
        else:
            self.board[board_y][board_x] = self.selected_button.tile(board_x, board_y, self.cell_size)
        

    def draw(self):
        self.win.fill((0,0,0))
        self.draw_grid()
        self.draw_toolbar()
        pygame.display.update()

    def create_board(self):
        return [[Tiles.Tile(i,j,self.cell_size) for i in range(self.grid_size)] for j in range(self.grid_size)]

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.board[i][j].draw(self, self.offset)

    def create_toolbar(self):
        tiles_id = {
            0: Tiles.Tile,
            1: Tiles.Wall
        }
        start_y = self.grid_size * self.cell_size + self.offset + 16
        
        buttons = []

        for i in range(len(tiles_id)):
            tile = tiles_id[i]
            buttons.append(Button(i * self.cell_size + self.offset, start_y, self.cell_size, tile))
        buttons[0].selected = True
        return buttons

    def draw_toolbar(self):
        for btn in self.toolbar:
            if btn.is_hovered(): btn.color = (255,0,0)
            else: btn.color = (0,255,0)
            btn.draw(self)

    def get_map_folder(self):
        asset_folder = os.path.join(os.path.dirname(__file__), "assets")
        map_folder = os.path.join(asset_folder, "maps")
        abs_map_folder = os.path.abspath(map_folder)
        return abs_map_folder

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
            print("Map loaded")
            return board

    def save_map(self):
        print("saving map")
        import json
        tiles_data = [[0 for _ in range(16)] for _ in range(16)]
        for i in range(16):
            for j in range(16):
                tiles_data[i][j] = self.board[i][j].to_json_data()

        json_data = json.dumps({"author":"random", "board":tiles_data})
        file_path = os.path.join(self.map_folder, self.map_name)
        with open(file_path, 'w') as f:
            f.write(json_data)

        print("map saved")
    

parser = argparse.ArgumentParser(description="Map Creator")
parser.add_argument('--name', type=str,default="map",help='the name of the map')
args = parser.parse_args()

game = Game(800,850, args.name)
game.run()
