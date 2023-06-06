import pygame
from tiles import Tile, StaticTile, Coin_lvl, Arbre
from support import import_csv_layout, import_cut_graphics
from parametres import TAILLE_CASES

class Niveau:
    def __init__(self,level_data,surface):
        self.display_surface = surface
        self.world_shift = -1
        
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_niveau_sprites = self.create_tile_group(terrain_layout, 'terrain')
        
        coin_layout = import_csv_layout(level_data['piece'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'piece')
        
        arbre_fg_layout = import_csv_layout(level_data['arbre fg'])
        self.arbre_fg_sprites = self.create_tile_group(arbre_fg_layout, 'arbre fg')
        
        arbre_bg_layout = import_csv_layout(level_data['arbre bg'])
        self.arbre_bg_sprites = self.create_tile_group(arbre_bg_layout, 'arbre bg')
        
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
                        
                        
                    if type == 'piece':
                        if val == '0':
                            sprite = Coin_lvl(TAILLE_CASES,x,y, 'Graphique/Levels/data/silver')
                        if val == '1':
                            sprite = Coin_lvl(TAILLE_CASES,x,y, 'Graphique/Levels/data/gold')
                        if val == '2':
                            sprite = Coin_lvl(TAILLE_CASES,x,y, 'Graphique/Levels/data/diamond')
                    
                    if type == 'arbre fg':
                        if val == '1':
                            sprite = Arbre(TAILLE_CASES,x,y,'Graphique/Arbre/Animation_Arbre2fg',61)
                        if val == '2':
                            sprite = Arbre(TAILLE_CASES,x,y,'Graphique/Arbre/Animation_Arbre1fg',61)
                        if val == '0':
                            sprite = Arbre(TAILLE_CASES,x,y,'Graphique/Arbre/Animation_Arbre3fg',61)
                    
                    if type == 'arbre bg':
                        if val == '3':
                            sprite = Arbre(TAILLE_CASES,x,y,'Graphique/Arbre/Animation_Arbre3bg',61)
                        if val == '4':
                            sprite = Arbre(TAILLE_CASES,x,y,'Graphique/Arbre/Animation_Arbre2bg',61)
                        if val == '5':
                            sprite = Arbre(TAILLE_CASES,x,y,'Graphique/Arbre/Animation_Arbre1bg',61)
                    
                    sprite_group.add(sprite)
                    
        return sprite_group
        
    
    def run(self):
        self.arbre_bg_sprites.update(self.world_shift)
        self.arbre_bg_sprites.draw(self.display_surface)
        
        self.terrain_niveau_sprites.update(self.world_shift)
        self.terrain_niveau_sprites.draw(self.display_surface)
        
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)
        
        self.arbre_fg_sprites.update(self.world_shift)
        self.arbre_fg_sprites.draw(self.display_surface)