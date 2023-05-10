#parametres généraux
TAILLE_CASES = 64
LARGEUR_FENETRE = 1280
HAUTEUR_FENETRE = 720
VITESSE_ANIMATION = 8
COULEUR_LIGNE = 'black'

EDITOR_DATA = {
    1: {'style': 'ciel', 'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': None},
    
    2: {'style': 'terrain', 'type': 'tile', 'menu': 'terrain', 'menu_surf': 'Graphique/Terrain/terrain.png', 'preview': 'Graphique/Preview/terrain.png', 'graphics': None},
    3: {'style': 'eau', 'type': 'tile', 'menu': 'terrain', 'menu_surf': 'Graphique/Eau/eau.png', 'preview': 'Graphique/Preview/eau.png', 'graphics': None},
    
    4: {'style': 'piece', 'type': 'tile', 'menu': 'piece', 'menu_surf': 'Graphique/Piece/gold.png', 'preview': 'Graphique/Preview/gold.png', 'graphics': None},
    5: {'style': 'piece', 'type': 'tile', 'menu': 'piece', 'menu_surf': 'Graphique/Piece/silver.png', 'preview': 'Graphique/Preview/silver.png', 'graphics': None},
    6: {'style': 'piece', 'type': 'tile', 'menu': 'piece', 'menu_surf': 'Graphique/Piece/diamond.png', 'preview': 'Graphique/Preview/diamond.png', 'graphics': None},
    
    7: {'style': 'ennemie', 'type': 'tile', 'menu': 'ennemie', 'menu_surf': 'Graphique/Ennemie/ennemie.png', 'preview': 'Graphique/Preview/ennemie.png', 'graphics': None},
    8: {'style': 'ennemie', 'type': 'tile', 'menu': 'ennemie', 'menu_surf': 'Graphique/Ennemie/ennemie2.png', 'preview': 'Graphique/Preview/ennemie2.png', 'graphics': None},
        
    9: {'style': 'arbre', 'type': 'tile', 'menu': 'arbre fg', 'menu_surf': 'Graphique/Arbre/arbre1.png', 'preview': 'Graphique/Preview/arbre1.png', 'graphics': None},
    10: {'style': 'arbre', 'type': 'tile', 'menu': 'arbre fg', 'menu_surf': 'Graphique/Arbre/arbre2.png', 'preview': 'Graphique/Preview/arbre2.png', 'graphics': None},
    11: {'style': 'arbre', 'type': 'tile', 'menu': 'arbre fg', 'menu_surf': 'Graphique/Arbre/arbre3.png', 'preview': 'Graphique/Preview/arbre3.png', 'graphics': None},
    
    12: {'style': 'arbre', 'type': 'tile', 'menu': 'arbre bg', 'menu_surf': 'Graphique/Arbre/arbre1bg.png', 'preview': 'Graphique/Preview/arbre1bg.png', 'graphics': None},
    13: {'style': 'arbre', 'type': 'tile', 'menu': 'arbre bg', 'menu_surf': 'Graphique/Arbre/arbre2bg.png', 'preview': 'Graphique/Preview/arbre2bg.png', 'graphics': None},
    14: {'style': 'arbre', 'type': 'tile', 'menu': 'arbre bg', 'menu_surf': 'Graphique/Arbre/arbre3bg.png', 'preview': 'Graphique/Preview/arbre3bg.png', 'graphics': None}
}

# colors
COULEUR_CIEL = '#ddc6a1'
COULEUR_MER = '#92a9cd'
COULEUR_HORIZON = '#f5f1de'
COULEUR_DESSUS_HORIZON = '#d1aa9d'
COULEUR_BG_BOUTON = '#33323d'
COULEUR_BOUTON_LIGNE = '#f5f1de'

DIRECTION_VOISINS = {
	'A': (0,-1),
	'B': (1,-1),
	'C': (1,0),
	'D': (1,1),
	'E': (0,1),
	'F': (-1,1),
	'G': (-1,0),
	'H': (-1,-1)
}

LEVEL_LAYERS = {
	'clouds': 1,
	'ocean': 2,
	'bg': 3,
	'water': 4,
	'main': 5
}