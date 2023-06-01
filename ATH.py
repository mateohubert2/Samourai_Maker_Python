import pygame

class ATH:
    def __init__(self,surface):

        #position
        self.display_surface = surface

        #vie
        self.barre_vie = pygame.image.load('Graphique/ATH/barre_vie.png')
        self.barre_vie_topleft = (54,39)
        self.longeur_max_barre = 152
        self.hauteur_barre = 4

        #piece
        self.piece = pygame.image.load('Graphique/Piece/silver.png')
        self.piece_rect = self.piece.get_rect(topleft = (50,61))
        self.police = pygame.font.Font('Graphique/ATH/ARCADEPI.TTF',30)
    
    def barre_de_vie(self, actuelle, full):
        """_summary_
        le but de cette fonction est d'afficher une barre de vie et de convertir le nombre de pixel pour avoir une vie max=100
        Args:
            actuelle (_type_): _description_
            full (_type_): _description_
        """
        self.display_surface.blit(self.barre_vie,(20,10))
        vie_actuelle_ratio = actuelle / full 
        vie_actuelle_longueur = self.longeur_max_barre * vie_actuelle_ratio
        barre_vie_rect = pygame.Rect(self.barre_vie_topleft,( vie_actuelle_longueur,self.hauteur_barre))
        pygame.draw.rect(self.display_surface,'#dc4949',barre_vie_rect)
        
    def nombre_piece(self, nombre):
        """_summary_
        le but de cette fonction est d'afficher le nombre de piece et une piece à coté
        Args:
            nombre (_type_): _description_
        """
        self.display_surface.blit(self.piece, self.piece_rect)
        nombre_piece_surface = self.police.render(str(nombre),False,'#33323d')
        nombre_piece_rect = nombre_piece_surface.get_rect(midleft =(self.piece_rect.right + 4,self.piece_rect.centery))
        self.display_surface.blit(nombre_piece_surface,nombre_piece_rect)
                                                          
