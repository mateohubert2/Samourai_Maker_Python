import pygame
from pygame.math import Vector2 as vector
from parametres import*
from pygame.mouse import get_pressed as boutons_souris
from pygame.mouse import get_pos as position_souris
from pygame.image import load
from menu import Menu
import sys
class Editeur:
    def __init__(self, cases_terrain):
        #description du main
        self.display_surface = pygame.display.get_surface()
        self.canvas_data = {}
        
        self.cases_terrain = cases_terrain
        self.imports()
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
        
    def cellule_actuelle(self):
        distance_de_origine = vector(position_souris()) - self.origin

        if distance_de_origine.x > 0:
            col = int(distance_de_origine.x / TAILLE_CASES)
        else:
            col = int(distance_de_origine.x / TAILLE_CASES) - 1

        if distance_de_origine.y > 0:
            lig = int(distance_de_origine.y / TAILLE_CASES)
        else:
            lig = int(distance_de_origine.y / TAILLE_CASES) - 1

        return col, lig    
    
    def trouver_voisins(self, cell_pos):

        # create a local cluster
        taille_cluster = 3
        cluster_local = [
            (cell_pos[0] + col - int(taille_cluster / 2), cell_pos[1] + lig - int(taille_cluster / 2)) 
            for col in range(taille_cluster) 
            for lig in range(taille_cluster)]

            # check neighbors
        for cell in cluster_local:
                if cell in self.canvas_data:
                    self.canvas_data[cell].terrain_voisins = []
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
                                    self.canvas_data[cell].terrain_voisins.append(name)
    
    def imports(self):
        self.bas_eau = load("Graphique/Eau/eau.png")
    
    def boucle_evenement(self):
        #ferme le jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            self.canvas_add()
            
    def pan_input(self, event):
        
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
            
        #panning mise a jour
        if self.pan_active:
            self.origin = vector(position_souris()) - self.pan_offset
    
    def selection_hotkeys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selection_index += 1
            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
        self.selection_index = max(2,min(self.selection_index, 18))
    
    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(position_souris()):
          self.selection_index = self.menu.click(position_souris(), boutons_souris())  
    
    def canvas_add(self):
        if boutons_souris()[0] and not self.menu.rect.collidepoint(position_souris()):
            cellule_actuelle = self.cellule_actuelle()

            if cellule_actuelle != self.derniere_cellule_selectionne:

                if cellule_actuelle in self.canvas_data:
                    self.canvas_data[cellule_actuelle].add_id(self.selection_index)
                else:
                    self.canvas_data[cellule_actuelle] = CanvasTile(self.selection_index)
        
                self.trouver_voisins(cellule_actuelle)
                self.derniere_cellule_selectionne = cellule_actuelle
    
    def draw_level(self):
        for cell_pos, tile in self.canvas_data.items():
            pos = self.origin + vector(cell_pos) * TAILLE_CASES

            # water
            if tile.has_water:
                if tile.water_on_top:
                    self.display_surface.blit(self.bas_eau, pos)
                else:
                    test_surf = pygame.Surface((TAILLE_CASES, TAILLE_CASES))
                    test_surf.fill('red')
                    self.display_surface.blit(test_surf, pos)

            if tile.has_terrain:
                terrain_string = ''.join(tile.terrain_voisins)
                terrain_style = terrain_string if terrain_string in self.cases_terrain else 'X'
                self.display_surface.blit(self.cases_terrain[terrain_style], pos)

            # coins
            if tile.coin:
                test_surf = pygame.Surface((TAILLE_CASES, TAILLE_CASES))
                test_surf.fill('yellow')
                self.display_surface.blit(test_surf, pos)

            # enemies
            if tile.enemy:
                test_surf = pygame.Surface((TAILLE_CASES, TAILLE_CASES))
                test_surf.fill('red')
                self.display_surface.blit(test_surf, pos)
    #dessin
    def dessin_cases_lignes(self):
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
        self.boucle_evenement()
        
        self.display_surface.fill('gray')
        self.dessin_cases_lignes()
        self.draw_level()
        pygame.draw.circle(self.display_surface, 'red', self.origin, 10)
        self.menu.afficher(self.selection_index)
        
class CanvasTile:
    def __init__(self, tile_id):

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

        self.add_id(tile_id)

    def add_id(self, tile_id):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = True
            case 'eau': self.has_water = True
            case 'piece': self.coin = tile_id
            case 'ennemie': self.enemy = tile_id