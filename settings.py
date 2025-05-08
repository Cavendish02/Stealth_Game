import pygame
from pygame.locals import *

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Stealth Mission Pro"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 70, 70)
GREEN = (70, 255, 70)
BLUE = (70, 70, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 150, 50)
PURPLE = (180, 70, 180)
DARK_GRAY = (30, 30, 40)

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
    'speed': 4.0,
    'size': 12,
    'stealth_speed': 2.0,
    'color': GREEN,
    'max_noise': 3.0,
    'friction': 0.85
}

# Guard settings
GUARD_SETTINGS = {
    'speed': 3.8,
    'chase_speed': 4.5,
    'vision_angle': 70,
    'vision_distance': 220,
    'hearing_distance': 160,
    'patrol_speed': 2.0,
    'alert_duration': 3000,
    'investigation_duration': 5000,
    'color': RED,
    'min_spawn_distance': 200,
    'search_radius': 130,
    'catch_radius': 30,
    'distraction_duration': 5000,
    'investigation_speed': 3.0
}

# Objective settings
OBJECTIVE = {
    'size': 18,
    'color': BLUE,
    'pulse_speed': 0.08
}

# AI settings
AI_SETTINGS = {
    'path_update_interval': 400,
    'min_path_distance': 80,
    'max_path_length': 25,
    'use_direct_path': True,
    'path_smoothing': True
}

# Vision settings
VISION_SETTINGS = {
    'high_quality': True,
    'shadow_quality': 2,
    'light_decay': 0.7
}