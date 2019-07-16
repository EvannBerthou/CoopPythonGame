import Client
import Map
import Player
import Tiles
import ChatBox

import pygame
import argparse
from pygame.locals import *

class Game:
    def __init__(self,w,h, args):
        self.w,self.h = w,h
        self.win = pygame.display.set_mode((self.w,self.h))
        self.game_socket = Client.GameSocket(args.ip, args.port)

        self.map = Map.Map(self)
        self.network_manager = Client.NetworkManger(self)

        self.chat_box = ChatBox.ChatBox(10, 800, 400, 250, self.game_socket)

        self.team = None
        self.player = None
        self.coop_player = None

        self.clock = pygame.time.Clock()
        self.tick = 0.0

    def run(self):
        running = True
        while running:
            dt = self.clock.tick()
            self.tick += dt
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.map.map_data and not self.chat_box.enabled:
                        self.player.on_key_pressed()

            self.chat_box.update(events)
            self.chat_box.input_field.update(events)
            self.network_manager.update_network()
            self.update(dt)
            self.draw()
        self.close()

    def update(self,dt):
        if self.tick >= 500:
            if self.map.is_playing:
                self.player.update()
            self.tick = 0
        if self.chat_box.in_animation:
            self.chat_box.animate(dt)

    def draw(self):
        self.win.fill((0,0,0))
        self.map.draw(self)
        if self.map.is_playing: #IF A MAP IS LOADED
            self.player.draw()
            self.coop_player.draw()
            self.chat_box.draw(self)

        pygame.display.update()

    def close(self):
        self.game_socket.Listener.running = False
        pygame.quit()
        quit(0)

parser = argparse.ArgumentParser(description="Server")
parser.add_argument('--port', type=int,default=25565,help='the port you want to use for the server')
parser.add_argument('--ip',   type=str,default="127.0.0.1",help='the port you want to use for the server')
args = parser.parse_args()

game = Game(800,800, args)
game.run()
