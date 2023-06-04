import pygame
from os import walk
from csv import reader
from parametres import TAILLE_CASES

def import_folder(path):
    surface_list = []

    for folder_name, sub_folders, img_files in walk(path):
        for image_name in img_files:
            full_path = path + '/' + image_name
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list

def import_folder_dict(path):
    surface_dict = {}

    for folder_name, sub_folders, img_files in walk(path):
        for image_name in img_files:
            full_path = path + '/' + image_name
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image_name.split('.')[0]] = image_surf
            
    return surface_dict

def import_csv_layout(path):
    terrain_map = []
    with open(path) as  map:
        level = reader(map, delimiter = ',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map
    
def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / TAILLE_CASES)
    tile_num_y = int(surface.get_size()[1] / TAILLE_CASES)
    
    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * TAILLE_CASES
            y = row * TAILLE_CASES
            new_surface = pygame.Surface((TAILLE_CASES, TAILLE_CASES))
            new_surface.blit(surface,(0,0),pygame.Rect(x, y, TAILLE_CASES,TAILLE_CASES))
            cut_tiles.append(new_surface)
            
    return cut_tiles