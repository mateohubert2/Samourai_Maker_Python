from typing import Any
import pygame
from pygame.math import Vector2 as vector
from pygame.sprite import Group
from parametres import*
from parametres import LEVEL_LAYERS
from timer import Timer
from random import randint
from random import choice
from support import import_folder
from level import *


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group, z = LEVEL_LAYERS['main']):
        """_summary_
        Constructeur des entitées qui ne se déplacent pas.
        """
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        
class Block(Generic):
    def __init__(self, pos, size, group):
        """_summary_
        Constructeur des blocs de l'éditeur.
        """
        surf = pygame.Surface(size)
        super().__init__(pos, surf, group)
        
class Cloud(Generic):
    def __init__(self, pos, surf, group, left_limit):
        """_summary_
        Constructeur
        """
        super().__init__(pos, surf, group, LEVEL_LAYERS[('clouds')])
        self.left_limit = left_limit      
                
        self.pos = vector(self.rect.topleft)
        self.speed = randint(20,30)
        
    def update(self, dt):
        """_summary_
        Gestion des déplacement des nuages et les supprimes lorsqu'ils quittent l'ecran.
        """
        self.pos.x -= self.speed * dt
        self.rect.x = round(self.pos.x)
        if self.rect.x <= self.left_limit:
            self.kill()
        
class Animated(Generic):
    def __init__(self, assets, pos, group, z = LEVEL_LAYERS['main']):
        """_summary_
        Constructeur des animations des entitées qui ne se déplacent pas.
        """
        self.animation_frames = assets
        self.frame_index = 0
        super().__init__(pos, self.animation_frames[self.frame_index], group, z)
    
    def animate(self, dt):
        """_summary_
        Gestion de l'animation en faisant boucler des images à une certaines vitesse définie dans le fichier parametres.
        """
        self.frame_index += (VITESSE_ANIMATION * dt) / 2
        self.frame_index = 0 if self.frame_index >= len(self.animation_frames) else self.frame_index
        self.image = self.animation_frames[int(self.frame_index)]
    
    def update(self, dt):
        """_summary_
        Met à jour les images qui défilent lors de l'animation.
        """
        self.animate(dt)
            
class Particule(Animated):
    def __init__(self, assets, pos, group):
        """_summary_
        Constructeur des particules quand on recupère une pièce.
        """
        super().__init__(assets, pos, group)            
        self.rect = self.image.get_rect(center = pos)
        
    def animate(self, dt):
        """_summary_
        Les particules fonctionnent comme l'animation d'un objet statique, on fait défiler des images à une certaine vitesse.
        Quand toute les images sont passées une fois, on arrête le défilement des images.
        """
        self.frame_index += VITESSE_ANIMATION * dt
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()
        
class Coin(Animated):
    def __init__(self, coin_type, assets, pos, group,valeur):
        """_summary_
        Constructeur d'une pièce statique animée.
        """
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center = pos)
        self.coin_type = coin_type 
        self.valeur = valeur
