import pygame
from tiles import AnimateTile
from random import randint


class Ennemie_lvl(AnimateTile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y, 'Graphique/Ennemie/Animation_Ennemie_2/run_left')
        self.speed = 1
        
    
    def reverse_image(self):
        if self.speed >= 0:
            self.image = pygame.transform.flip(self.image,True,False)
    
    def reverse(self):
        self.speed *= -1
    
    def move(self):
        self.rect.x += self.speed
        
    def update(self, shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()

class Ennemie_lvl2(AnimateTile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y, 'Graphique/Ennemie/Animation_Ennemie_1')