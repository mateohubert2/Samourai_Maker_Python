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
from niveau import *
from game_data import level_0, level_1, level_2

class Main:
    #instantiation de la classe
    def __init__(self):
        """_summary_
        Instancie les variables necessaires dans la classe main.
        """ 
        pygame.init()
        self.selection = 0
        self.i = True
        self.display_surface = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        self.clock = pygame.time.Clock()
        self.imports()
        self.menu_appuye = False
        self.rect_musique1 = 428
        self.number = 50
        self.musique_volume = 0.5
        self.volume_level = 0.5
        #ath
        self.ath = ATH(self.display_surface)
        self.piece = 0
        self.editeur_active = True
        self.transition = Transition(self.toggle)
        self.editeur = Editeur(self.cases_terrain, self.switch, self.musique_volume)
        self.selection_bruit = pygame.mixer.Sound('audio/Selection.ogg')
        self.selection_bruit.set_volume(0.4)
        self.musique_bg = pygame.mixer.Sound('audio/musique_bg.ogg')
        self.musique_bg.set_volume(0.25)
        self.Victory = pygame.mixer.Sound('audio/Victory.ogg')
        self.Victory.set_volume(0.25)
        #importation et changement du cureur
        #convert_alpha() permet d'augmenter les performances
        surf = load('Graphique/curseur/souris.png').convert_alpha()
        curseur = pygame.cursors.Cursor((0,0), surf)
        pygame.mouse.set_cursor(curseur)
   
    def imports(self):
        """_summary_
        Importation des elements à aller chercher dans un dossier (image et sons).
        On importera quelquefois un fichier complet pour ne pas avaoir à prendre toutes les images d'un fichier.
        On s'occupera de gerer ces fichiers plus tard.
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
            'music': pygame.mixer.Sound('audio/musique_bg.ogg'),
            'Game_Over': pygame.mixer.Sound('audio/Bruitage_Game_Over.ogg'),
        }

    def toggle(self):
        """_summary_
        Boucle de musique de l'editeur sans fin tant qu'on est dans l'éditeur.
        """
        self.editeur_active = not self.editeur_active
        if self.editeur_active:
            self.editeur.editor_music.play(loops = -1)
   
    def switch(self, grid = None):
        """_summary_
        Création d'un dictionnaire de tous les graphismes reutilisable par la suite.
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
        definition des conditions de lancement de l'editeur et du jeu sur le niveau crée + menu de Game_Over + menu de victoire
        """
        while True:
            #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            #lancement de l'éditeur de niveau
            if self.editeur_active:
                self.editeur.lancement(dt)
                
                #bouton retour menu principal
                if self.editeur.retour_menu == True:
                    self.editeur.editor_music.stop()
                    main_retour_menu = Main()
                    main_retour_menu.lancement2()
                    self.editeur.retour_menu = False
            else:
                #mode jeu sur le niveau crée par l'utilisateur
                self.level.lancement(dt)
                self.editeur.editor_music.stop()
                #condition de game over + menu de game over
                if self.level.vie_actuelle_level == 0:
                    self.level.bg_music.stop()
                    self.level.Game_Over_music.play()
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
                                self.selection_bruit.play()
                                self.level.bg_music.stop()
                                self.editeur.editor_music.play(loops = -1)
                                self.editeur_active = True
                                self.i = False
                            if event.type == pygame.QUIT:
                                pygame.quit()
                            if event.type == pygame.MOUSEBUTTONDOWN and self.rectover2.collidepoint(position_souris()):
                                self.selection_bruit.play()
                                self.editeur.editor_music.stop()
                                self.level.bg_music.stop()
                                mainmenu = Main()
                                mainmenu.lancement2()
                    self.i = True
                #conditions de victoire + menu de victoire
                if len(self.level.coin_sprites) == 0:
                    self.level.bg_music.stop()
                    self.Victory.play()
                    self.image1 = pygame.image.load('Graphique/game_over/victoire.png').convert_alpha()
                    self.image1 = pygame.transform.scale2x(self.image1)
                    self.image2 = pygame.image.load('Graphique/game_over/tryagain.png').convert_alpha()
                    self.image3 = pygame.image.load('Graphique/game_over/menu.png').convert_alpha()
                    self.rectover2 = pygame.draw.rect(self.display_surface, 'blue', pygame.Rect(LARGEUR_FENETRE - 1230, ((HAUTEUR_FENETRE/2)+170), 473, 136))
                    self.rectover = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 592, ((HAUTEUR_FENETRE/2)+130), 550, 130))
                    self.display_surface.fill('#ddc6a1')
                    self.display_surface.blit(self.image1, (-250,-100))
                    self.display_surface.blit(self.image2, (LARGEUR_FENETRE - 632, ((HAUTEUR_FENETRE/2)+140)))
                    self.display_surface.blit(self.image3, (LARGEUR_FENETRE - 1352, ((HAUTEUR_FENETRE/2)+110)))
                    pygame.display.update()
                    while self.i == True:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN and self.rectover.collidepoint(position_souris()):
                                self.selection_bruit.play()
                                self.level.bg_music.stop()
                                self.editeur.editor_music.play(loops = -1)
                                self.editeur_active = True
                                self.i = False
                            if event.type == pygame.QUIT:
                                pygame.quit()
                            if event.type == pygame.MOUSEBUTTONDOWN and self.rectover2.collidepoint(position_souris()):
                                self.selection_bruit.play()
                                self.editeur.editor_music.stop()
                                self.level.bg_music.stop()
                                mainmenu = Main()
                                mainmenu.lancement2()
                    self.i = True
            self.transition.display(dt)
            pygame.display.update()
            
    def lancement1(self):
        """_summary_
        Menu de la section "level" qui permet de selectionner 1 niveau parmi les 3 proposés.
        """
        while True:
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                #Niveau1
                if event.type == pygame.MOUSEBUTTONDOWN and self.rect1.collidepoint(position_souris()):
                    self.editeur.editor_music.stop()
                    
                    self.selection_bruit.play()
                    
                    mainlvl1 = Main()
                    mainlvl1.lancement5()
                #Niveau2
                if event.type == pygame.MOUSEBUTTONDOWN and self.rect2.collidepoint(position_souris()):
                    self.editeur.editor_music.stop()
                    
                    self.selection_bruit.play()
                    
                    mainlvl1 = Main()
                    mainlvl1.lancement3()
                #Niveau3
                if event.type == pygame.MOUSEBUTTONDOWN and self.rect3.collidepoint(position_souris()):
                    self.selection_bruit.play()
                    self.editeur.editor_music.stop()
                    
                    
                    mainlvl1 = Main()
                    mainlvl1.lancement4()
        
            self.display_surface.fill('#ddc6a1')
            self.image = pygame.image.load('Graphique/Levels/Menu/arbrefond.png').convert_alpha()
            self.image1 = pygame.image.load('Graphique/Levels/Menu/level1.png').convert_alpha()
            self.image2 = pygame.image.load('Graphique/Levels/Menu/level2.png').convert_alpha()
            self.image3 = pygame.image.load('Graphique/Levels/Menu/level3.png').convert_alpha()
            self.image = pygame.transform.scale2x(self.image)
            self.image1 = pygame.transform.scale2x(self.image1)
            self.image2 = pygame.transform.scale2x(self.image2)
            self.image3 = pygame.transform.scale2x(self.image3)
            self.rect1 = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(160,120,300,200))
            self.rect2 = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(460,420,300,200))
            self.rect3 = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(760,120,300,200))
            self.display_surface.blit(self.image, (0,0))
            self.display_surface.blit(self.image1, (150,100))
            self.display_surface.blit(self.image2, (450,400))
            self.display_surface.blit(self.image3, (750,100))
            
            pygame.display.update()
    
    def lancement5(self):
        """_summary_
        lancement niveau 1 dans le mode de jeu "Level", on appel cette fonction dans la fonction précédente
        """
        niveau = Niveau(level_0, self.display_surface)
        self.editeur.editor_music.stop()
        self.musique_bg.play()
        while True:
        #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and niveau.retour_menu.collidepoint(position_souris()):
                    self.musique_bg.stop()
                    self.selection_bruit.play()
                    main_retour_menu = Main()
                    main_retour_menu.lancement2()
            self.display_surface.fill('grey')
            niveau.run()
            
            pygame.display.update()
    
    def lancement3(self):
        """_summary_
        lancement niveau 2 dans le mode de jeu "Level", on appel cette fonction dans la fonction précédente
        """
        niveau = Niveau(level_1, self.display_surface)
        self.editeur.editor_music.stop()
        self.musique_bg.play()
        while True:
        #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and niveau.retour_menu.collidepoint(position_souris()):
                    self.musique_bg.stop()
                    self.selection_bruit.play()
                    main_retour_menu = Main()
                    main_retour_menu.lancement2()
            self.display_surface.fill('grey')
            niveau.run()
            pygame.display.update()
            
    def lancement4(self):
        """_summary_
        lancement niveau 3 dans le mode de jeu "Level", on appel cette fonction dans la fonction précédente
        """
        niveau = Niveau(level_2, self.display_surface)
        self.editeur.editor_music.stop()
        self.musique_bg.play()
        while True:
        #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and niveau.retour_menu.collidepoint(position_souris()):
                    self.musique_bg.stop()
                    self.selection_bruit.play()
                    main_retour_menu = Main()
                    main_retour_menu.lancement2()
                    self.musique_bg.stop()
            self.display_surface.fill('grey')
            niveau.run()
            
            pygame.display.update()
            
    def lancement2(self):
        """_summary_
        Lancement du menu principal qui se lance dès le début
        """
        while True:
        #changer le nom de la fênetre de jeu
            pygame.display.set_caption('Samourai Maker par Matéo et Evan')
            dt = self.clock.tick() / 850
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                #parametrage son par l'utilisateur
                if event.type == pygame.MOUSEBUTTONDOWN and self.rect_options.collidepoint(position_souris()):
                    self.i = 0
                
                while self.i == 0:
                    self.surf_fond = pygame.Surface((720, 480))
                    self.surf_fond.fill('white')
                    self.surf_fond.set_alpha(3)
                    self.image_croix = pygame.image.load('Graphique/Options/croix.png').convert_alpha()
                    self.image_exit = pygame.image.load('Graphique/Options/exit.png').convert_alpha()
                    self.image_musique = pygame.image.load('Graphique/Options/musique.png').convert_alpha()
                    self.display_surface.blit(self.surf_fond, [280,120])
                    self.display_surface.blit(self.image_exit, [300,500])
                    self.display_surface.blit(self.image_croix, [455,-55])
                    self.display_surface.blit(self.image_musique, [250,20])
                    #self.rect_musique = pygame.draw.rect(self.display_surface, 'red',pygame.Rect(415, 172, 10, 30))
                    self.vecteur_x = 0
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN and self.rect_croix.collidepoint(position_souris()):
                            self.i = 1
                        if event.type == pygame.QUIT:
                            pygame.quit()
                        if event.type == pygame.MOUSEBUTTONDOWN and self.rect_exit.collidepoint(position_souris()):
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN and self.rect_musique_fond.collidepoint(position_souris()):
                            self.vecteur = position_souris()
                            self.vecteur_x = self.vecteur[0]
                            self.rect_musique = pygame.draw.rect(self.display_surface, 'white',pygame.Rect(self.rect_musique1, 172, 10, 30))
                            self.rect_musique1 = self.vecteur_x
                            self.pourcentage = int((self.vecteur_x - 350) * 0.66)
                            self.number = self.pourcentage
                    police = pygame.font.SysFont("monospace",20)
                    text = police.render(str(self.number), 1 , (255,0,0))
                    if self.number < 10:
                        self.display_surface.blit(text, (490,150))
                    if self.number <= 99 and self.number >=10:
                        self.display_surface.blit(text, (480,150))
                    if self.number >= 100:
                        text = police.render(("100"), 1 , (255,0,0))
                        self.display_surface.blit(text, (470,150))
                    police = pygame.font.SysFont("monospace",20)
                    text = police.render(("%"), 1 , (255,0,0))
                    self.display_surface.blit(text, (503,150))
                    self.rect_musique = pygame.draw.rect(self.display_surface, 'red',pygame.Rect(self.rect_musique1, 172, 10, 30))
                    
                    pygame.display.update()
                    self.musique_volume = round((self.number / 100), 1)
                    self.editeur.musique_volume = self.musique_volume
                    self.editeur.changer_volume(self.musique_volume)
                    
                pygame.display.update()
                    #self.rect_musique2 = pygame.draw.rect(self.display_surface, 'red',pygame.Rect(self.rect_musique.x, 172, 10, 30))    
                    #pygame.display.update()
                        
            self.rect_croix = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(925, 140, 50, 50))
            self.rect_exit = pygame.draw.rect(self.display_surface, 'blue', pygame.Rect(300, 500, 210, 94))
            self.rect_musique_fond = pygame.draw.rect(self.display_surface, 'blue', pygame.Rect(350, 172, 155, 30))
            self.rect_options = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 115, 25, 80, 80))
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
            self.image_options = pygame.image.load('Graphique/Options/roue_crante.png').convert_alpha()
            self.display_surface.blit(self.image_options, [LARGEUR_FENETRE - 175, -100])
            self.display_surface.blit(text1, (350,150))
            #menu de selection du mode de jeu 
            pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(position_souris()):
                self.selection_bruit.play()
                self.editeur.editor_music.stop()
                main = Main()
                main.lancement()
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect1.collidepoint(position_souris()):
                self.selection_bruit.play()
                self.editeur.editor_music.stop()
                print(self.musique_volume)
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
        """_summary_
        Affiche un cercle noir qui va retrecir puis s'élargir pour faire une transition
        """
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
