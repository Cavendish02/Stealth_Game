import pygame
import math
import random
from settings import *
from .utils import distance, angle_between, draw_vision_cone

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = PLAYER_SETTINGS['size'] // 2
        self.speed = PLAYER_SETTINGS['speed']
        self.is_sneaking = False
        self.noise_level = 0
        
    def move(self, keys, world):
        # Calculate movement direction
        dx, dy = 0, 0
        if keys['up']: dy -= 1
        if keys['down']: dy += 1
        if keys['left']: dx -= 1
        if keys['right']: dx += 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        # Calculate speed based on sneaking
        speed = PLAYER_SETTINGS['stealth_speed'] if self.is_sneaking else PLAYER_SETTINGS['speed']
        
        # Calculate new position with collision detection
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed
        
        # Check collision with walls
        if not world.is_wall(new_x - self.radius, self.y):
            self.x = new_x
        if not world.is_wall(self.x, new_y - self.radius):
            self.y = new_y
        
        # Calculate noise level
        self.noise_level = math.sqrt(dx**2 + dy**2) * (1 if self.is_sneaking else 2)
    
    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.radius)

class Guard:
    def __init__(self, x, y, patrol_points):
        self.x, self.y = x, y
        self.radius = PLAYER_SETTINGS['size'] // 2
        self.speed = GUARD_SETTINGS['speed']
        self.state = "patrol"
        self.patrol_points = patrol_points
        self.current_point = 0
        self.path = []
        self.vision_angle = 0
        
    def update(self, player, world):
        # Update vision angle (for cone visualization)
        self.vision_angle = angle_between((self.x, self.y), (player.x, player.y))
        
        if self.state == "patrol":
            self.patrol(world)
            if self.can_see(player, world):
                self.state = "chase"
        
        elif self.state == "chase":
            self.chase(player, world)
            if not self.can_see(player, world):
                self.state = "patrol"
    
    def can_see(self, player, world):
        angle = angle_between((self.x, self.y), (player.x, player.y))
        dist = distance((self.x, self.y), (player.x, player.y))
        
        # Check if in vision cone
        angle_diff = abs((self.vision_angle - angle + 180) % 360 - 180)
        if angle_diff > GUARD_SETTINGS['vision_angle']/2:
            return False
            
        # Check distance
        if dist > GUARD_SETTINGS['vision_distance']:
            return False
            
        # Check for walls
        steps = int(dist)
        for step in range(1, steps):
            check_x = self.x + (player.x - self.x) * step/steps
            check_y = self.y + (player.y - self.y) * step/steps
            if world.is_wall(check_x, check_y):
                return False
                
        return True
    
    def patrol(self, world):
        target_x, target_y = self.patrol_points[self.current_point]
        
        # Move toward target
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += math.cos(angle) * GUARD_SETTINGS['patrol_speed']
        self.y += math.sin(angle) * GUARD_SETTINGS['patrol_speed']
        
        # Check if reached target
        if distance((self.x, self.y), (target_x, target_y)) < 5:
            self.current_point = (self.current_point + 1) % len(self.patrol_points)
    
    def chase(self, player, world):
        # Simple chase behavior - can be replaced with pathfinding
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed
        
        # Basic wall avoidance
        if world.is_wall(self.x, self.y):
            self.x -= math.cos(angle) * self.speed * 2
            self.y -= math.sin(angle) * self.speed * 2
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        
        # Draw vision cone when chasing
        if self.state == "chase":
            draw_vision_cone(
                surface,
                (int(self.x), int(self.y)),
                self.vision_angle,
                GUARD_SETTINGS['vision_distance'],
                GUARD_SETTINGS['vision_angle']
            )