import pygame
from parametres import*
from pygame.image import load
from support import*

from editeur import Editeur

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        self.clock = pygame.time.Clock()
        self.imports()
        
        self.editeur = Editeur(self.cases_terrain)
    
        #cureur
        surf = load('Graphique/curseur/souris.png').convert_alpha()
        curseur = pygame.cursors.Cursor((0,0), surf)
        pygame.mouse.set_cursor(curseur)
        
    def imports(self):
        self.cases_terrain = import_folder_dict('Graphique/Terrain/Land')  
    
    def lancement(self):
        while True:
            dt = self.clock.tick() / 1000
                    
            self.editeur.lancement(dt)
            pygame.display.update()

if __name__ == '__main__':
    main = Main()
    main.lancement()