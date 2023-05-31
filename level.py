import pygame, sys
from pygame.math import Vector2 as vector

from parametres import*
from support import*
from random import choice
from random import randint
from main import Main


from sprites import Generic, Block, Animated, Particule, Coin, Player, Ennemie2, Ennemie, Cloud

class Level:
    def __init__(self, grid, switch, asset_dict, audio):
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
        self.ath = ATH(self.display_surface)
        #groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.ennemie_sprites = pygame.sprite.Group()
        
        self.build_level(grid, asset_dict, audio['jump'])
        
        #limite du lvl
        self.level_limits = {
            'left': -LARGEUR_FENETRE,
            'right': sorted(list(grid['terrain'].keys()), key = lambda pos: pos[0])[-1][0] + 500
        }

        #ATH
        self.piece = 0
        
        #chose additionnel
        self.particule_surfs = asset_dict['particle']
        self.cloud_timer = pygame.USEREVENT + 2
        self.cloud_surfs = asset_dict['clouds']
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.startup_clouds()
        
        #musique
        self.bg_music = audio['music']
        self.bg_music.set_volume(0.4)
        self.bg_music.play(loops = -1)
        
        self.coin_sound = audio['coin']
        self.coin_sound.set_volume(0.3)
        
        self.hit_sound = audio['hit']
        self.hit_sound.set_volume(0.3)
    
    def differencier_piece(self, grid):
        if grid.items()['gold']:
            valeur = 5
            self.update_piece(valeur)
            self.ath.nombre_piece(self.piece)
    
    def build_level(self, grid, asset_dict, jump_sound):
        
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
                        case 0: self.player = Player(pos, asset_dict['player'] ,self.all_sprites, self.collision_sprites, jump_sound, self.display_surface)
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
        self.piece += nombre      

    def get_coins(self) :
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

    
    def get_damage(self):
        collision_sprites = pygame.sprite.spritecollide(self.player, self.damage_sprites, False, pygame.sprite.collide_mask)
        if collision_sprites:
            self.hit_sound.play()
            self.player.damage()
        
    def boucle_evenement(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()
                self.bg_music.stop()
            if event.type == self.cloud_timer:
                surf = choice(self.cloud_surfs)
                surf = pygame.transform.scale2x(surf) if randint(0,5) > 3 else surf
                x = self.level_limits['right'] + randint(100, 300)
                y = self.horizon_y - randint(-50, 600)
                Cloud((x,y), surf, self.all_sprites, self.level_limits['left'])
            
    def startup_clouds(self):
        for i in range(40):
            surf = choice(self.cloud_surfs)
            surf = pygame.transform.scale2x(surf) if randint(0,5) > 3 else surf
            x = randint(self.level_limits['left'],self.level_limits['right'])
            y = self.horizon_y - randint(-50, 600)
            Cloud((x,y), surf, self.all_sprites, self.level_limits['left'])
                
    def lancement(self, dt):
        self.boucle_evenement()
        self.all_sprites.update(dt)
        self.get_coins()
        self.get_damage()
        self.display_surface.fill(COULEUR_CIEL)
        self.all_sprites.custom_draw(self.player)
        self.ath.nombre_piece(self.piece)
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
      
    def draw_horizon(self):
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