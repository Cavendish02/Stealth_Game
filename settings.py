import pygame
from pygame.locals import *

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_TITLE = "Stealth Game"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Controls
CONTROLS = {
    'up': [K_UP, K_w],
    'down': [K_DOWN, K_s],
    'left': [K_LEFT, K_a],
    'right': [K_RIGHT, K_d],
    'sneak': K_LSHIFT
}

# Player settings
PLAYER_SETTINGS = {
    'speed': 5,
    'size': 20,
    'stealth_speed': 2.5
}

# Guard settings
GUARD_SETTINGS = {
    'speed': 3,
    'vision_angle': 90,
    'vision_distance': 300,
    'hearing_distance': 200,
    'patrol_speed': 2
}