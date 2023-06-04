import pygame
from os import walk
from csv import reader
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
