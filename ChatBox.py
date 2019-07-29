from InputField import InputField

import pygame
from pygame.locals import *

pygame.init()

TITLE_FONT = pygame.font.SysFont("Fira mono", 18)
MESSAGE_FONT = pygame.font.SysFont("Fira mono", 14)

class HistoryBox:
    def __init__(self, x,y,w,h):
        self.x,self.y,self.w,self.h = x,y,w,h

    def draw_messages(self, background, messages):
        last_y = self.y + 2
        for msg in messages:
            background.blit(msg, (self.x + 4, last_y))
            last_y += msg.get_height()

    def draw(self, background):
        pygame.draw.rect(background, (170,170,170), (self.x,self.y,self.w, self.h))

class ChatBox:
    def __init__(self, x,y,w,h, game_socket):
        self.x,self.y,self.w,self.h = x,y,w,h
        self.enabled = False
        self.background = self.create_background()
        self.title = TITLE_FONT.render("Game chat", 1, (255,255,255))

        input_height = 28
        title_height = self.title.get_height()

        input_field_real_rect = pygame.Rect(self.x + 4, self.y + self.h - title_height - 9, self.w - 8, input_height)
        self.input_field = InputField(4, self.h - title_height - 9, self.w - 8, input_height, input_field_real_rect, self)
        self.history_box = HistoryBox(4, title_height + 2, self.w - 8,self.h - title_height - input_height - 8)

        self.messages = []

        self.in_animation = False
        self.animation_timer = 0
        self.animation_duration = 500
        self.start_y = self.y
        self.end_y = 540
        self.animated_y = self.y
        self.animation_speed = (self.start_y - self.end_y) / self.animation_duration

        self.game_socket = game_socket

        import random
        self.name = random.randint(0,1000)

    def split_message(self, message):
        index = 0
        text = [""]

        parts = message.split(' ')

        for i,part in enumerate(parts):
            tmp = text[index] + part + " "

            if INPUT_FIELD_FONT.size(tmp)[0] > self.history_box.w + 64:
                index += 1
                text.append(" " + part)
            else:
                text[index] = tmp

        return text

    def add_message(self, message):
        msg_width = MESSAGE_FONT.size(message)[0]

        msg = [message]
        if msg_width >= self.history_box.w:
            msg = self.split_message(message)

        for line in msg:
            if line.strip(' ') == '': continue #avoid empty lines
            rendered = MESSAGE_FONT.render(line, 1, (255,255,255))
            self.messages.append(rendered)
            if self.all_messages_height() > self.history_box.h:
                #SHOULD NOT DELETE, SHOULD BE KEPT TO ALLOW SCROLLING IN HISTORY
                del self.messages[0]


    def send_message_to_server(self, message):
        msg = "{}: {}".format(self.name, message)
        self.game_socket.send_message("chat_message {}".format(msg))

    def create_background(self):
        surface = pygame.Surface((self.w,self.h))
        surface.fill((150,150,150))
        return surface

    def toggle(self):
        if not self.in_animation:
            self.enabled = not self.enabled
            self.in_animation = True
            self.animation_timer = 0

    def animate(self,dt):
        self.animation_timer += dt
        if self.animation_duration > self.animation_timer:
            self.animated_y += self.animation_speed * (-1 if self.enabled else 1) * dt
            self.y = self.animated_y
        else:
            self.y = self.end_y if self.enabled else self.start_y
            self.in_animation = False

            if self.enabled:
                self.input_field.selected = True

    def update(self,events):
        self.input_field.update(events)
        for event in events:
            if event.type == KEYDOWN:
                keyboard_state = pygame.key.get_pressed()
                if keyboard_state[K_t] and not self.input_field.selected:
                    self.toggle()
                if self.input_field.selected and self.input_field.enter_pressed:
                    self.send_message()

    def send_message(self):
        if self.input_field.text.strip(' ') != '':
            self.send_message_to_server(self.input_field.text)
            self.input_field.reset()

    def draw(self, game):
        self.background.fill((150,150,150))

        #DRAWS TITLE CENTERED IN THE BOX
        self.background.blit(self.title, (self.w / 2 - self.title.get_width() / 2, 0))

        #DRAW HISTORY BOX
        self.history_box.draw(self.background)
        self.history_box.draw_messages(self.background, self.messages)

        #DRAW INPUT FIELD
        self.input_field.draw(self.background)

        #DRAWS BACKGROUND
        game.win.blit(self.background, (self.x, self.y))

    def all_messages_height(self):
        return sum([msg.get_height() for msg in self.messages])

"""
TODO:
    Add mouse scroll in history box
    Add pseudo for each player
    Add notification on message recieved when the chat box is not opened
"""
