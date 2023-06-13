import pygame
from parametres import*
from pygame.image import load
from support import*
from pygame.math import Vector2 as vector
from editeur import *
from level import*
from ATH import ATH
from os import walk
from pygame.mouse import get_pos as position_souris
from niveau import Niveau
from game_data import level_0

class Main:
    #instantiation de la classe
    def __init__(self):
        """_summary_
        instancie les variables necessaires dans la classe main
        """ 
        pygame.init()
        self.selection = 0
        self.i = True
        self.display_surface = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        self.clock = pygame.time.Clock()
        self.imports()
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
                if self.editeur.retour_menu == True:
                    main_retour_menu = Main()
                    main_retour_menu.lancement2()
                    self.editeur.retour_menu = False
            else:
                self.level.lancement(dt)
                if self.level.vie_actuelle_level == 0:
                    self.image1 = pygame.image.load('Graphique/game_over/game_over.png').convert_alpha()
                    self.image2 = pygame.image.load('Graphique/game_over/tryagain.png').convert_alpha()
                    self.image3 = pygame.image.load('Graphique/game_over/menu.png').convert_alpha()
                    self.rectover2 = pygame.draw.rect(self.display_surface, 'blue', pygame.Rect(LARGEUR_FENETRE - 1230, ((HAUTEUR_FENETRE/2)+170), 473, 136))
                    self.rectover = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 592, ((HAUTEUR_FENETRE/2)+130), 550, 130))
                    self.display_surface.fill('#ddc6a1')
                    self.display_surface.blit(self.image1, (90,-270))
                    self.display_surface.blit(self.image2, (LARGEUR_FENETRE - 632, ((HAUTEUR_FENETRE/2)+140)))
                    self.display_surface.blit(self.image3, (LARGEUR_FENETRE - 1352, ((HAUTEUR_FENETRE/2)+110)))
                    
                    pygame.display.update()
                    while self.i == True:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN and self.rectover.collidepoint(position_souris()):
                                self.editeur_active = True
                                self.i = False
                            if event.type == pygame.QUIT:
                                pygame.quit()
                            if event.type == pygame.MOUSEBUTTONDOWN and self.rectover2.collidepoint(position_souris()):
                                mainmenu = Main()
                                mainmenu.lancement2()
                    self.i = True
            self.transition.display(dt)
                            
            pygame.display.update()
            
    def lancement1(self):
        """_summary_
        definition des conditions de lancement de l'editeur ou du niveau
        +lancement de l'editeur au début 
        """
        niveau = Niveau(level_0, self.display_surface)
        while True:
        #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            self.display_surface.fill('grey')
            niveau.run()
            
            pygame.display.update()
    
    def lancement2(self):
        """_summary_
        definition des conditions de lancement de l'editeur ou du niveau
        +lancement de l'editeur au début 
        """
        while True:
        #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            self.display_surface.fill('blue')
            self.image1 = pygame.image.load('Graphique/Levels/Menu/arbrefond.png').convert_alpha()
            self.image1 = pygame.transform.scale2x(self.image1)
            self.display_surface.blit(self.image1, (0,0))
            self.rect = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 532, ((HAUTEUR_FENETRE/2)+20), 288, 180))
            self.rect1 = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 1062, ((HAUTEUR_FENETRE/2)+20), 288, 180))
            self.image = pygame.image.load('Graphique/Levels/Menu/level.png').convert_alpha()
            self.image = pygame.transform.scale2x(self.image)
            self.display_surface.blit(self.image, [200, (HAUTEUR_FENETRE/2)])
            self.imagex = pygame.image.load('Graphique/Levels/Menu/fond.png').convert_alpha()
            self.display_surface.blit(self.imagex, [150, 30])
            self.image_text = pygame.image.load('Graphique/Levels/Menu/edit.png').convert_alpha()
            self.image_text = pygame.transform.scale2x(self.image_text)
            self.display_surface.blit(self.image_text, [LARGEUR_FENETRE - 550, (HAUTEUR_FENETRE/2)])
            police = pygame.font.SysFont("monospace",100)
            text = police.render(("Samourai Maker"), 1 , (255,0,0))
            self.display_surface.blit(text, (210,50))
            police1 = pygame.font.SysFont("monospace",40)
            text1 = police1.render(("HUBERT Matéo, HELLE Evan"), 1 , (255,0,0))
            self.display_surface.blit(text1, (350,150))
            
            pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(position_souris()):
                main = Main()
                main.lancement()
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect1.collidepoint(position_souris()):
                main1 = Main()
                main1.lancement1()

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
    main2 = Main()
    main2.lancement2()
