import pygame
import math
from settings import *

def draw_vision_cone(surface, pos, angle, distance, angle_width):
    """رسم مخروط الرؤية للحارس"""
    half_angle = angle_width / 2
    points = [pos]
    for i in range(int(-half_angle), int(half_angle) + 1):
        rad = math.radians(angle + i)
        end_x = pos[0] + distance * math.cos(rad)
        end_y = pos[1] + distance * math.sin(rad)
        points.append((end_x, end_y))
    
    # إنشاء سطح شفاف لرسم المخروط
    cone_surface = pygame.Surface((distance*2, distance*2), pygame.SRCALPHA)
    pygame.draw.polygon(cone_surface, (*YELLOW, 100),
                       [(p[0]-pos[0]+distance, p[1]-pos[1]+distance) for p in points])
    surface.blit(cone_surface, (pos[0]-distance, pos[1]-distance))

def distance(p1, p2):
    """حساب المسافة بين نقطتين"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def angle_between(p1, p2):
    """حساب الزاوية بين نقطتين"""
    return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))