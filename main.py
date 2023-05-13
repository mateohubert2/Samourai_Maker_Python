import pygame
from parametres import*
from pygame.image import load
from support import*
from pygame.math import Vector2 as vector
from editeur import Editeur
from level import Level
from os import walk

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        self.clock = pygame.time.Clock()
        self.imports()
        
        self.editeur_active = True
        self.transition = Transition(self.toggle)
        self.editeur = Editeur(self.cases_terrain, self.switch)
        
        
        #cureur
        surf = load('Graphique/curseur/souris.png').convert_alpha()
        curseur = pygame.cursors.Cursor((0,0), surf)
        pygame.mouse.set_cursor(curseur)
        
    def imports(self):
        self.cases_terrain = import_folder_dict('Graphique/Terrain/Land')  
        self.bas_eau = load('Graphique/Eau/eau.png').convert_alpha()
        self.water_top_animation = import_folder('Graphique/Eau/Animations')
        
        #piece
        self.gold = import_folder('Graphique/Piece/Animation_Piece_Gold')
        self.silver = import_folder('Graphique/Piece/Animation_Piece_Silver')
        self.diamond = import_folder('Graphique/Piece/Animation_Piece_Diamond')
        self.particule = import_folder('Graphique/Piece/Particule')
        
        #arbre
        self.arbre = {folder: import_folder(f'Graphique/Arbre/{folder}') for folder in list(walk('Graphique/Arbre'))[0][1]}
        
        self.ennemie2 = {folder: import_folder(f'Graphique/Ennemie/Animation_Ennemie_2/{folder}') for folder in list(walk('Graphique/Ennemie/Animation_Ennemie_2'))[0][1]}
        
    def toggle(self):
        self.editeur_active = not self.editeur_active
    
    def switch(self, grid = None):
        self.transition.active = True
        if grid:
            self.level = Level(grid, self.switch,{
                'land': self.cases_terrain,
                'water bottom': self.bas_eau,
                'water top': self.water_top_animation,
                'gold': self.gold,
                'silver': self.silver,
                'diamond': self.diamond,
                'particle': self.particule,
                'arbre': self.arbre,
                'ennemie2': self.ennemie2
            })
    
    def lancement(self):
        while True:
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 1000
                    
            if self.editeur_active:
                self.editeur.lancement(dt)
            else:
                self.level.lancement(dt)
            self.transition.display(dt)
            pygame.display.update()

class Transition:
    def __init__(self, toggle):
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle
        self.active = False
        
        self.largeur_bordure = 0
        self.direction = 1
        self.center = (LARGEUR_FENETRE / 2, HAUTEUR_FENETRE / 2)
        self.rayon = vector(self.center).magnitude()
        self.threshold = self.rayon + 100
    
    def display(self, dt):
        if self.active:
            self.largeur_bordure += 1000 * dt * self.direction
            if self.largeur_bordure >= self.threshold:
                self.direction = -1
                self.toggle()
            if self.largeur_bordure < 0:
                self.active = False
                self.largeur_bordure = 0
                self.direction = 1
            pygame.draw.circle(self.display_surface, 'black', self.center, self.rayon, int(self.largeur_bordure))
            

if __name__ == '__main__':
    main = Main()
    main.lancement()
