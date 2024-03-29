import pygame
from tiles import Tile, StaticTile, Coin_lvl, Arbre, AnimateTile
from support import import_csv_layout, import_cut_graphics
from parametres import TAILLE_CASES
from ennemie import Ennemie_lvl, Ennemie_lvl2
from parametres import LARGEUR_FENETRE, HAUTEUR_FENETRE
from timer import Timer
class Niveau:
    def __init__(self,level_data,surface):
        
        self.display_surface = surface
        self.world_shift = 0
        self.world_shift1 = 0

        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_niveau_sprites = self.create_tile_group(terrain_layout, 'terrain')
        
        coin_layout = import_csv_layout(level_data['piece'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'piece')
        
        arbre_fg_layout = import_csv_layout(level_data['arbre fg'])
        self.arbre_fg_sprites = self.create_tile_group(arbre_fg_layout, 'arbre fg')
        
        arbre_bg_layout = import_csv_layout(level_data['arbre bg'])
        self.arbre_bg_sprites = self.create_tile_group(arbre_bg_layout, 'arbre bg')
        
        ennemies_layout = import_csv_layout(level_data['ennemies'])
        self.ennemies_sprites = self.create_tile_group(ennemies_layout, 'ennemies')
        
        contrainte_layout = import_csv_layout(level_data['contrainte'])
        self.contrainte_sprites = self.create_tile_group(contrainte_layout, 'contrainte')
        
    def create_tile_group(self, layout, type):
        """_summary_
        la fonction create_tile_group permet de crée des groupes en regroupants les cases du meme type
        Args:
            layout (_type_): liste contenant les cases de meme types
            type (_type_): type de cases

        Returns:
            _type_: cette fonction return les differents groupes crées.
        """
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
                            
                    if type == 'ennemies':
                        if val == '0':
                            sprite = Ennemie_lvl2(TAILLE_CASES,x,y,'Graphique/Ennemie/Animation_Ennemie_2')
                        else:
                            sprite = Ennemie_lvl(TAILLE_CASES,x,y,'Graphique/Ennemie/Animation_Ennemie_1')
                    
                    if type == 'contrainte':
                        sprite = Tile(TAILLE_CASES,x,y)
                    
                    sprite_group.add(sprite)
                    
        return sprite_group
    
    
    def player_setup(self, layout):
        """_summary_
        la fonction player_setup permet de mettre en place le joueur au bon endroit et differencier le bloc debut et le bloc fin
        Args:
        """
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * TAILLE_CASES
                y = row_index * TAILLE_CASES 
                if val == '0':
                    sprite = AnimateTile(TAILLE_CASES,x,y,'Graphique/Personnage/Animation_Personnage/idle_right')
                    sprite.rect.topleft += pygame.Vector2(0,9)
                    self.player.add(sprite)
                if val == '1':
                    player_surface = pygame.image.load('Graphique/Levels/data/arriver.png').convert_alpha()
                    sprite = StaticTile(TAILLE_CASES,x,y,player_surface)
                    self.goal.add(sprite)
    def ennemie_collisions_reverse(self):
        """_summary_
        la fonction ennemie_collisions_reverse permet de faire faire demi tour au ennemies quand ils rentrent en collisions
        avec un bloc de types contraintes
        """
        for ennemie in self.ennemies_sprites.sprites():
            if pygame.sprite.spritecollide(ennemie, self.contrainte_sprites,False):
                ennemie.reverse()
    
    def player_mouvement(self):
        """_summary_
        la fonction player_mouvement permet de faire bouger le joeur de droite a gauche
        """
        keys =  pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.world_shift = 1
            self.orientation = 'right'
        elif keys[pygame.K_q]:
            self.world_shift = -1
            self.orientation = 'left'
        else: self.world_shift = 0
    def run(self):
        """_summary_
        la fonciton run tourne en boucle lorsqu'un niveau est lancé
        """
        self.event = pygame.event.get()
        
        self.arbre_bg_sprites.update(self.world_shift1)
        self.arbre_bg_sprites.draw(self.display_surface)
        
        self.terrain_niveau_sprites.update(self.world_shift1)
        self.terrain_niveau_sprites.draw(self.display_surface)
        
        self.ennemies_sprites.update(self.world_shift1)
        self.contrainte_sprites.update(self.world_shift1)
        self.ennemie_collisions_reverse()
        self.ennemies_sprites.draw(self.display_surface)
        
        self.coin_sprites.update(self.world_shift1)
        self.coin_sprites.draw(self.display_surface)
        
        self.arbre_fg_sprites.update(self.world_shift1)
        self.arbre_fg_sprites.draw(self.display_surface)
        
        self.goal.update(self.world_shift1)
        self.goal.draw(self.display_surface)
        
        self.player.update(self.world_shift)
        self.player.draw(self.display_surface)
        self.imagemenu = pygame.image.load('Graphique/game_over/menuditeur.png').convert_alpha()
        self.retour_menu = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 147, ((HAUTEUR_FENETRE/2)+293), 103, 27))
        self.display_surface.blit(self.imagemenu, (LARGEUR_FENETRE - 172,((HAUTEUR_FENETRE/2)+280)))
        self.player_mouvement()