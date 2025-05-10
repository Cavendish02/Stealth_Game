import pygame
from pygame.locals import *

# ===== إعدادات النظام الأساسي =====
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_TITLE = "Shadow Operative"
FONT_NAME = "Arial"
SAVE_FILE = "game_save.dat"

# ===== نظام الألوان =====
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'dark_gray': (40, 40, 50),
    'light_gray': (120, 120, 140),
    'red': (220, 60, 60),
    'dark_red': (180, 40, 40),
    'green': (70, 220, 70),
    'dark_green': (40, 160, 40),
    'blue': (70, 70, 220),
    'dark_blue': (40, 40, 180),
    'yellow': (255, 220, 100),
    'orange': (255, 150, 50),
    'purple': (180, 70, 180),
    'cyan': (70, 220, 220),
    'pink': (220, 70, 220)
}

# اختصارات للألوان الشائعة
DARK_GRAY = COLORS['dark_gray']
GREEN = COLORS['green']
RED = COLORS['red']
WHITE = COLORS['white']
ORANGE = COLORS['orange']
YELLOW = COLORS['yellow']

# ===== عناصر التحكم =====
CONTROLS = {
    'up': [K_UP, K_w],
    'down': [K_DOWN, K_s],
    'left': [K_LEFT, K_a],
    'right': [K_RIGHT, K_d],
    'sneak': [K_LCTRL, K_RCTRL],
    'sprint': [K_LSHIFT, K_RSHIFT],
    'interact': [K_e],
    'inventory': [K_i],
    'pause': [K_ESCAPE],
    'restart': [K_r]
}

# ===== إعدادات اللاعب =====
PLAYER_SETTINGS = {
    'size': 14,
    'speed': {
        'normal': 4.5,
        'sprint': 6.5,
        'sneak': 2.8,
        'crouch': 1.5
    },
    'stamina': {
        'max': 100,
        'sprint_cost': 20,
        'regen_rate': 15
    },
    'noise': {
        'base': 1.0,
        'sprint_multiplier': 2.5,
        'sneak_multiplier': 0.4
    },
    'vision': {
        'normal_radius': 250,
        'sneak_radius': 180
    },
    'health': 100,
    'interaction_range': 60
}

# ===== إعدادات الحراس =====
GUARD_SETTINGS = {
    'size': 16,
    'speed': {
        'patrol': 2.5,
        'alert': 3.8,
        'chase': 5.0,
        'search': 3.0
    },
    'vision': {
        'distance': 280,
        'angle': 85,
        'alert_bonus': 1.3,
        'dark_penalty': 0.7
    },
    'hearing': {
        'normal_range': 160,
        'sprint_range': 220,
        'sneak_range': 80
    },
    'behavior': {
        'min_spawn_distance': 220,  # تأكد من وجود هذا السطر
        'patrol_points': 4,
        'investigation_time': 8,
        'search_time': 12,
        'catch_radius': 35,
        'search_radius': 150,
        'forget_time': 20
    },
    'min_spawn_distance': 220  # أضف هذا السطر كمفتاح رئيسي أيضاً
}

# ===== إعدادات الهدف =====
OBJECTIVE_SETTINGS = {
    'size': 20,
    'pulse_speed': 0.01,
    'glow_radius': 100,
    'collect_radius': 30,
    'color': 'blue'
}

# ===== إعدادات الذكاء الاصطناعي =====
AI_SETTINGS = {
    'pathfinding': {
        'update_interval': 0.4,
        'max_length': 25,
        'smoothing': True,
        'direct_path': True,
        'node_distance': 40,
        'wall_avoidance': 1.5,
        'path_precision': 2,
        'allow_diagonal': True
    },
    'behavior': {
        'reaction_time': 0.3,
        'certainty_threshold': 0.7,
        'search_pattern': 'spiral',
        'cooperation_level': 0.5
    },
    'movement': {
        'min_turn_angle': 15,
        'max_turn_angle': 90,
        'acceleration': 0.1,
        'deceleration': 0.2
    }
}

# ===== إعدادات العالم =====
WORLD_SETTINGS = {
    'cell_size': 64,
    'wall_thickness': 10,
    'lighting': {
        'quality': 2,
        'decay': 0.8,
        'min_alpha': 15,
        'max_alpha': 200
    },
    'shadows': {
        'enabled': True,
        'resolution': 1,
        'softness': 2
    }
}

# ===== إعدادات الصوت =====
SOUND_SETTINGS = {
    'volume': {
        'master': 0.8,
        'music': 0.6,
        'effects': 0.9,
        'voice': 0.7
    },
    'distances': {
        'footsteps': 200,
        'gunshot': 1000,
        'alert': 500,
        'whisper': 100
    }
}

# ===== إعدادات التصحيح =====
DEBUG_SETTINGS = {
    'visible': {
        'collision': False,
        'paths': False,
        'vision': False,
        'fps': True
    },
    'console': {
        'enabled': True,
        'max_lines': 20
    }
}

# ===== مستويات الصعوبة =====
DIFFICULTY_LEVELS = {
    'easy': {
        'guard_vision': 0.8,
        'guard_hearing': 0.7,
        'player_speed': 1.1,
        'stamina_regen': 1.2
    },
    'normal': {
        'guard_vision': 1.0,
        'guard_hearing': 1.0,
        'player_speed': 1.0,
        'stamina_regen': 1.0
    },
    'hard': {
        'guard_vision': 1.3,
        'guard_hearing': 1.2,
        'player_speed': 0.9,
        'stamina_regen': 0.8
    }
}

def get_color(name, alpha=None):
    """الحصول على لون مع شفافية اختيارية"""
    color = COLORS.get(name, COLORS['white'])
    if alpha is not None:
        return (*color[:3], alpha)
    return color

def load_fonts():
    """تحميل خطوط اللعبة"""
    try:
        fonts = {
            'small': pygame.font.SysFont(FONT_NAME, 20),
            'medium': pygame.font.SysFont(FONT_NAME, 28),
            'large': pygame.font.SysFont(FONT_NAME, 36),
            'title': pygame.font.SysFont(FONT_NAME, 48, bold=True)
        }
        return fonts
    except:
        return pygame.font.get_default_font()