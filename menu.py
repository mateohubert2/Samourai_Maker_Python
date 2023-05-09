import pygame
from parametres import*
from pygame.image import load
class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.creation_donnee()
        self.cree_boutons()
    
    def creation_donnee(self):
        self.menu_surfs = {}
        for key, value in EDITOR_DATA.items():
            if value['menu']:
                if not value['menu'] in self.menu_surfs:
                    self.menu_surfs[value['menu']] = [(key,load(value['menu_surf']))]
                else:
                    self.menu_surfs[value['menu']].append((key, load(value['menu_surf'])))
    
    def cree_boutons(self):
        #zone de menu
        taille = 180
        marge = 6
        coinsuperieur = (LARGEUR_FENETRE - taille - marge, HAUTEUR_FENETRE - taille - marge)
        self.rect = pygame.Rect(coinsuperieur,(taille, taille))
        
        #zone des boutons
        generic_button_rect = pygame.Rect(self.rect.topleft, (self.rect.width / 2, self.rect.height / 2))
        marge_bouton = 5
        self.terrain_rectangle_bouton = generic_button_rect.copy().inflate(-marge_bouton,-marge_bouton)
        self.piece_rectangle_bouton = generic_button_rect.move(self.rect.width / 2, 0).inflate(-marge_bouton,-marge_bouton)
        self.ennemie_rectangle_bouton = generic_button_rect.move(self.rect.width / 2, self.rect.width / 2).inflate(-marge_bouton,-marge_bouton)
        self.arbre_rectangle_bouton = generic_button_rect.move(0,self.rect.width / 2).inflate(-marge_bouton,-marge_bouton)
        
        #creation de boutons
        self.boutons = pygame.sprite.Group()
        Bouton(self.terrain_rectangle_bouton, self.boutons, self.menu_surfs['terrain'])
        Bouton(self.piece_rectangle_bouton, self.boutons, self.menu_surfs['piece'])
        Bouton(self.ennemie_rectangle_bouton, self.boutons, self.menu_surfs['ennemie'])
        Bouton(self.arbre_rectangle_bouton, self.boutons, self.menu_surfs['arbre fg'], self.menu_surfs['arbre bg'])
        
    def click(self, souris_pos, bouton_souris):
        for sprite in self.boutons:
            if sprite.rect.collidepoint(souris_pos):
                if bouton_souris[1]: #molette
                    if sprite.items['alt']:
                        sprite.main_active = not sprite.main_active
                if bouton_souris[2]: #clique droit
                    sprite.switch()
                return sprite.get_id()    
    
    def surbrillance(self, index):
        if EDITOR_DATA[index]['menu'] == 'terrain':
            pygame.draw.rect(self.display_surface, COULEUR_BOUTON_LIGNE, self.terrain_rectangle_bouton.inflate(4,4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'piece':
            pygame.draw.rect(self.display_surface, COULEUR_BOUTON_LIGNE, self.piece_rectangle_bouton.inflate(4,4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'arbre fg':
            pygame.draw.rect(self.display_surface, COULEUR_BOUTON_LIGNE, self.arbre_rectangle_bouton.inflate(4,4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'ennemie':
            pygame.draw.rect(self.display_surface, COULEUR_BOUTON_LIGNE, self.ennemie_rectangle_bouton.inflate(4,4), 5, 4)
             
    def afficher(self, index):
        self.boutons.update()
        self.boutons.draw(self.display_surface)
        self.surbrillance(index)



class Bouton(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, items_alt = None):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect

        # items 
        self.items = {'main': items, 'alt': items_alt}
        self.index = 0
        self.main_active = True
    
    def get_id(self):
        return self.items['main' if self.main_active else 'alt'][self.index][0]    

    def switch(self):
        self.index += 1
        self.index = 0 if self.index >= len(self.items['main' if self.main_active else 'alt']) else self.index

    def update(self):
        self.image.fill(COULEUR_BG_BOUTON)
        surf = self.items['main' if self.main_active else 'alt'][self.index][1]
        rect = surf.get_rect(center = (self.rect.width / 2, self.rect.height / 2))
        self.image.blit(surf, rect)
  
