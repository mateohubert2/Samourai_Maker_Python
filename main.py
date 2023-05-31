import pygame
from parametres import*
from pygame.image import load
from support import*
from pygame.math import Vector2 as vector
from editeur import Editeur
from level import Level
from ATH import ATH
from os import walk

class Main:
    #instantiation de la classe
    def __init__(self):
        """_summary_
        instancie les variables necessaires dans la classe main
        """ 
        pygame.init()
        self.display_surface = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        self.clock = pygame.time.Clock()
        self.imports()
        #definition de la partie qui gere la vie et le nombre de piece
        self.vie_max = 100
        self.vie_actuelle = 100
        #ath
        self.ath = ATH(self.display_surface)
        self.piece = 0
        self.editeur_active = True
        self.transition = Transition(self.toggle)
        self.editeur = Editeur(self.cases_terrain, self.switch)
        #importation et changement du cureur
        #convert_alpha() permet d'augmenter les performances
        surf = load('Graphique/curseur/souris.png').convert_alpha()
        curseur = pygame.cursors.Cursor((0,0), surf)
        pygame.mouse.set_cursor(curseur)
   
    def imports(self):
        """_summary_
        importation des elements à aller chercher dans un dossier (image et sons)
        on importera quelquefois un fichier complet pour ne pas avaoir à prendre toutes les images d'un fichier
        on s'occupera de gerer ces fichiers plus tard
        """
        #terrain
        self.cases_terrain = import_folder_dict('Graphique/Terrain/Land')  
        self.bas_eau = load('Graphique/Eau/eau.png').convert_alpha()
        self.water_top_animation = import_folder('Graphique/Eau/Animations')
        #piece
        self.gold = import_folder('Graphique/Piece/Animation_Piece_Gold')
        self.silver = import_folder('Graphique/Piece/Animation_Piece_Silver')
        self.diamond = import_folder('Graphique/Piece/Animation_Piece_Diamond')
        self.particule = import_folder('Graphique/Piece/Particule')
        #arbre (fichier complet)
        self.arbre = {folder: import_folder(f'Graphique/Arbre/{folder}') for folder in list(walk('Graphique/Arbre'))[0][1]}
        #ennemis (fichier complet)
        self.ennemie2 = {folder: import_folder(f'Graphique/Ennemie/Animation_Ennemie_2/{folder}') for folder in list(walk('Graphique/Ennemie/Animation_Ennemie_2'))[0][1]}
        self.ennemie = {folder: import_folder(f'Graphique/Ennemie/Animation_Ennemie_1/{folder}') for folder in list(walk('Graphique/Ennemie/Animation_Ennemie_1'))[0][1]}
        self.pearl = load('Graphique/Ennemie/Pearl/pearl.png').convert_alpha()
        #joueur (fichier complet)
        self.player_graphics = {folder: import_folder(f'Graphique/Personnage/Animation_Personnage/{folder}') for folder in list(walk('Graphique/Personnage/Animation_Personnage'))[0][1]}
        #nuage
        self.clouds = import_folder('Graphique/Nuage')
        #musique
        self.level_sounds = {
            'coin': pygame.mixer.Sound('audio/coin.wav'),
            'hit': pygame.mixer.Sound('audio/hit.wav'),
            'jump': pygame.mixer.Sound('audio/jump.wav'),
            'music': pygame.mixer.Sound('audio/SuperHero.ogg'),
        }

    def toggle(self):
        """_summary_
        boucle de musique de l'editeur sans fin tant qu'on est dans l'éditeur
        """
        self.editeur_active = not self.editeur_active
        if self.editeur_active:
            self.editeur.editor_music.play(loops = -1)
   
    def switch(self, grid = None):
        """_summary_
        création d'un dictionnaire de tous les graphismes reutilisable par la suite
        Args:
            grid (_type_, optional): permet de recuperer les information d'une liste de donnée
        """
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
                'ennemie2': self.ennemie2,
                'ennemie': self.ennemie,
                'player': self.player_graphics,
                'pearl': self.pearl,
                'clouds': self.clouds},
            self.level_sounds)
    
    def lancement(self):
        """_summary_
        definition des conditions de lancement de l'editeur ou du niveau
        +lancement de l'editeur au début 
        """
        while True:
            #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
                    
            if self.editeur_active:
                self.editeur.lancement(dt)
            else:
                self.level.lancement(dt)
                self.ath.barre_de_vie(self.vie_actuelle,self.vie_max)
                
            self.transition.display(dt)
        
            pygame.display.update()

class Transition:
    def __init__(self, toggle):
        """_summary_
        instancie les variables necessaires à la classe Transition
        Args:
            toggle (fonction definie plus haut): boucle de musique sans fin de l'editeur
        """
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle
        self.active = False
        
        self.largeur_bordure = 0
        self.direction = 1
        self.center = (LARGEUR_FENETRE / 2, HAUTEUR_FENETRE / 2)
        self.rayon = vector(self.center).magnitude()
        self.threshold = self.rayon + 100
    #condtions de la transition en 2 temps (faire grandir le cercle jusqu'au cenrtre puis repart en arrière)
    def display(self, dt):
        if self.active:
            self.largeur_bordure += 1000 * dt * self.direction
            #augmente l'epaisseur du cercle jusqu'au centre
            if self.largeur_bordure >= self.threshold:
                self.direction = -1
                self.toggle()
            #diminue l'epaisseur jusqu'au crecle initial
            if self.largeur_bordure < 0:
                self.active = False
                self.largeur_bordure = 0
                self.direction = 1
            pygame.draw.circle(self.display_surface, 'black', self.center, self.rayon, int(self.largeur_bordure))
            
#obligation de lancer le programme dans le main sinon ça ne va pas marcher
if __name__ == '__main__':
    main = Main()
    main.lancement()
