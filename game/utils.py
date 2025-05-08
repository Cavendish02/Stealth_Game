import pygame
import math
from settings import *

def draw_vision_cone(surface, pos, angle, distance, angle_width, color=None):
    if color is None:
        color = (*YELLOW, 80)
    
    half_angle = angle_width / 2
    points = [pos]
    
    steps = int(angle_width // 5) + 1
    for i in range(steps):
        current_angle = -half_angle + (i * angle_width / steps)
        rad = math.radians(angle + current_angle)
        end_x = pos[0] + distance * math.cos(rad)
        end_y = pos[1] + distance * math.sin(rad)
        points.append((end_x, end_y))
    
    cone_surface = pygame.Surface((distance*2, distance*2), pygame.SRCALPHA)
    pygame.draw.polygon(cone_surface, color,
                       [(p[0]-pos[0]+distance, p[1]-pos[1]+distance) for p in points])
    
    pygame.draw.polygon(cone_surface, (*color[:3], min(200, color[3]+40)),
                       [(p[0]-pos[0]+distance, p[1]-pos[1]+distance) for p in points], 2)
    
    for r in range(distance//4, 0, -distance//20):
        alpha = max(10, color[3] - r*2)
        pygame.draw.circle(cone_surface, (*color[:3], alpha),
                          (distance, distance), r)
    
    surface.blit(cone_surface, (pos[0]-distance, pos[1]-distance))

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def angle_between(p1, p2):
    return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))