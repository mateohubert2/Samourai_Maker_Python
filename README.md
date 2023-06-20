# Samourai_Maker_Python

## Introduction:

Ce programme est un jeu de platforme en 2D dans le style de Mario_Maker.
Ce projet a été entierement réalisé en Python dans le cadre d'un projet scolaire à l'ESIREM.

## Prérequis:
Pour executer ce programme, il est nécessaire d'importer la librairie Pygame.

## Inspiration:
 ce projet à été réalisé sur la base d'un tuto:
 
 https://www.youtube.com/watch?v=qYomF9p_SYM&t=2s
 
 Celui-ci nous a permis de maitriser l'outil "pygame". Nous avons par la suite ajouter de nombreuses fonctionnalités au jeu.
 Les musiques et les bruitages sont libres de droits et n'ont pas étés composées par nous.
 
 ## Fonctionnalités ajoutés:
 - Un menu principal avec la possibilité du mode de jeu: Niveau ou Editeur de niveau.
 - La possibilité de retourner au menu principal depuis l'éditeur.
 - Une gestion de fin de jeu (game over) avec un nouveau menu qui permet de rejouer au niveau ou  de retourner au menu principal.
 - Une barre de vie et la gestion de prise de dégat par les enemies avec des effets de recul à chaque dégat subit.
 - Ajout de bruit d'ambiance (Game_over, Victoire, Click dans un menu).
 - La direction artistique à été entierment revu.
 - gestion de la valeur de chaque pièce.
 - Gestion de victoire une fois que toutes les pièces ont étés récuperées. Avec un menu (le même que pour le game over mais légérement modifié)
 - Possibilité de changer le volume en cliquant sur le rouage dans le menu principal

## Comment jouer:

- Déplacements avec Z Q S D.
- Clique droit pour changer de bloc/arbre/pièce/enemies dans le menu en bas à droite de l'éditeur.
- clique molette pour déplacer la caméra dans l'éditeur.
- Les objets tels que le joueur ou les arbres sont deplaçable en faisant clique gauche dessus.
- Pour lancer le niveau que vous venez de creer, il faut appuyer sur "entrez"
- Pour retourner dans l'éditeur lorsque vous jouez, il faut appyer sur "echap"
- La fin du jeu est défini par le fait que toutes les pièces présentes ont étés récuperées, **il est donc impératif de poser au minimum une pièce lors de la création d'un niveau!**
