import pygame
from tiles import Tile, StaticTile
from support import import_csv_layout, import_cut_graphics
from parametres import TAILLE_CASES

class Niveau:
    def __init__(self,level_data,surface):
        self.display_surface = surface
        self.world_shift = -1
        
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
                        terrain_tile_list = import_cut_graphics('Graphique/Levels/data/terrain.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(TAILLE_CASES,x,y, tile_surface)
                        sprite_group.add(sprite)
                    
        return sprite_group
        
    
    def run(self):
        self.terrain_niveau_sprites.draw(self.display_surface)
        self.terrain_niveau_sprites.update(self.world_shift)