import pygame
from pygame.math import Vector2 as vector
from parametres import*
from pygame.mouse import get_pressed as boutons_souris
from pygame.mouse import get_pos as position_souris
from pygame.image import load
from menu import Menu
from timer import Timer
from support import*
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
        
        #objets
        self.canvas_objets = pygame.sprite.Group()
        self.objet_drag_active = False
        self.object_timer = Timer(400)
        
        #personnage
        CanvasObject(
            pos = (200, HAUTEUR_FENETRE / 2),
            frames = self.animations[0]['frames'],
            tile_id = 0,
            origin = self.origin,
            group = self.canvas_objets)
        
        #sky
        self.sky_handle = CanvasObject(
            pos = (LARGEUR_FENETRE / 2, HAUTEUR_FENETRE / 2),
            frames = [self.sky_handle_surf],
            tile_id = 1,
            origin = self.origin,
            group = self.canvas_objets
            )
        
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
        for value in self.animations.values():
            value['frame index'] += (VITESSE_ANIMATION * dt) / 1.5
            if value['frame index'] >= value['length']:
                value['frame index'] = 0
        
    def boucle_evenement(self):
        #ferme le jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            self.objet_drag(event)
            self.canvas_add()
            self.canvas_remove()

    def souris_sur_objets(self):
        for sprite in self.canvas_objets:
            if sprite.rect.collidepoint(position_souris()):
                return sprite
            
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
            
            for sprite in self.canvas_objets:
                sprite.pan_pos(self.origin)
    
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
                if not self.object_timer.active:
                    CanvasObject(
                        pos = position_souris(),
                        frames = self.animations[self.selection_index]['frames'],
                        tile_id = self.selection_index,
                        origin = self.origin,
                        group = self.canvas_objets)
                    self.object_timer.activate()
    
    def canvas_remove(self):
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
                
    def draw_level(self):
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
                terrain_string = ''.join(tile.terrain_voisins)
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
        self.canvas_objets.draw(self.display_surface)
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
        #mise a jour
        self.animation_uptade(dt)
        self.canvas_objets.update(dt)
        self.object_timer.uptade()
        #dessin
        self.display_surface.fill('gray')
        self.dessin_cases_lignes()
        self.draw_level()
        pygame.draw.circle(self.display_surface, 'red', self.origin, 10)
        self.preview()
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
        self.is_empty = False

    def add_id(self, tile_id):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = True
            case 'eau': self.has_water = True
            case 'piece': self.coin = tile_id
            case 'ennemie': self.enemy = tile_id
            
    def remove_id(self, tile_id):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = False
            case 'eau': self.has_water = False
            case 'piece': self.coin = None
            case 'ennemie': self.enemy = None
        self.verifier_contenue()
    
    def verifier_contenue(self):
        if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
            self.is_empty = True
            
class CanvasObject(pygame.sprite.Sprite):
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
        self.selected = True
        self.mouse_offset = vector(position_souris()) - vector(self.rect.topleft)
        
    def drag(self):
        if self.selected:
            self.rect.topleft = position_souris() - self.mouse_offset
    
    def drag_end(self, origin):
        self.selected = False
        self.distance_to_origin = vector(self.rect.topleft) - origin
    def animate(self, dt):
        self.frame_index += (VITESSE_ANIMATION * dt) / 1.5
        self.frame_index = 0 if self.frame_index >= len(self.frames) else self.frame_index
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
    
    def pan_pos(self, origin):
        self.rect.topleft = origin + self.distance_to_origin
    
    def update(self, dt):
        self.animate(dt)
        self.drag()