class Ennemie2(Generic):
    def __init__(self, assets, pos, group, collision_sprites):
        """_summary_
        Constructeur de l'enemie qui se déplace sur les platformes.
        """
        self.animation_frames = assets
        self.frame_index = 0
        self.orientation = 'right'
        surf = self.animation_frames[f'run_{self.orientation}'][self.frame_index]
        super().__init__(pos, surf, group)
        self.rect.bottom = self.rect.top + TAILLE_CASES
        self.mask = pygame.mask.from_surface(self.image)
        
        self.direction = vector(choice((1,-1)),0)
        self.orientation = 'left' if self.direction.x < 0 else 'right'
        self.pos = vector(self.rect.topleft)
        self.speed = 120
        self.collision_sprites = collision_sprites
        
        #detruire l'ennemie si il n'est pas au sol
        if not [sprite for sprite in collision_sprites if sprite.rect.collidepoint(self.rect.midbottom + vector(0,10))]:
            self.kill()
            
    def animate(self, dt):
        """_summary_
        Animation de l'enemie quand il se déplace.
        """
        current_animation = self.animation_frames[f'run_{self.orientation}']
        self.frame_index += VITESSE_ANIMATION * dt
        self.frame_index = 0 if self.frame_index >= len(current_animation) else self.frame_index
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)
        
    def move(self, dt):
        """_summary_
        Gestion du déplacement sur la platfome jusqu'aux extremitées de celle-ci.
        """
        right_gap = self.rect.bottomright + vector(1,1)
        right_block = self.rect.midright + vector(1,0)
        left_gap = self.rect.bottomleft + vector(-1,1)
        left_block = self.rect.midleft + vector(-1,0)
        
        if self.direction.x > 0:
            floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_gap)]
            wall_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_block)]
            
            if wall_sprites or not floor_sprites:
                self.direction *= -1
                self.orientation = 'left'
            
        if self.direction.x < 0:
            if not[sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(left_gap)] or [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(left_block)]:
                self.direction *= -1
                self.orientation = 'right'
            
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
    
    def update(self, dt):
        """_summary_
        Mise à jour de l'image de l'animation.
        """
        self.animate(dt)
        self.move(dt)
        
class Ennemie(Generic):
    def __init__(self, orientation, assets, pos, group, pearl_surf, damage_sprites):
        """_summary_
        Constructeur d'un enemie statique qui tire des perles.
        """
        self.orientation = orientation
        self.animation_frames = assets.copy()
        if orientation == 'right':
            for key, value in self.animation_frames.items():
                self.animation_frames[key] = [pygame.transform.flip(surf, True, False) for surf in value]
                
        self.frame_index = 0
        self.status = 'idle'
        super().__init__(pos, self.animation_frames[self.status][self.frame_index], group)
        self.rect.bottom = self.rect.top + TAILLE_CASES
        
        self.pearl_surf = pearl_surf
        self.has_shot = False
        self.attack_cooldown = Timer(2000)
        self.damage_sprites = damage_sprites
    
    def animate(self, dt):
        """_summary_
        Gestion de l'animation.
        """
        current_animation = self.animation_frames[self.status]
        self.frame_index += VITESSE_ANIMATION * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.has_shot:
                self.attack_cooldown.activate()
                self.has_shot = False
        self.image = current_animation[int(self.frame_index)]
        
        if int(self.frame_index) == 3 and self.status == 'attack' and not self.has_shot:
            pearl_direction = vector(-1,0) if self.orientation == 'left' else vector(1,0)
            offset = (pearl_direction * 20) + vector(0, -5) if self.orientation == 'left' else (pearl_direction * 20)
            Pearl(self.rect.center + offset, pearl_direction, self.pearl_surf, [self.groups()[0], self.damage_sprites])
            self.has_shot = True
    def get_status(self):
        """_summary_
        Permet de savoir si l'enemie tire une perle ou non (permet d'eviter d'en tirer plusieurs en même temps).
        """
        if vector(self.player.rect.center).distance_to(vector(self.rect.center)) < 500 and not self.attack_cooldown.active:
            self.status = 'attack'
        else:
            self.status = 'idle'
    
    def update(self, dt):
        """_summary_
        Met à jour les images de l'animiation.
        Lance un cooldown à chaque fois que l'enemie attaque pour eviter de tirer plusieurs perles en même temps.
        """
        self.get_status()
        self.animate(dt)
        self.attack_cooldown.uptade()
        
class Pearl(Generic):
    def __init__(self, pos, direction, surf, group):
        """_summary_
        Constructeur de la perle tiré par l'enemie.
        """
        super().__init__(pos, surf, group)       
        self.mask = pygame.mask.from_surface(self.image)
        
        self.pos = vector(self.rect.topleft)
        self.direction = direction
        self.speed = 400
        
        self.timer = Timer(6000)
        self.timer.activate()


    def update(self, dt):
        """_summary_
        Met à jour la postion de la perle.
        """
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        
        self.timer.uptade()
        if not self.timer.active:
            self.kill()
    
