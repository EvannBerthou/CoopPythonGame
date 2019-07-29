import pygame
from pygame.locals import *

pygame.init()

INPUT_FIELD_FONT = pygame.font.SysFont("Fira mono", 16)

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
        self.enter_pressed = False

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
        self.enter_pressed = False
        mods = pygame.key.get_mods()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_RETURN: self.enter_pressed = True
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

    def reset(self):
        self.text = ''
        self.offset = 0
        self.cursor_pos = 0
        self.cursor_x = 4
