import pygame

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.active = False
        self.start_time = 0
        
    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
    def desactive(self):
        self.active = False
        self.start_time = 0
    
    def uptade(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.desactive()