import pygame, sys
from pygame.math import Vector2 as vector
from ATH import ATH
from parametres import*
from support import*
from random import choice
from random import randint
from timer import Timer
from niveau import *
from editeur import *
from support import *
from pygame.mouse import get_pos as position_souris
from sprites import Generic, Block, Animated, Particule, Coin, Player, Ennemie2, Ennemie, Cloud

class Level:
    def __init__(self, grid, switch, asset_dict, audio):
        """_summary_
        constructeur de la classe Level
        """
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
        self.ath = ATH(self.display_surface)
        self.origin = vector(0,0)
        #groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.ennemie_sprites = pygame.sprite.Group()
        self.explosion_sprites = pygame.sprite.Group()
        self.build_level(grid, asset_dict, audio['jump'])
        self.enemy_timer = Timer(1000)
        self.animation_timer = Timer(500)
        self.offset = self.player.pos
        offset_x = 0
        offset_y = 0
        self.offset_rect = 0
        #limite du lvl
        self.level_limits = {
            'left': -LARGEUR_FENETRE,
            'right': sorted(list(grid['terrain'].keys()), key = lambda pos: pos[0])[-1][0] + 500
        }

        #ATH
        self.piece = 0
        #definition de la partie qui gere la vie et le nombre de piece
        self.vie_max = 100
        self.vie_actuelle_level = 100
        #chose additionnel
        self.particule_surfs = asset_dict['particle']
        self.cloud_timer = pygame.USEREVENT + 2
        self.cloud_surfs = asset_dict['clouds']
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.startup_clouds()
        #musique
        self.bg_music = audio['music']
        self.bg_music.set_volume(0.5)
        self.bg_music.play(loops = -1)
        self.Game_Over_music = audio['Game_Over']
        self.Game_Over_music.set_volume(0.4)
        self.coin_sound = audio['coin']
        self.coin_sound.set_volume(0.3)
        
        self.hit_sound = audio['hit']
        self.hit_sound.set_volume(0.1)
    
    def build_level(self, grid, asset_dict, jump_sound):
        """_summary_
        Importation des images qu'on peut placer dans l'éditeur
        """
        
        for layer_name, couche in grid.items():
            for pos, data in couche.items():
                if layer_name == 'terrain':
                    Generic(pos, asset_dict['land'][data], [self.all_sprites, self.collision_sprites])
                if layer_name == 'eau':
                    if data == 'top':
                        Animated(asset_dict['water top'], pos, self.all_sprites, LEVEL_LAYERS['water'])
                    else:
                        Generic(pos, asset_dict['water bottom'], self.all_sprites, LEVEL_LAYERS['water'])
                    
                match data:
                    case 0: self.player = Player(pos, asset_dict['player'] ,self.all_sprites, self.collision_sprites, jump_sound, self.display_surface,self.prise_degat)
                    case 1:
                        self.horizon_y = pos[1]
                        self.all_sprites.horizon_y = pos[1]
                        
                    case 4: Coin('gold', asset_dict['gold'], pos, [self.all_sprites, self.coin_sprites],5)
                    case 5: Coin('silver', asset_dict['silver'], pos, [self.all_sprites, self.coin_sprites],1)
                    case 6: Coin('diamond', asset_dict['diamond'], pos, [self.all_sprites, self.coin_sprites],10)
                        
                    case 7:
                        Ennemie(orientation = 'left', 
                                assets = asset_dict['ennemie'], 
                                pos = pos, 
                                group = [self.all_sprites, self.collision_sprites, self.ennemie_sprites],
                                pearl_surf = asset_dict['pearl'],
                                damage_sprites = self.damage_sprites)
                            
                            
                    case 8:
                        Ennemie2(asset_dict['ennemie2'], pos, [self.all_sprites, self.damage_sprites], self.collision_sprites)
                        
                        
                        
                    case 9:
                        Animated(asset_dict['arbre']['Animation_Arbre1fg'], pos, self.all_sprites)
                        Block(pos + vector(25,11), (85, 45), self.collision_sprites)
                    case 10:
                        Animated(asset_dict['arbre']['Animation_Arbre2fg'], pos, self.all_sprites)
                        Block(pos + vector(15,10), (95, 40), self.collision_sprites)
                    case 11:
                        Animated(asset_dict['arbre']['Animation_Arbre3fg'], pos, self.all_sprites)
                        Block(pos + vector(15,25), (100, 60), self.collision_sprites)
                        
                    case 12: Animated(asset_dict['arbre']['Animation_Arbre1bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 13: Animated(asset_dict['arbre']['Animation_Arbre2bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 14: Animated(asset_dict['arbre']['Animation_Arbre3bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
        for sprite in self.ennemie_sprites:
            sprite.player = self.player

    def update_piece(self,nombre):
        """_summary_
        Change la valeur de la variable piece quand on recupère une piecesur le jeu.
        """
        self.piece += nombre      

    def prise_degat(self, nombre):
        """_summary_
        Change la valeur de la vie quand on se fait attaquer par un enemie.
        """
        self.vie_actuelle_level += nombre 

    def get_coins(self) :
        """_summary_
        Permet de gerer les collisions avec les pièces, jouer un son de récuperation et palce une valeur sur chaque type de pièce.
        """
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)    
        if collided_coins:  
            for sprite in collided_coins:
                self.coin_sound.play()
                Particule(self.particule_surfs, sprite.rect.center, self.all_sprites)
                if  sprite.coin_type == 'gold':
                    valeur = 5
                    self.update_piece(valeur)
                if  sprite.coin_type == 'silver':
                    valeur = 1
                    self.update_piece(valeur)
                if  sprite.coin_type == 'diamond':
                    valeur = 10
                    self.update_piece(valeur)

    def check_enemy_collision(self):
        """_summary_
        permet de tuer un enemie en sautant dessu + rebondir dessus
        """
        enemy_collision = pygame.sprite.spritecollide(self.player,self.damage_sprites, False)
        if enemy_collision:
            for ennemie in enemy_collision:
                enemy_centre = ennemie.rect.centery
                enemy_top = ennemie.rect.top
                player_bottom = self.player.rect.bottom
                if enemy_top<player_bottom<enemy_centre and self.player.direction.y>0:
                    #effet de knockback quand on tue un enemie ou une perle
                    self.player.direction.y = -2
                    self.animation_timer.activate()
                    ennemie.kill()    
    
    def get_damage(self):
        """_summary_
        Gestion des collisions avec les enemies + son de dégat + appel de la fonction qui nous rend invincible.
        """
        collision_sprites = pygame.sprite.spritecollide(self.player, self.damage_sprites, False, pygame.sprite.collide_mask)
        if collision_sprites:
            self.hit_sound.play()
            self.player.damage()

    def boucle_evenement(self):
        """_summary_
        Gestion de l'arrêt du mode "jeu" de l'éditeur en appyant sur "echap".
        Placement aléatoire des nuages dans le fond du jeu.
        Gestion de l'altitude min qui renvoie à un game over si elle est dépacée. 
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #Quitter le mode jeu de l'éditeur
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()
                self.bg_music.stop()
            #Placement nuages aléatoires
            if event.type == self.cloud_timer:
                surf = choice(self.cloud_surfs)
                surf = pygame.transform.scale2x(surf) if randint(0,5) > 3 else surf
                x = self.level_limits['right'] + randint(100, 300)
                y = self.horizon_y - randint(-50, 600)
                Cloud((x,y), surf, self.all_sprites, self.level_limits['left'])
            #Altitude minimale
            if self.player.pos.y > 1300:
                self.vie_actuelle_level = 0
            
    def startup_clouds(self):
        """_summary_
        Lancement INSTANTANEE des nuages dans le fond du jeu pour ne pas que le fond soit vide au lancement.
        """
        for i in range(40):
            surf = choice(self.cloud_surfs)
            surf = pygame.transform.scale2x(surf) if randint(0,5) > 3 else surf
            x = randint(self.level_limits['left'],self.level_limits['right'])
            y = self.horizon_y - randint(-50, 600)
            Cloud((x,y), surf, self.all_sprites, self.level_limits['left'])
            
          
    def lancement(self, dt):
        """_summary_
        Permet d'appeler toutes les fonctions nécessaires au lancement d'un niveau lancé dans l'éditeur.
        """
        #partie ou on regarde les collisions
        self.boucle_evenement()
        self.all_sprites.update(dt)
        self.get_coins()
        self.check_enemy_collision()
        self.get_damage()
        #partie ou on dessine l'ath
        self.display_surface.fill(COULEUR_CIEL)
        self.all_sprites.custom_draw(self.player)
        self.ath.barre_de_vie(self.vie_actuelle_level,self.vie_max)
        self.ath.nombre_piece(self.piece)
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        """_summary_
        Constructeur
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
      
    def draw_horizon(self):
        """_summary_
        Possibilité de changer la hauteur du ciel dans l'éditeur.
        """
        horizon_pos = self.horizon_y - self.offset.y
           
        if horizon_pos < HAUTEUR_FENETRE:
            sea_rect = pygame.Rect(0, horizon_pos, LARGEUR_FENETRE, HAUTEUR_FENETRE - horizon_pos)
            pygame.draw.rect(self.display_surface, COULEUR_MER, sea_rect)
            horizon_rect1 = pygame.Rect(0,horizon_pos - 10,LARGEUR_FENETRE,10)
            horizon_rect2 = pygame.Rect(0,horizon_pos - 16,LARGEUR_FENETRE,4)
            horizon_rect3 = pygame.Rect(0,horizon_pos - 20,LARGEUR_FENETRE,2)
            pygame.draw.rect(self.display_surface, COULEUR_DESSUS_HORIZON, horizon_rect1)
            pygame.draw.rect(self.display_surface, COULEUR_DESSUS_HORIZON, horizon_rect2)
            pygame.draw.rect(self.display_surface, COULEUR_DESSUS_HORIZON, horizon_rect3)
            pygame.draw.line(self.display_surface, COULEUR_HORIZON, (0,horizon_pos), (LARGEUR_FENETRE,horizon_pos), 3)
            
        if horizon_pos < 0:
            self.display_surface.fill(COULEUR_MER)

            
        
    def custom_draw(self, player):
        """_summary_
        Dessine le monde de jeu sur un claque, on dessinera les autres choses qu'on veut afficher par dessus ce calque.
        """
        self.offset.x = player.rect.centerx - LARGEUR_FENETRE / 2
        self.offset.y = player.rect.centery - HAUTEUR_FENETRE / 2
        
        for sprite in self:
            if sprite.z == LEVEL_LAYERS['clouds']:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)
            
            
        self.draw_horizon()
        for sprite in self:
            for layer in LEVEL_LAYERS.values():
                if sprite.z == layer and sprite.z != LEVEL_LAYERS['clouds']:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
    