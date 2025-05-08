import pygame
import math
import random
from settings import *

class World:
    def __init__(self):
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,2,0,0,1,0,0,0,1,0,0,0,1,0,0,1],
            [1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,1],
            [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1],
            [1,1,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,1,1,0,1,1,0,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,0,1,1,0,1,1,1,3,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        self.cell_size = 50
        self.wall_color = (80, 80, 100)
        self.wall_highlight = (110, 110, 130)
        self.floor_color = (25, 25, 35)
        self.floor_highlight = (45, 45, 55)
        self.start_color = GREEN
        self.end_color = BLUE

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
                    pygame.draw.rect(surface, self.wall_highlight, rect.inflate(-5, -5), 2)
                elif tile == 2:
                    pygame.draw.rect(surface, self.floor_color, rect)
                    pygame.draw.circle(surface, self.start_color, rect.center, 10)
                elif tile == 3:
                    pygame.draw.rect(surface, self.floor_color, rect)
                    pygame.draw.circle(surface, self.end_color, rect.center, 10)
                else:
                    pygame.draw.rect(surface, self.floor_color, rect)
                    if (x + y) % 3 == 0:
                        pygame.draw.rect(surface, self.floor_highlight, rect.inflate(-40, -40))

    def get_start_position(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == 2:
                    return (x * self.cell_size + self.cell_size//2,
                            y * self.cell_size + self.cell_size//2)
        return (self.cell_size, self.cell_size)
    
    def get_end_position(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == 3:
                    return (x * self.cell_size + self.cell_size//2,
                            y * self.cell_size + self.cell_size//2)
        return (len(self.grid[0])*self.cell_size - self.cell_size,
                len(self.grid)*self.cell_size - self.cell_size)

    def is_wall(self, x, y):
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
            return self.grid[grid_y][grid_x] == 1
        return True

    def is_valid_position(self, x, y, radius):
        """تحقق من أن الموقع صالح للكائن بحجم معين"""
        points = [
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius)
        ]
        return not any(self.is_wall(px, py) for px, py in points)

    def has_line_of_sight(self, pos1, pos2):
        steps = max(10, int(math.dist(pos1, pos2)))
        for step in range(1, steps):
            x = pos1[0] + (pos2[0] - pos1[0]) * step/steps
            y = pos1[1] + (pos2[1] - pos1[1]) * step/steps
            if self.is_wall(x, y):
                return False
        return True

    def get_valid_position(self, min_dist=200, exclude_pos=None, max_attempts=100):
        attempts = 0
        radius = PLAYER_SETTINGS['size']
        while attempts < max_attempts:
            x = random.randint(1, len(self.grid[0])-2)
            y = random.randint(1, len(self.grid)-2)
            
            if self.grid[y][x] == 0:
                pos = (x * self.cell_size + self.cell_size//2,
                       y * self.cell_size + self.cell_size//2)
                
                if exclude_pos and math.dist(pos, exclude_pos) < min_dist:
                    attempts += 1
                    continue
                    
                if self.is_valid_position(pos[0], pos[1], radius):
                    return pos
                    
            attempts += 1
        return None

    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.grid[0]) and 0 <= ny < len(self.grid):
                if self.grid[ny][nx] != 1:
                    neighbors.append((nx, ny))
        return neighbors