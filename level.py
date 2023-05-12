import pygame, sys
from pygame.math import Vector2 as vector

from parametres import*
from support import*


class Level:
    def __init__(self, grid, switch):
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
    def boucle_evenement(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()
    def lancement(self, dt):
        self.boucle_evenement()
        self.display_surface.fill('red')