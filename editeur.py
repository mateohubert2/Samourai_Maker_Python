import pygame
from pygame.math import Vector2 as vector
from parametres import*
from pygame.mouse import get_pressed as boutons_souris
from pygame.mouse import get_pos as position_souris
from pygame.image import load
from menu import Menu
from timer import Timer
from support import*
from random import choice, randint
import sys
#definition de la classe editeur qui va gérer ce qui se passe dans l'éditeur de niveau
class Editeur:
    #la fonction __init__ est une fonction spéciale qui permet l'instanciation d'une classe c'est un sorte de constructeur.
    #le constructeur a besoin de self pour acceder aux attributs de l'objet, des cases qui pourront etre placé et de switch pour pouvoir passer au lvl
    def __init__(self, cases_terrain, switch, volume_musique):
        """_summary_
        La fonction __init__ va servir a instancier toutes les variables et objets nécessaires au bon fonctionnement de l'éditeur.
        On utilisera majoritairement des dictionnaires de données et des listes comme pour canvas_data qui va contenir toutes les
        informations des cases placées. 
        Args:
            cases_terrain (dictionnaire): contient toutes les cases terrain dans un dictionnaire par exemple A, AB, ABC...
            switch (dictionnaire de données et listes de cases): contient toutes les images importés classés par types
            ainsi que l'information de tout les elements graphique du niveau crée par le joueur a transmettre au level
        """
        #description du main
        
        self.display_surface = pygame.display.get_surface()
        self.canvas_data = {}
        self.switch = switch
        self.retour_menu = False
        self.a = 1
        #importation
        self.cases_terrain = cases_terrain
        self.imports()
        self.musique_volume = 0.5
        #nuages
        self.current_clouds = []
        self.cloud_surf = import_folder('Graphique/Nuage')
        self.cloud_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.startup_clouds()
        self.number = 50
        self.rect_musique1 = 428
        #navigation
        self.origin = vector()
        self.pan_active = False
        self.pan_offset = vector()
        
        #ligne de support
        self.ligne_de_support_surface = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        self.ligne_de_support_surface.set_colorkey('green')
        self.ligne_de_support_surface.set_alpha(30)
        
        #selection
        self.selection_index = 2
        self.derniere_cellule_selectionne = None
        #menu
        self.menu = Menu()
        
        #objets
        self.canvas_objets = pygame.sprite.Group()
        self.foreground = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        self.objet_drag_active = False
        self.object_timer = Timer(400)
        self.rect_croix = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(925, 140, 50, 50))
        self.rect_exit = pygame.draw.rect(self.display_surface, 'blue', pygame.Rect(300, 500, 210, 94))
        self.rect_musique_fond = pygame.draw.rect(self.display_surface, 'blue', pygame.Rect(350, 172, 155, 30))
        self.rect_options = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 115, 25, 80, 80))
        
        #personnage
        CanvasObject(
            pos = (200, HAUTEUR_FENETRE / 2),
            frames = self.animations[0]['frames'],
            tile_id = 0,
            origin = self.origin,
            group = [self.canvas_objets, self.foreground])
        
        #ciel
        self.sky_handle = CanvasObject(
            pos = (LARGEUR_FENETRE / 2, HAUTEUR_FENETRE / 2),
            frames = [self.sky_handle_surf],
            tile_id = 1,
            origin = self.origin,
            group = [self.canvas_objets, self.background]
            )
        
        #musique
        self.editor_music = pygame.mixer.Sound('audio/Explorer.ogg')
        self.editor_music.set_volume(self.musique_volume)
        self.editor_music.play(loops = -1)
        self.selection_bruit = pygame.mixer.Sound('audio/Selection.ogg')
        self.selection_bruit.set_volume(0.4)
        
    def cellule_actuelle(self, obj = None):
        """_summary_
        La fonction cellule_actuelle à pour objectif de determiner l'emplacement de la cellule que l'on utilise lors d'un clique déplacement etc..
        pour ce faire, on recupere la distance entre l'endroit du clic et l'origine de la fenetre (en haut a gauche) et l'on divise cette
        distance par la taille de nos cases. Ainsi, si l'on clique à l'emplacement 652, 433 on obtient la case 10, 6
        Si l'on apelle la fonction sur un objet deja existant, on recupere la distance de l'origine de l'objet calculer précedement
        Args:
            obj (_type_, optional): la fonction peux prendre en entrée un objet deja existant

        Returns:
            _type_: la fonction retourne la colonne et la ligne de la case souhaité
        """
        distance_de_origine = vector(position_souris()) - self.origin if not obj else vector(obj.distance_to_origin) - self.origin

        if distance_de_origine.x > 0:
            col = int(distance_de_origine.x / TAILLE_CASES)
        else:
            col = int(distance_de_origine.x / TAILLE_CASES) - 1

        if distance_de_origine.y > 0:
            lig = int(distance_de_origine.y / TAILLE_CASES)
        else:
            lig = int(distance_de_origine.y / TAILLE_CASES) - 1

        return col, lig    

    def changer_volume(self, musique_volume):
        """_summary_
        La fonction changer volume à pour objectif de changer le volume de la musique quand on clique sur la jauge de la musique
        dans le menu options
        Args:
            musique_volume (_type_): la fonction prend en entre un nombre allant de 0 à 1 par pas de 0.1 calculer en fonction de
            la position du curseur dans le menu options
        """
        self.editor_music.set_volume(musique_volume)
    
    def trouver_voisins(self, cell_pos):
        """_summary_
        La fonction trouver_voisins a pour but de trouver les cases remplit autour de la case choisit et ca afin de remplir un liste
        pour pouvoir dessiner automatiquement la bonne case en fonction de ses voisins. Ceci fonctionne a l'aide d'une 'matrice'.
        c'est a dire que l'on regarde si la case au dessus est remplit si oui la liste prend comme valeur pour l'emplacement A.
        Ensuite on regarde les autres cases en tournant dans le sens horaire. Ce qui nous donne par exemple une case avec le nom AEF
        ce qui permet d'importer directement la bonne image. C'est le meme foncitonnement pour l'eau mais uniquement pour detecter si
        l'eau est au dessous d'un autre bloc eau. On regarde les voisins dans un carré de 3 blocs de coté positionner de maniere
        a ce que le bloc ciblé soit au centre du cluster.
        Args:
            cell_pos (_type_): _description_
        """

        # create a local cluster
        taille_cluster = 3
        cluster_local = [
            (cell_pos[0] + col - int(taille_cluster / 2), cell_pos[1] + lig - int(taille_cluster / 2)) 
            for col in range(taille_cluster) 
            for lig in range(taille_cluster)]

            # check neighbors
        for cell in cluster_local:
                if cell in self.canvas_data:
                    self.canvas_data[cell].cases_terrain = []
                    self.canvas_data[cell].water_on_top = False
                    for name, side in DIRECTION_VOISINS.items():
                        cellule_voisine = (cell[0] + side[0],cell[1] + side[1])
                        
                        if cellule_voisine in self.canvas_data:
                            
                            #eau voisins
                            if self.canvas_data[cellule_voisine].has_water and self.canvas_data[cell].has_water and name == 'A':
                                self.canvas_data[cell].water_on_top = True
                        
                            #terrain voisins
                            if cellule_voisine in self.canvas_data:
                                if self.canvas_data[cellule_voisine].has_terrain:
                                    self.canvas_data[cell].cases_terrain.append(name)
    
    def imports(self):
        """_summary_
        la fonction import a pour but d'importer tous les graphics nécéssaire au bon fonctionnement de l'éditeur.
        """
        self.bas_eau = load('Graphique/Eau/eau.png').convert_alpha()
        self.sky_handle_surf = load('Graphique/curseur/handle.png').convert_alpha()
        #animations
        self.animations = {}
        for key, value in EDITOR_DATA.items():
            if value['graphics']:
                graphics = import_folder(value['graphics'])
                self.animations[key] = {
                    'frame index': 0,
                    'frames': graphics,
                    'length': len(graphics)
                }
        #preview
        self.preview_surfs = {key: load(value['preview']) for key, value in EDITOR_DATA.items() if value['preview']}
        
    def animation_uptade(self, dt):
        """_summary_
        la fonction animation_update a pour but de faire tourner en boucle les images d'animation numéroté de 0 a n dans le but
        de créer du mouvement
        Args:
            dt (_type_): dt est en nombre qui va etre pris en compte dans toutes les fonctions gérant une fréquence de rafraichissement
            et ce dans un but de performance pour ne pas redessiner la meme chose 1000 fois par secondes mais egalement pour controler
            la vitesse d'animation des personnages etc...
        """
        for value in self.animations.values():
            value['frame index'] += (VITESSE_ANIMATION * dt) / 1.5
            if value['frame index'] >= value['length']:
                value['frame index'] = 0
        
    def create_grid(self):
        """_summary_
        la fonction create_grid a pour objectif de crée une grille avec l'emplacement et le nom de l'image de chaque bocs possé
        dans l'éditeur afin de transmettre les données au level

        Returns:
            _type_: _la fonction return des dictionnaires nommés en fonction du types de cases contenue afin de pouvoir dessiner dans
            level dans le bon ordre pour ne pas se retrouver avec de l'eau devant des blocs
        """
        #ajouter les objets au cases
        
        for tile in self.canvas_data.values():
            tile.objects = []
        
        for obj in self.canvas_objets:
            cellule_actuelle = self.cellule_actuelle(obj)
            offset = vector(obj.distance_to_origin) - (vector(cellule_actuelle) * TAILLE_CASES)
            
            if cellule_actuelle in self.canvas_data: #la case existe deja
                self.canvas_data[cellule_actuelle].add_id(obj.tile_id, offset)
            else: #la case n'existe pas encore
                self.canvas_data[cellule_actuelle] = CanvasTile(obj.tile_id, offset)
                
        #grid offset
        gauche = sorted(self.canvas_data.keys(), key = lambda tile: tile[0])[0][0]
        haut = sorted(self.canvas_data.keys(), key = lambda tile: tile[1])[0][1]

        #grille vide
        couche = {
            'eau': {},
            'arbre bg': {},
            'terrain': {},
            'ennemie': {},
            'piece': {},
            'objets fg': {},
        }
        
        #remplir la grille
        for tile_pos, tile in self.canvas_data.items():
            lig_ajuste = tile_pos[1] - haut
            col_ajuste = tile_pos[0] - gauche
            
            x = col_ajuste * TAILLE_CASES
            y = lig_ajuste * TAILLE_CASES
            
            if tile.has_water:
                couche['eau'][(x,y)] = tile.get_water()
                
            if tile.has_terrain:
                couche['terrain'][(x,y)] = tile.get_terrain() if tile.get_terrain() in self.cases_terrain else 'X'
            
            if tile.coin:
                couche['piece'][(x + TAILLE_CASES // 2,y + TAILLE_CASES // 2)] = tile.coin
            
            if tile.enemy:
                couche['ennemie'][(x,y)] = tile.enemy
                
            if tile.objects:
                for obj, offset in tile.objects:
                    if obj in [key for key, value in EDITOR_DATA.items() if value['style'] == 'arbre bg']: #arriere plan
                        couche['arbre bg'][int((x + offset.x),int(y + offset.y))] = obj
                    else:
                        couche['objets fg'][int(x + offset.x),int(y + offset.y)] = obj #premier plan
        return couche
                    
    def boucle_evenement(self):
        """_summary_
        la boucle evenement sert a gerer tous ce qui est interaction entre le joueur et l'editeur
        """
        #ferme le jeu
        self.image_options = pygame.image.load('Graphique/Options/roue_crante.png').convert_alpha()
        self.display_surface.blit(self.image_options, [LARGEUR_FENETRE - 175, -100])
        self.retour_menu = pygame.draw.rect(self.display_surface, 'white', pygame.Rect(LARGEUR_FENETRE - 147, ((HAUTEUR_FENETRE/2)+143), 103, 27))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch(self.create_grid())
                self.editor_music.stop()
            if event.type == pygame.MOUSEBUTTONDOWN and self.retour_menu.collidepoint(position_souris()):
                self.selection_bruit.play()
                self.retour_menu = True
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect_options.collidepoint(position_souris()):
                    self.a = 0
                
            while self.a == 0:
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
                            self.a = 1
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
                    self.musique_volume = self.musique_volume
                    self.changer_volume(self.musique_volume)
                    pygame.display.update()
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            self.objet_drag(event)
            self.canvas_add()
            self.canvas_remove()
            self.creation_nuages(event)
    
    def souris_sur_objets(self):
        """_summary_
        la fonction souris_sur_objets nous permet de savoir si la souris passe au dessus d'un objet dans l'editeur afin de pouvoir
        par la suite dessiner un petit rectangle de selection autour de l'objet pour montrer qu'il est selectionnable
        Returns:
            _type_: la fonction return l'objet l'objet survoler
        """
        for sprite in self.canvas_objets:
            if sprite.rect.collidepoint(position_souris()):
                return sprite
            
    def pan_input(self, event):
        """_summary_
        la fonction pan_input permet de faire bouger tous l'editeur en maintement un clique molette. On peut egalement en faisant rouler
        la molette bouger de gauche a doite ou de haut en bas en maintenant en meme temps LCTRL
        Args:
            event (_type_): la fonction prend en entrer les evenements de la fenetre afin de savoir si la clique molette est actif
        """
        #clique molette appuye / relache
        if event.type == pygame.MOUSEBUTTONDOWN and boutons_souris()[1]:
            self.pan_active = True
            self.pan_offset = vector(position_souris()) - self.origin
        if not boutons_souris()[1]:
            self.pan_active = False
        if event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * 50
            else:
                self.origin.x -= event.y * 50
            for sprite in self.canvas_objets:
                sprite.pan_pos(self.origin)
            
            
        #panning mise a jour
        if self.pan_active:
            self.origin = vector(position_souris()) - self.pan_offset
            
            for sprite in self.canvas_objets:
                sprite.pan_pos(self.origin)
    
    def selection_hotkeys(self, event):
        """_summary_
        la fonction selection_hotkeys permet de selectionnner dans le menu la case souhaite. Dans le fichier parametres, on a crée
        un dictionnaire avec des numéros d'identification allant de 2 a 18 pour les blocs pouvant etre posés. Cette fonction permet
        de mettre a jour le menu de l'éditeur afin d'avoir acces a tous les blocs

        Args:
            event (_type_): la fonction prend en entrée les events de la fenetres afin de savoir si le joueur a des interactions avec
            le menu
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selection_index += 1
            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
        self.selection_index = max(2,min(self.selection_index, 18))
    
    def menu_click(self, event):
        """_summary_
        la fonciton menu_click nous sert a savoir si le joueur clique sur le menu

        Args:
            event (_type_): la fonction prend en entrée les events de la fenetres afin de savoir si le joueur clique sur le menu
        """
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(position_souris()):
            new_index = self.menu.click(position_souris(), boutons_souris())  
            self.selection_index = new_index if new_index else self.selection_index  
    
    def canvas_add(self):
        """_summary_
        la fonction canvas_add a pour but de gerer l'ajout de cases dans l'editeur. Cette fonction va crée un id pour pouvoir identifier
        la case posé rajouté cette case dans le dictionnaire contenant les autres cases du meme types. Si cette case est un terrain
        ou de l'eau, alors on apelle la fonction trouver voisins pour mettre a jour automatiquement les bonnes textures. Si 
        cette case est un objet on lance un timer afin de ne pas poser en boucle des objets.
        """
        if boutons_souris()[0] and not self.menu.rect.collidepoint(position_souris()) and not self.objet_drag_active:
            cellule_actuelle = self.cellule_actuelle()
            if EDITOR_DATA[self.selection_index]['type'] == 'tile':
                
                if cellule_actuelle != self.derniere_cellule_selectionne:

                    if cellule_actuelle in self.canvas_data:
                        self.canvas_data[cellule_actuelle].add_id(self.selection_index)
                    else:
                        self.canvas_data[cellule_actuelle] = CanvasTile(self.selection_index)
            
                    self.trouver_voisins(cellule_actuelle)
                    self.derniere_cellule_selectionne = cellule_actuelle
            else:
                groups = [self.canvas_objets, self.background] if EDITOR_DATA[self.selection_index]['style'] == 'arbre bg' else [self.canvas_objets, self.foreground]
                if not self.object_timer.active:
                    CanvasObject(
                        pos = position_souris(),
                        frames = self.animations[self.selection_index]['frames'],
                        tile_id = self.selection_index,
                        origin = self.origin,
                        group = groups)
                    self.object_timer.activate()
                
    
    def canvas_remove(self):
        """_summary_
        la fonction canvas_remove a pour but de suprimer un case. Pour cela si l'on fait clique droit sur une case du meme type que la
        case actuellement selectionnée dans le menu (afin de ne pas supprimer des terrain en enlevant des arbres par exemple) la case
        est supprimé est si celle ci possédait en id on apelle la fonction remove id afin de la supprimer et on rapelle trouver voisins
        pour encore une fois remettre a jour le niveau
        """
        if boutons_souris()[2] and not self.menu.rect.collidepoint(position_souris()):
            
            #objets
            selected_object = self.souris_sur_objets()
            if selected_object:
                if EDITOR_DATA[selected_object.tile_id]['style'] not in ('personnage', 'ciel'):
                    selected_object.kill()
            
            #cases
            if self.canvas_data:
                current_cell = self.cellule_actuelle()
                if current_cell in self.canvas_data:
                    self.canvas_data[current_cell].remove_id(self.selection_index)

                    if self.canvas_data[current_cell].is_empty:
                        del self.canvas_data[current_cell]
                    self.trouver_voisins(current_cell)
    
    def objet_drag(self, event):
        """_summary_
        la fonction objet_drag a pour but de faire bouger les objets lors que l'on fait clique gauche dessus

        Args:
            event (_type_): la fonction prend en entrée les events de la fenetre afin de savoir si le joueur clique dessus.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and boutons_souris()[0]:
            for sprite in self.canvas_objets:
                if sprite.rect.collidepoint(event.pos):
                    sprite.start_drag()
                    self.objet_drag_active = True
        if event.type == pygame.MOUSEBUTTONUP and self.objet_drag_active:
            for sprite in self.canvas_objets:
                if sprite.selected:
                    sprite.drag_end(self.origin)
                    self.objet_drag_active = False
    
    def preview(self):
        """_summary_
        la fonction preview a pour objectif de faire aparraitre un image de la case que nous allons placer légerement transparente.
        """
        #dessiner des lignes autour des objets quand on passe dessus
        objets_selectionne = self.souris_sur_objets()
        if not self.menu.rect.collidepoint(position_souris()):
            if objets_selectionne:
                rect = objets_selectionne.rect.inflate(10,10)
                couleur ='black'
                largeur = 3
                taille = 15
                
                #en haut a gauche
                pygame.draw.lines(self.display_surface, couleur, False, ((rect.left,rect.top + taille), rect.topleft, (rect.left + taille,rect.top)), largeur)
                #en haut a droite
                pygame.draw.lines(self.display_surface, couleur, False, ((rect.right - taille,rect.top), rect.topright, (rect.right,rect.top + taille)), largeur)
                #en bas a droite
                pygame.draw.lines(self.display_surface, couleur, False, ((rect.right - taille,rect.bottom), rect.bottomright, (rect.right,rect.bottom - taille)), largeur)
                #en bas a gauche
                pygame.draw.lines(self.display_surface, couleur, False, ((rect.left,rect.bottom - taille), rect.bottomleft, (rect.left + taille,rect.bottom)), largeur)
                
            else:
                #previsualisation des cases et objets
                type_dict = {key: value['type'] for key, value in EDITOR_DATA.items()}
                surf = self.preview_surfs[self.selection_index].copy()
                surf.set_alpha(200)
                
                #cases
                if type_dict[self.selection_index] == 'tile':
                    current_cell = self.cellule_actuelle()
                    rect = surf.get_rect(topleft = self.origin + vector(current_cell) * TAILLE_CASES)
                #objets
                else:
                    rect = surf.get_rect(center = position_souris())
                
                self.display_surface.blit(surf, rect)
                
    def display_sky(self, dt):
        """_summary_
        la fonction display_sky gere l'affichage du ciel dans l'éditeur
        Args:
            dt (_type_): dt est un nombre permettant de gerer le taux de raffraichissement des nuages
        """
        self.display_surface.fill(COULEUR_CIEL)        
        y = self.sky_handle.rect.centery
        
        #lignes d'horizon
        if y > 0:
            horizon_rect1 = pygame.Rect(0,y - 10,LARGEUR_FENETRE,10)
            horizon_rect2 = pygame.Rect(0,y - 16,LARGEUR_FENETRE,4)
            horizon_rect3 = pygame.Rect(0,y - 20,LARGEUR_FENETRE,2)
            pygame.draw.rect(self.display_surface, COULEUR_DESSUS_HORIZON, horizon_rect1)
            pygame.draw.rect(self.display_surface, COULEUR_DESSUS_HORIZON, horizon_rect2)
            pygame.draw.rect(self.display_surface, COULEUR_DESSUS_HORIZON, horizon_rect3)
        
            self.afficher_nuages(dt, y)
        
        #mer
        if 0 < y < HAUTEUR_FENETRE:
            mer_rect = pygame.Rect(0,y,LARGEUR_FENETRE,HAUTEUR_FENETRE)
            pygame.draw.rect(self.display_surface, COULEUR_MER, mer_rect)
            pygame.draw.line(self.display_surface, COULEUR_HORIZON, (0,y), (LARGEUR_FENETRE,y),3)
            
        if y < 0:
            self.display_surface.fill(COULEUR_MER)
    
    def afficher_nuages(self, dt, horizon_y):
        """_summary_
        la fonction afficher nuages gere l'affichage des nuages de maniere aléatoire
        Args:
            dt (_type_): dt gere la frequence de rafraichissement
            horizon_y (_type_): horizon_y est la ligne d'horizon entre la mer et le ciel afin de ne pas afficher des nuages dans la mer
        """
        for cloud in self.current_clouds:
            cloud['pos'][0] -= cloud['speed'] * dt
            x = cloud['pos'][0]
            y = horizon_y - cloud['pos'][1]
            self.display_surface.blit(cloud['surf'], (x,y))
    
    def creation_nuages(self, event):
        """_summary_
        la fonction création nuages crée des nuages parmi 3 types de nuages en gérant de maniere aléatoire leurs tailles et positions.

        Args:
            event (_type_): _description_
        """
        if event.type == self.cloud_timer:
            surf = choice(self.cloud_surf)
            surf = pygame.transform.scale2x(surf) if randint(0, 4) < 2 else surf
            
            pos = [LARGEUR_FENETRE + randint(50,100),randint(0,HAUTEUR_FENETRE)]
            self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': randint(20,50)})
            
            #supprimer nuages
            self.current_clouds = [cloud for cloud in self.current_clouds if cloud['pos'][0] > -400]
    
    def startup_clouds(self):
        """_summary_
        la fonction startup_clouds se charge de crée un nombre aléatoire de nuages directement positionner dans l'éditeur afin de
        ne pas avoir un ciel vide en attendant que les autres nuages arrivent
        """
        for i in range(20):
            surf = pygame.transform.scale2x(choice(self.cloud_surf)) if randint(0,4) < 2 else choice(self.cloud_surf)
            pos = [randint(0, LARGEUR_FENETRE), randint(0, HAUTEUR_FENETRE)]
            self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': randint(20,50)})
    
    def draw_level(self):
        """_summary_
        la fonction draw_level gere l'affichage de presque tous les élements du niveau
        """
        self.background.draw(self.display_surface)
        for cell_pos, tile in self.canvas_data.items():
            pos = self.origin + vector(cell_pos) * TAILLE_CASES

            # water
            if tile.has_water:
                if tile.water_on_top:
                    self.display_surface.blit(self.bas_eau, pos)
                else:
                    frames = self.animations[3]['frames']
                    index = int(self.animations[3]['frame index'])
                    surf = frames[index]
                    self.display_surface.blit(surf, pos)

            if tile.has_terrain:
                terrain_string = ''.join(tile.cases_terrain)
                terrain_style = terrain_string if terrain_string in self.cases_terrain else 'X'
                self.display_surface.blit(self.cases_terrain[terrain_style], pos)

            # coins
            if tile.coin:
                frames = self.animations[tile.coin]['frames']
                index = int(self.animations[tile.coin]['frame index'])
                surf = frames[index]
                self.display_surface.blit(surf, pos)

            # enemies
            if tile.enemy:
                frames = self.animations[tile.enemy]['frames']
                index = int(self.animations[tile.enemy]['frame index'])
                surf = frames[index]
                self.display_surface.blit(surf, pos)
        self.foreground.draw(self.display_surface)
    #dessin
    def dessin_cases_lignes(self):
        """_summary_
        cette fonction dessiner le quadrillages du niveau
        """
        colonnes = LARGEUR_FENETRE //TAILLE_CASES
        lignes =HAUTEUR_FENETRE //TAILLE_CASES

        origine_offset = vector(x = self.origin.x - int(self.origin.x / TAILLE_CASES) * TAILLE_CASES,y = self.origin.y - int(self.origin.y / TAILLE_CASES) * TAILLE_CASES)

        self.ligne_de_support_surface.fill('green')

        for col in range(colonnes + 1):
            x = origine_offset.x + col * TAILLE_CASES
            pygame.draw.line(self.ligne_de_support_surface, COULEUR_LIGNE, (x,0), (x,HAUTEUR_FENETRE)) 
        
        for lig in range(lignes + 1):
            y = origine_offset.y + lig * TAILLE_CASES
            pygame.draw.line(self.ligne_de_support_surface, COULEUR_LIGNE, (0,y), (LARGEUR_FENETRE,y))
                      
        self.display_surface.blit(self.ligne_de_support_surface,(0,0))
        
    def lancement(self, dt):
        """_summary_
        la fonction lancement est la fonction qui tourne en boucle lorsque l'éditeur est lancé.
        Args:
            dt (_type_): dt gere la fréquence de rafrachissement de l'éditeur.
        """
        self.image1 = pygame.image.load('Graphique/game_over/menuditeur.png').convert_alpha()
        
        #mise a jour
        self.animation_uptade(dt)
        self.canvas_objets.update(dt)
        self.object_timer.uptade()
        #dessin
        self.display_surface.fill('gray')
        self.display_sky(dt)
        self.dessin_cases_lignes()
        self.draw_level()
        #pygame.draw.circle(self.display_surface, 'red', self.origin, 10)
        self.preview()
        self.menu.afficher(self.selection_index)
        self.boucle_evenement()
        self.display_surface.blit(self.image1, (LARGEUR_FENETRE - 172,((HAUTEUR_FENETRE/2)+130)))
            
class CanvasTile:
    """_summary_
    la class CanvasTile est la classe qui permet de gérer la création de cases
    """
    def __init__(self, tile_id, offset = vector()):

        # terrain
        self.has_terrain = False
        self.terrain_neighbors = []

        # water
        self.has_water = False
        self.water_on_top = False

        # coin
        self.coin = None

        # enemy
        self.enemy = None

        # objects
        self.objects = []

        self.add_id(tile_id, offset = offset)
        self.is_empty = False

    def add_id(self, tile_id, offset = vector()):
        """_summary_
        la fonction add_id a pour but de donner un id a une case pour savoir si c'est un terrain une piece etc...

        Args:
            tile_id (_type_): tile_id regroupe tous les types de cases existant.
            offset (_type_, optional): offset est la position de la case par rapport a l'origine. Defaults to vector().
        """
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = True
            case 'eau': self.has_water = True
            case 'piece': self.coin = tile_id
            case 'ennemie': self.enemy = tile_id
            case _:
                if (tile_id, offset) not in self.objects:
                    self.objects.append((tile_id, offset))
            
    def remove_id(self, tile_id):
        """_summary_
        la fonction remove_id est l'inverse de add_id
        Args:
            tile_id (_type_): _description_
        """
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = False
            case 'eau': self.has_water = False
            case 'piece': self.coin = None
            case 'ennemie': self.enemy = None
        self.verifier_contenue()
    
    def verifier_contenue(self):
        """_summary_
        la fonction verifier_contenue verifie si une case est vide
        """
        if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
            self.is_empty = True
        
    def get_water(self):
        """_summary_
        la fonction get_water recupere le nom d'une case etant de l'eau pour savoir si elle est au top au en dessous
        Returns:
            _type_: la fonction retourne le type d'eau
        """
        return 'bottom' if self.water_on_top else 'top'    
    
    def get_terrain(self):
        """_summary_
        la fonction get_terrain retourne le nom de l'image de la case terrain
        Returns:
            _type_: retourne une valeur de type AEF.
        """
        return ''.join(self.cases_terrain)
    
class CanvasObject(pygame.sprite.Sprite):
    """_summary_
    la class CanvasObject permet de gerer la créaction d'objets
    """
    def __init__(self, pos, frames, tile_id, origin, group):
        super().__init__(group)
        self.tile_id = tile_id
        
        #animation
        self.frames = frames
        self.frame_index = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        #mouvement
        self.distance_to_origin = vector(self.rect.topleft) - origin
        self.selected = False
        self.mouse_offset = vector()
        
    def start_drag(self):
        """_summary_
        la fonction start_drag permet de faire bouger un objet.
        """
        self.selected = True
        self.mouse_offset = vector(position_souris()) - vector(self.rect.topleft)
        
    def drag(self):
        """_summary_
        la fonction drag vient en complement de la fonciton start_drag pour permettre de mettre a jour la position de l'objet
        """
        if self.selected:
            self.rect.topleft = position_souris() - self.mouse_offset
    
    def drag_end(self, origin):
        """_summary_
        la fonciton drag_end permet de mettre fin au deplacement de l'objet
        Args:
            origin (_type_): origine du niveau
        """
        self.selected = False
        self.distance_to_origin = vector(self.rect.topleft) - origin
    def animate(self, dt):
        """_summary_
        la fonciton animate permet d'animer les objets en faisant tourner les images importées
        Args:
            dt (_type_): permet de gerer la frequence de rafraichissement de l'animation
        """
        self.frame_index += (VITESSE_ANIMATION * dt) / 1.5
        self.frame_index = 0 if self.frame_index >= len(self.frames) else self.frame_index
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
    
    def pan_pos(self, origin):
        """_summary_
        la foncition pan_pos permet de recuperer le position de la souris quand le clique molette est actif
        Args:
            origin (_type_): origin du niveau
        """
        self.rect.topleft = origin + self.distance_to_origin
    
    def update(self, dt):
        """_summary_
        la fonction update permet de mettre a jour les animations des objets et les deplacement lors de la selection
        Args:
            dt (_type_): _description_
        """
        self.animate(dt)
        self.drag()