class Player(Generic):
    def __init__(self, pos, assets, group, collision_sprites, jump_sound, surface,prise_degat):
        """_summary_
        Construteur de l'entitée joueur.
        """
        self.animation_frames = assets
        self.frame_index = 0
        #nouvellefonction
        self.display_surface = surface
        self.status = 'idle'
        self.orientation = 'right'
        surf = self.animation_frames[f'{self.status}_{self.orientation}'][self.frame_index]
        super().__init__(pos, surf, group)
        self.mask = pygame.mask.from_surface(self.image)
        self.dust_frame_index = 0
        self.dust_animation_speed = 0
        
        #mouvement
        self.direction = vector()
        self.pos = vector(self.rect.center)
        self.speed = 310
        self.gravity = 6
        self.on_floor = False
        
        #collision
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate(-16,-14)
        
        self.invul_timer = Timer(500)
        self.invul_timer1 = Timer(900)
        
        self.jump_sound = jump_sound
        self.jump_sound.set_volume(0.2)

        #damage
        self.prise_degat = prise_degat
        self.duree_damage = 0

    def damage(self):
        """_summary_
        Gestion de la prise de dégat avec une durée d'invulnérabilité et un effet de knockback.
        """
        if not self.invul_timer.active:
            self.duree_damage = pygame.time.get_ticks()
            self.invul_timer1.activate()
            self.invul_timer.activate()
            self.prise_degat(-25)
            self.direction.y -= 1
    
    
    def get_status(self):
        """_summary_
        Gestion du statut pour ne pas pouvoir sauter deux fois par exemple.
        """
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
           self.status = 'run' if self.direction.x != 0 else 'idle'
    
    def animate(self, dt):
        """_summary_
        Animation du joueur avec des images qui défilent.
        Ajout d'un masque qui fait briller le joueur quand il prend des dégats.
        """
        current_animation = self.animation_frames[f'{self.status}_{self.orientation}']
        self.frame_index += VITESSE_ANIMATION * dt / 2
        self.frame_index = 0 if self.frame_index >= len(current_animation) else self.frame_index
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

        if self.invul_timer.active:
           surf = self.mask.to_surface()
           surf.set_colorkey('black')
           self.image = surf
        
    def input(self):
        """_summary_
        Gestion des déplacements du joueur selon les touches préssées.
        """
        keys =  pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.direction.x = 1
            self.orientation = 'right'
        elif keys[pygame.K_q]:
            self.direction.x = -1
            self.orientation = 'left'
        else: self.direction.x = 0
        
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -2
            self.jump_sound.play()
        
    def move(self, dt):
        """_summary_
        Gestion du déplacement du joueur selon la direction choisi.
        """
        #horizontale
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        #verticale
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
    
    def apply_gravity(self, dt):
        """_summary_
        Gestion de la gravité qui permet de de tomber quand on saute ou quand on tombe d'une platforme.
        """
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y
    
    def check_on_floor(self):
        """_summary_
        Regarde si il y'a une hitbox sous le joueur.
        """
        floor_rect = pygame.Rect(self.hitbox.bottomleft,(self.hitbox.width,2))
        floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(floor_rect)]
        self.on_floor = True if floor_sprites else False
    
    def collision(self, direction):
        """_summary_
        Gestion de collision avec la hitbox du joueur.
        """
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    self.hitbox.right = sprite.rect.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.rect.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else:
                    self.hitbox.top = sprite.rect.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
                    self.direction.y = 0
 
    def update(self, dt):
        """_summary_
        Mise à jour du statut du joueur,de la gravité et des images de l'animation.
        Regarde contament ce qu'il se passe sur la hitbox du joueur.
        """
        self.input()
        self.apply_gravity(dt)
        self.move(dt)
        self.check_on_floor()
        self.invul_timer.uptade()
        
        self.get_status()
        self.animate(dt)
