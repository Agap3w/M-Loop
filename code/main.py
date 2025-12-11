import pygame, sys
from settings import *
from level import Level

class Game:
    def __init__(self):

        pygame.init()

        #general setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('M-Loop')
        self.clock = pygame.time.Clock()
        
        self.level = Level()

    def run(self):
        while True:
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

            self.screen.fill('black')
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()