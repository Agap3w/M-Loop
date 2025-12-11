import pygame, sys
from settings import *
from level import Level
from time_manager import TimeManager


class Game:
    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('M-Loop')
        self.clock = pygame.time.Clock()
        self.time_manager = TimeManager(time_speed=TIME_SPEED, start_time=START_TIME, end_time=END_TIME)
        self.timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)
        self.level = Level(self.time_manager)

    def run(self):
        while True:
            delta_time = self.clock.get_time() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Gestione input per dialoghi
                if event.type == pygame.KEYDOWN:
                    # Se c'è un dialogo attivo, passa l'input al dialogue manager
                    if self.level.dialogue_manager.active:
                        self.level.dialogue_manager.handle_input(event)
                    # Altrimenti gestisci interazioni con NPC
                    elif event.key == pygame.K_e:
                        self.level.handle_interaction()

            self.time_manager.update(delta_time)
            self.screen.fill('black')
            self.level.run()
            self.time_manager.draw(self.screen, self.timer_font)
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()