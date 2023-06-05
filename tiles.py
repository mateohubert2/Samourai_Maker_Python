from typing import Any
import pygame
from support import import_folder_lvl

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft = (x,y))
    
    def update(self,shift):
        self.rect.x += shift
        
class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface
        
class AnimateTile(Tile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y)
        self.frames = import_folder_lvl(path)
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        
    def animate(self):
        self.frames_index += 0.027 / 3
        if self.frames_index >= len(self.frames):
            self.frames_index = 0
        self.image = self.frames[int(self.frames_index)]
        
    def update(self, shift):
        self.animate()
        self.rect.x += shift

class Coin_lvl(AnimateTile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y, path)
        center_x = x + int(size/2)
        center_y = y + int(size/2)
        self.rect = self.image.get_rect(center = (center_x, center_y))
        
class Arbre(AnimateTile):
    def __init__(self, size, x, y, path, offset):
        super().__init__(size, x, y, path)
        offset_y = y - offset
        self.rect.topleft = (x, offset_y)