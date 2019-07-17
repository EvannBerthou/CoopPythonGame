import pygame
from pygame.locals import *

pygame.init()

TITLE_FONT = pygame.font.SysFont("Fira mono", 18)
MESSAGE_FONT = pygame.font.SysFont("Fira mono", 14)
INPUT_FIELD_FONT = pygame.font.SysFont("Fira mono", 16)

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


class InputField:
    def __init__(self, x,y,w,h, real_rect, chat_box):
        self.x,self.y,self.w,self.h = x,y,w,h
        self.text = ''
        self.offset = 0
        self.cursor_pos = 0
        self.cursor_x = 4 #offset
        self.selected = False
        self.real_rect = real_rect
        self.chat_box = chat_box
        self.bg = pygame.Surface((self.w, self.h))

    def draw(self, background):
        self.bg.fill((170,170,170))
        text = INPUT_FIELD_FONT.render(self.text, 1, (255,255,255)) #RENDER TEXT
        self.bg.blit(text, (-self.offset, self.h / 4)) #TEXT

        if self.selected:
            pygame.draw.rect(self.bg, (0,0,0), (self.cursor_x - self.offset - 4, 4, 1, self.h - 8)) #CURSOR
        background.blit(self.bg, (self.x, self.y))

    def is_hovered(self, mouse_position):
        return (self.real_rect.x + self.w > mouse_position[0] > self.real_rect.x
                and self.real_rect.y + self.h > mouse_position[1] > self.real_rect.y)

    def is_clicked(self, mouse_position, mouse_clicks):
        return self.is_hovered(mouse_position) and mouse_clicks[0]

    def send_message(self):
        if self.text.strip(' ') != '':
            self.chat_box.send_message_to_server(self.text)
            self.text = ''
            self.offset = 0
            self.cursor_pos = 0
            self.cursor_x = 4

    def delete_word_backspace(self):
        for i in range(self.cursor_pos, 0, -1):
            if self.text[i - 1] != ' ':
                self.remove_letter()
            else:
                self.remove_letter() #DELETE SPACE
                return

    def delete_word_delete(self):
        #if the next char is a space, move the cursor to avoid only removing the space
        if self.text[self.cursor_pos] == ' ': self.cursor_pos += 1
        self.move_word(1)
        self.delete_word_backspace()


    def remove_letter(self):
        letter = self.text[self.cursor_pos - 1] if self.cursor_pos < len(self.text) else ""
        self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]

        if INPUT_FIELD_FONT.size(self.text)[0] > self.w - 8:
            self.offset -= INPUT_FIELD_FONT.size(letter)[0]

        self.cursor_pos -= 1
        if self.cursor_pos < 0: self.cursor_pos = 0

        self.cursor_x = INPUT_FIELD_FONT.size(self.text[:self.cursor_pos])[0] + 4

    def add_letter(self, unicode):
        self.text = self.text[:self.cursor_pos] + unicode + self.text[self.cursor_pos:]
        self.cursor_pos += len(unicode)
        self.cursor_x = INPUT_FIELD_FONT.size(self.text[:self.cursor_pos])[0] + 4
        if INPUT_FIELD_FONT.size(self.text)[0] >= self.w:
            self.offset += INPUT_FIELD_FONT.size(unicode)[0]

    def move_cursor(self, direction):
        if self.cursor_pos >= 0 and self.cursor_pos <= len(self.text):
            self.cursor_pos = max(self.cursor_pos + direction, 0)
            self.cursor_pos = min(self.cursor_pos, len(self.text))
            self.cursor_x = INPUT_FIELD_FONT.size(self.text[:self.cursor_pos])[0] + 4

    def loop_until_space(self, start, end, step):
        for i in range(start, end, step):
            if self.text[i] == ' ':
                return i
        return None

    def move_word(self, direction):
        cursor_pos = None
        if direction == -1:
            i = self.loop_until_space(self.cursor_pos - 1, 0, -1)
            if i: cursor_pos = i
        if direction == 1:
            i = self.loop_until_space(self.cursor_pos, len(self.text), 1)
            if i: cursor_pos = i + 1

        if cursor_pos:
            self.cursor_pos = cursor_pos
        else:
            if direction == 1: self.cursor_pos = len(self.text)
            else: self.cursor_pos = 0

        self.cursor_x = INPUT_FIELD_FONT.size(self.text[:self.cursor_pos])[0] + 4

    def ctrl_control(self, event):
        if event.key == K_RIGHT: self.move_word(1)
        elif event.key == K_LEFT:  self.move_word(-1)
        elif event.key == K_BACKSPACE: self.delete_word_backspace()
        elif event.key == K_DELETE: self.delete_word_delete()

    def update(self, events):
        if not self.selected: return
        mods = pygame.key.get_mods()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_RETURN: self.send_message()
                elif mods & KMOD_LCTRL: self.ctrl_control(event)
                elif event.key == K_BACKSPACE: self.remove_letter()
                elif event.key == K_ESCAPE:
                    self.selected = False
                    self.chat_box.toggle()
                elif event.key == K_RIGHT: self.move_cursor(1)
                elif event.key == K_LEFT: self.move_cursor(-1)
                elif event.key == K_DELETE:
                    self.cursor_pos += 1
                    self.remove_letter()
                else: self.add_letter(event.unicode)
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


    #TODO: Send command to server through chat
    def send_message_to_server(self, message):
        msg = "{}: {}".format(self.name, message)
        self.game_socket.send_message("chat_message {}".format(msg))
        self.add_message(msg)

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
        for event in events:
            if event.type == KEYDOWN:
                keyboard_state = pygame.key.get_pressed()
                if keyboard_state[K_t] and not self.input_field.selected:
                    self.toggle()

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
