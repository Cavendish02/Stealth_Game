import pygame
import random
from settings import *

class World:
    def __init__(self):
        # Improved maze design
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.cell_size = 60
        self.wall_color = GRAY
        self.floor_color = BLACK
        
    def draw(self, surface):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                if tile == 1:
                    pygame.draw.rect(surface, self.wall_color, rect)
                else:
                    pygame.draw.rect(surface, self.floor_color, rect)
    
    def is_wall(self, x, y):
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
            return self.grid[grid_y][grid_x] == 1
        return True
    
    def get_valid_position(self):
        """Get random valid position not in wall"""
        while True:
            x = random.randint(1, len(self.grid[0])-2)
            y = random.randint(1, len(self.grid)-2)
            if self.grid[y][x] == 0:
                return (x * self.cell_size + self.cell_size//2, 
                        y * self.cell_size + self.cell_size//2)