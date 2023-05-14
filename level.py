import pygame, sys
from pygame.math import Vector2 as vector

from parametres import*
from support import*

from sprites import Generic, Block, Animated, Particule, Coin, Player, Ennemie2, Ennemie

class Level:
    def __init__(self, grid, switch, asset_dict):
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
        
        #groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.ennemie_sprites = pygame.sprite.Group()
        
        self.build_level(grid, asset_dict)
        
        #chose additionnel
        self.particule_surfs = asset_dict['particle']
    
    def build_level(self, grid, asset_dict):
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
                        case 0: self.player = Player(pos, asset_dict['player'] ,self.all_sprites, self.collision_sprites)
                        case 4: Coin('gold', asset_dict['gold'], pos, [self.all_sprites, self.coin_sprites])
                        case 5: Coin('silver', asset_dict['silver'], pos, [self.all_sprites, self.coin_sprites])
                        case 6: Coin('diamond', asset_dict['diamond'], pos, [self.all_sprites, self.coin_sprites])
                        
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
                     
    def get_coins(self) :
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)      
        for sprite in collided_coins:
            Particule(self.particule_surfs, sprite.rect.center, self.all_sprites)
        
        
    def boucle_evenement(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()
                
    def lancement(self, dt):
        self.boucle_evenement()
        self.all_sprites.update(dt)
        self.get_coins()
        
        self.display_surface.fill(COULEUR_CIEL)
        self.all_sprites.custom_draw(self.player)
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - LARGEUR_FENETRE / 2
        self.offset.y = player.rect.centery - HAUTEUR_FENETRE / 2
        
        for sprite in self:
            for layer in LEVEL_LAYERS.values():
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)