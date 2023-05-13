import pygame
from pygame.math import Vector2 as vector
from parametres import*

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        
class Animated(Generic):
    def __init__(self, assets, pos, group):
        self.animation_frames = assets
        self.frame_index = 0
        super().__init__(pos, self.animation_frames[self.frame_index], group)
    
    def animate(self, dt):
        self.frame_index += VITESSE_ANIMATION * dt
        self.frame_index = 0 if self.frame_index >= len(self.animation_frames) else self.frame_index
        self.image = self.animation_frames[int(self.frame_index)]
    
    def update(self, dt):
        self.animate(dt)
            
class Particule(Animated):
    def __init__(self, assets, pos, group):
        super().__init__(assets, pos, group)            
        self.rect = self.image.get_rect(center = pos)
        
    def animate(self, dt):
        self.frame_index += VITESSE_ANIMATION * dt
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()
        
class Coin(Animated):
    def __init__(self, coin_type, assets, pos, group):
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center = pos)
        self.coin_type = coin_type 
        
class Ennemie2(Generic):
	def __init__(self, assets, pos, group):

		self.animation_frames = assets
		self.frame_index = 0
		self.orientation = 'right'
		surf = self.animation_frames[f'run_{self.orientation}'][self.frame_index]
		super().__init__(pos, surf, group)
        
class Player(Generic):
    def __init__(self, pos, group):
        super().__init__(pos, pygame.Surface((32,64)), group)
        self.image.fill('red')
        
        #mouvement
        self.direction = vector()
        self.pos = vector(self.rect.topleft)
        self.speed = 300
        
    def input(self):
        keys =  pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_q]:
            self.direction.x = -1
        else: self.direction.x = 0
        
    def move(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))    
    
    def update(self, dt):
        self.input()
        self.move(dt)