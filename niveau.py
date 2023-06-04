import pygame
from support import import_csv_layout
from parametres import TAILLE_CASES

class Niveau:
    def __init__(self,level_data,surface):
        self.display_surface = surface
        
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_niveau_sprites = self.create_tile_group(terrain_layout, 'terrain')
        
    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()
        
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * TAILLE_CASES
                    y = row_index * TAILLE_CASES

                    if type == 'terrain':
                        sprite = Tile(tile_size,x,y)
                        sprite_group.add(sprite)
                    
        return sprite_group
        
    
    def run(self):
        pass