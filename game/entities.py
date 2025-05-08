import pygame
import math
import random
from settings import *
from .utils import distance, angle_between, draw_vision_cone
from .ai import AStar

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x, self.y = x, y
        self.radius = PLAYER_SETTINGS['size']
        self.speed = PLAYER_SETTINGS['speed']
        self.is_sneaking = False
        self.noise_level = 0
        self.color = PLAYER_SETTINGS['color']
        self.direction = 0
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.update_sprite()

    def update_sprite(self):
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        eye_dist = self.radius * 0.6
        eye_radius = self.radius * 0.3
        angle_rad = math.radians(self.direction)
        
        left_eye = (self.radius + math.cos(angle_rad + math.pi/6) * eye_dist,
                    self.radius + math.sin(angle_rad + math.pi/6) * eye_dist)
        right_eye = (self.radius + math.cos(angle_rad - math.pi/6) * eye_dist,
                     self.radius + math.sin(angle_rad - math.pi/6) * eye_dist)
        
        pygame.draw.circle(self.image, WHITE, [int(p) for p in left_eye], int(eye_radius))
        pygame.draw.circle(self.image, WHITE, [int(p) for p in right_eye], int(eye_radius))

    def move(self, keys, world):
        dx, dy = 0, 0
        if keys['up']: dy -= 1
        if keys['down']: dy += 1
        if keys['left']: dx -= 1
        if keys['right']: dx += 1
        self.is_sneaking = keys['sneak']

        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(dy, dx))

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        speed = PLAYER_SETTINGS['stealth_speed'] if self.is_sneaking else PLAYER_SETTINGS['speed']

        new_x = self.x + dx * speed
        new_y = self.y + dy * speed

        if world.is_valid_position(new_x, self.y, self.radius):
            self.x = new_x
        if world.is_valid_position(self.x, new_y, self.radius):
            self.y = new_y

        self.noise_level = math.sqrt(dx**2 + dy**2) * (0.8 if self.is_sneaking else 2.2)
        self.rect.center = (self.x, self.y)
        self.update_sprite()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Guard(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_points=None):
        super().__init__()
        self.x, self.y = x, y
        self.radius = PLAYER_SETTINGS['size'] * 1.1
        self.speed = GUARD_SETTINGS['speed']
        self.state = "patrol"
        self.patrol_points = patrol_points or self.generate_default_patrol()
        self.current_point = 0
        self.alert_timer = 0
        self.color = GUARD_SETTINGS['color']
        self.last_known_pos = None
        self.search_points = []
        self.investigation_timer = 0
        self.direction = 0
        self.search_radius = GUARD_SETTINGS['search_radius']
        self.patrol_speed = GUARD_SETTINGS['patrol_speed']
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 300  # تقليل زمن التأخير بين الحركات
        self.current_path = []
        self.path_update_cooldown = 0
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.update_sprite()

    def update_sprite(self):
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        eye_dist = self.radius * 0.5
        eye_radius = self.radius * 0.25
        angle_rad = math.radians(self.direction)
        
        left_eye = (self.radius + math.cos(angle_rad + math.pi/4) * eye_dist,
                    self.radius + math.sin(angle_rad + math.pi/4) * eye_dist)
        right_eye = (self.radius + math.cos(angle_rad - math.pi/4) * eye_dist,
                     self.radius + math.sin(angle_rad - math.pi/4) * eye_dist)
        
        pygame.draw.circle(self.image, WHITE, [int(p) for p in left_eye], int(eye_radius))
        pygame.draw.circle(self.image, WHITE, [int(p) for p in right_eye], int(eye_radius))

    def update(self, player, world):
        current_time = pygame.time.get_ticks()
        
        # الاصطياد عند الاقتراب
        if (distance((self.x, self.y), (player.x, player.y)) < GUARD_SETTINGS['catch_radius'] and
            self.has_line_of_sight(player, world)):
            return "caught"
        
        # تحديث المسار أثناء المطاردة
        if self.state == "chase" and self.path_update_cooldown <= current_time:
            self.current_path = AStar.find_path((self.x, self.y), (player.x, player.y), world)
            self.path_update_cooldown = current_time + AI_SETTINGS['path_update_interval']

        if self.current_path and self.state in ["chase", "investigate"]:
            self.follow_path(world)
        else:
            if self.state == "patrol":
                self.patrol(world)
            elif self.state == "search":
                self.search(world)

        if self.state == "patrol":
            if self.can_see(player, world):
                self.state = "chase"
                self.last_known_pos = (player.x, player.y)
                self.alert_timer = GUARD_SETTINGS['alert_duration']

        elif self.state == "chase":
            if self.can_see(player, world):
                self.last_known_pos = (player.x, player.y)
                self.alert_timer = GUARD_SETTINGS['alert_duration']
            else:
                if self.last_known_pos:
                    if distance((self.x, self.y), self.last_known_pos) < 15:
                        self.state = "search"
                        self.generate_search_points(world)
                        self.alert_timer = GUARD_SETTINGS['alert_duration']
                else:
                    self.state = "patrol"

            self.alert_timer -= (current_time - self.last_move_time)
            if self.alert_timer <= 0:
                self.state = "patrol"

        elif self.state == "search":
            self.alert_timer -= (current_time - self.last_move_time)
            if self.alert_timer <= 0 or not self.search_points:
                self.state = "patrol"

        if (player.noise_level > 1.2 and 
            distance((self.x, self.y), (player.x, player.y)) < GUARD_SETTINGS['hearing_distance'] and
            self.state != "chase"):
            self.state = "investigate"
            self.investigation_timer = GUARD_SETTINGS['investigation_duration']
            self.last_known_pos = (player.x, player.y)
            self.generate_search_points(world)

        elif self.state == "investigate":
            self.investigation_timer -= (current_time - self.last_move_time)
            if self.investigation_timer <= 0:
                self.state = "patrol"

        self.last_move_time = current_time
        self.rect.center = (self.x, self.y)
        self.update_sprite()
        return None

    def can_see(self, player, world):
        player_angle = angle_between((self.x, self.y), (player.x, player.y))
        facing_angle = self.direction
        angle_diff = (player_angle - facing_angle + 180) % 360 - 180
        
        if abs(angle_diff) > GUARD_SETTINGS['vision_angle']/2:
            return False
            
        dist = distance((self.x, self.y), (player.x, player.y))
        if dist > GUARD_SETTINGS['vision_distance']:
            return False
            
        if not world.has_line_of_sight((self.x, self.y), (player.x, player.y)):
            return False
                
        return True

    def has_line_of_sight(self, player, world):
        steps = max(20, int(distance((self.x, self.y), (player.x, player.y)) * 2))
        for step in range(1, steps):
            x = self.x + (player.x - self.x) * step/steps
            y = self.y + (player.y - self.y) * step/steps
            if world.is_wall(x, y):
                return False
        return True

    def patrol(self, world):
        if not self.patrol_points or len(self.patrol_points) < 2:
            self.patrol_points = self.generate_default_patrol()
            
        target = self.patrol_points[self.current_point]
        dist = distance((self.x, self.y), target)
        
        if dist < 10:
            self.current_point = (self.current_point + 1) % len(self.patrol_points)
            target = self.patrol_points[self.current_point]
        
        self.move_toward(target, world, self.patrol_speed)

    def generate_default_patrol(self):
        return [
            (self.x + 100, self.y),
            (self.x, self.y + 100),
            (self.x - 100, self.y),
            (self.x, self.y - 100)
        ]

    def generate_search_points(self, world):
        self.search_points = []
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            dist = random.uniform(self.search_radius*0.5, self.search_radius)
            point = (
                self.last_known_pos[0] + math.cos(rad) * dist,
                self.last_known_pos[1] + math.sin(rad) * dist
            )
            if world.is_valid_position(point[0], point[1], self.radius):
                self.search_points.append(point)

    def search(self, world):
        if not self.search_points:
            self.generate_search_points(world)
            return
            
        target = self.search_points[0]
        if distance((self.x, self.y), target) < 15:
            self.search_points.pop(0)
            if not self.search_points:
                return
                
        self.move_toward(target, world, self.speed * 0.9)

    def follow_path(self, world):
        if not self.current_path:
            return

        target = self.current_path[0]
        if distance((self.x, self.y), target) < 10:
            self.current_path.pop(0)
            if not self.current_path:
                return

        self.move_toward(target, world, self.speed)

    def move_toward(self, target, world, speed):
        angle = math.atan2(target[1] - self.y, target[0] - self.x)
        
        # تحديد السرعة بناء على حالة الحارس
        current_speed = GUARD_SETTINGS['chase_speed'] if self.state == "chase" else speed
        
        # حساب الحركة مع مراعاة الإطارات
        frame_speed = current_speed * (pygame.time.get_ticks() - self.last_move_time) / 1000
        
        dx = math.cos(angle) * frame_speed
        dy = math.sin(angle) * frame_speed
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # الحركة الذكية مع تجنب الجدران
        if world.is_valid_position(new_x, new_y, self.radius):
            self.x = new_x
            self.y = new_y
        elif world.is_valid_position(new_x, self.y, self.radius):
            self.x = new_x
        elif world.is_valid_position(self.x, new_y, self.radius):
            self.y = new_y
        else:
            # إذا فشل كل شيء، نغير الاتجاه
            self.direction = (self.direction + 180) % 360
        
        self.direction = math.degrees(angle)
        self.rect.center = (self.x, self.y)
        self.last_move_time = pygame.time.get_ticks()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        
        if self.state == "patrol":
            vision_color = (*YELLOW, 60)
        elif self.state == "chase":
            vision_color = (*RED, 120)
        elif self.state == "investigate":
            vision_color = (*PURPLE, 90)
        else:
            vision_color = (*ORANGE, 80)
            
        draw_vision_cone(
            surface,
            (int(self.x), int(self.y)),
            self.direction,
            GUARD_SETTINGS['vision_distance'],
            GUARD_SETTINGS['vision_angle'],
            color=vision_color
        )

class Objective:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = OBJECTIVE['size']
        self.color = OBJECTIVE['color']
        self.collected = False
        self.pulse_timer = 0
        self.pulse_speed = OBJECTIVE['pulse_speed']
        self.image = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        if not self.collected:
            self.pulse_timer += self.pulse_speed
            pulse_factor = 0.7 + 0.3 * math.sin(self.pulse_timer)
            
            self.image.fill((0,0,0,0))
            for alpha in range(20, 0, -4):
                radius = int(self.radius * pulse_factor * 2 + alpha)
                pygame.draw.circle(self.image, (*self.color, alpha), 
                                 (self.radius*2, self.radius*2), radius)
            
            current_radius = int(self.radius * pulse_factor)
            pygame.draw.circle(self.image, self.color, 
                             (self.radius*2, self.radius*2), current_radius)
            pygame.draw.circle(self.image, WHITE, 
                             (self.radius*2, self.radius*2), int(current_radius/2))
            
            surface.blit(self.image, self.rect.topleft)