import pygame
import InputField

pygame.font.init()

class MainMenu:
    def __init__(self, game):
        self.TITLE_FONT = pygame.font.SysFont("Fira Mono", 64)
        self.INFO_FONT = pygame.font.SysFont("Fira Mono", 24)

        r = pygame.Rect(350,400,150,30)
        self.ip_input_field = InputField.InputField(
                r.x,r.y,
                r.w,r.h,
                r, None)

        r = pygame.Rect(350,450,150,30)
        self.port_input_field = InputField.InputField(
                r.x,r.y,
                r.w,r.h,
                r, None)
        #TODO: Add a default text to input field
        self.port_input_field.text = '25565'
        self.game = game

    def port_to_int(self):
        try:
            return int(self.port_input_field.text)
        except:
            return 25565

    def update(self, events):
        self.ip_input_field.update(events)
        self.port_input_field.update(events)
        if self.ip_input_field.enter_pressed or self.port_input_field.enter_pressed:
            self.game.connect_to_server(self.ip_input_field.text, self.port_to_int())
            self.ip_input_field.reset()

    def draw(self):
        self.game.win.fill((34,17,119))

        #Render Title
        rendered_text = self.TITLE_FONT.render("Game Title", 1, (255,255,255))
        render_x = self.game.w / 2 - rendered_text.get_width() / 2
        render_y = 100
        self.game.win.blit(rendered_text, (render_x, render_y))

        #Render IP input field
        rendered_text = self.INFO_FONT.render("Server IP ", 1, (255,255,255))
        self.game.win.blit(rendered_text, (self.ip_input_field.x - rendered_text.get_width(), self.ip_input_field.y))
        self.ip_input_field.draw(self.game.win)

        #Render Port input field
        rendered_text = self.INFO_FONT.render("Server Port ", 1, (255,255,255))
        self.game.win.blit(rendered_text, (self.port_input_field.x - rendered_text.get_width(), self.port_input_field.y))
        self.port_input_field.draw(self.game.win)

        pygame.display.update()
