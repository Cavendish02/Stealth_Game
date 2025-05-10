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
        self.speed = PLAYER_SETTINGS['speed']['normal']
        self.is_sneaking = False
        self.is_sprinting = False
        self.noise_level = 0
        self.stamina = PLAYER_SETTINGS['stamina']['max']
        self.color = get_color('green')
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
        
        pygame.draw.circle(self.image, get_color('white'), left_eye, int(eye_radius))
        pygame.draw.circle(self.image, get_color('white'), right_eye, int(eye_radius))

    def move(self, keys, world):
        dx, dy = 0, 0
        if keys.get('up', False): dy -= 1
        if keys.get('down', False): dy += 1
        if keys.get('left', False): dx -= 1
        if keys.get('right', False): dx += 1
        
        self.is_sneaking = keys.get('sneak', False)
        self.is_sprinting = keys.get('sprint', False) and not self.is_sneaking and self.stamina > 0
        
        if self.is_sprinting:
            speed = PLAYER_SETTINGS['speed']['sprint']
            self.stamina -= PLAYER_SETTINGS['stamina']['sprint_cost'] / FPS
        elif self.is_sneaking:
            speed = PLAYER_SETTINGS['speed']['sneak']
        else:
            speed = PLAYER_SETTINGS['speed']['normal']
            self.stamina = min(self.stamina + PLAYER_SETTINGS['stamina']['regen_rate'] / FPS, 
                             PLAYER_SETTINGS['stamina']['max'])

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        movement_factor = math.sqrt(dx**2 + dy**2)
        if self.is_sprinting:
            self.noise_level = movement_factor * PLAYER_SETTINGS['noise']['sprint_multiplier']
        elif self.is_sneaking:
            self.noise_level = movement_factor * PLAYER_SETTINGS['noise']['sneak_multiplier']
        else:
            self.noise_level = movement_factor
        
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed
        
        if world.is_valid_position(new_x, self.y, self.radius + 2):
            self.x = new_x
        if world.is_valid_position(self.x, new_y, self.radius + 2):
            self.y = new_y

        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(dy, dx))
        
        self.rect.center = (self.x, self.y)
        self.update_sprite()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Guard(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_points=None):
        super().__init__()
        self.x, self.y = x, y
        self.radius = GUARD_SETTINGS['size']
        self.base_speed = GUARD_SETTINGS['speed']['patrol']
        self.state = "patrol"
        self.patrol_points = patrol_points or self.generate_patrol_route()
        self.current_point = 0
        self.alert_level = 0
        self.color = get_color('red')
        self.last_known_pos = None
        self.search_points = []
        self.direction = random.uniform(0, 360)
        self.current_path = []
        self.path_update_timer = 0
        self.stuck_timer = 0
        self.max_stuck_time = 3  # ثواني قبل اعتباره عالقاً
        self.current_speed = 0
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.update_sprite()

    def update_sprite(self):
        self.image.fill((0,0,0,0))
        
        if self.state == "chase":
            color = get_color('dark_red')
        elif self.state == "investigate":
            color = get_color('orange')
        else:
            color = self.color
            
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        
        eye_dist = self.radius * 0.5
        eye_radius = self.radius * 0.25
        angle_rad = math.radians(self.direction)
        
        left_eye = (self.radius + math.cos(angle_rad + math.pi/4) * eye_dist,
                    self.radius + math.sin(angle_rad + math.pi/4) * eye_dist)
        right_eye = (self.radius + math.cos(angle_rad - math.pi/4) * eye_dist,
                     self.radius + math.sin(angle_rad - math.pi/4) * eye_dist)
        
        pygame.draw.circle(self.image, get_color('white'), left_eye, int(eye_radius))
        pygame.draw.circle(self.image, get_color('white'), right_eye, int(eye_radius))
        
        pupil_offset = eye_radius * 0.6
        pygame.draw.circle(self.image, get_color('black'), 
                         (left_eye[0] + math.cos(angle_rad) * pupil_offset,
                          left_eye[1] + math.sin(angle_rad) * pupil_offset), 
                         int(eye_radius/2))
        pygame.draw.circle(self.image, get_color('black'), 
                         (right_eye[0] + math.cos(angle_rad) * pupil_offset,
                          right_eye[1] + math.sin(angle_rad) * pupil_offset), 
                         int(eye_radius/2))

    def update(self, player, world):
        self.path_update_timer -= 1/FPS
        
        if self.state == "chase":
            self.alert_level = min(1.0, self.alert_level + 0.05)
            if self.check_catch_player(player, world):
                return "caught"
        else:
            self.alert_level = max(0, self.alert_level - 0.01)

        if self.can_see(player, world):
            self.handle_player_detected(player, world)
        elif self.state == "chase":
            self.handle_lost_player(player, world)

        if player.noise_level > 0.5:
            noise_range = GUARD_SETTINGS['hearing']['sprint_range'] if player.is_sprinting else \
                         GUARD_SETTINGS['hearing']['normal_range'] if not player.is_sneaking else \
                         GUARD_SETTINGS['hearing']['sneak_range']
            
            if distance((self.x, self.y), (player.x, player.y)) < noise_range * (1 + self.alert_level):
                self.distract((player.x, player.y), world)

        if self.current_path:
            self.follow_path(world)
        elif self.state == "patrol":
            self.patrol(world)
        elif self.state == "search":
            self.search(world)

        self.rect.center = (self.x, self.y)
        self.update_sprite()

    def can_see(self, player, world):
        dist = distance((self.x, self.y), (player.x, player.y))
        vision_dist = GUARD_SETTINGS['vision']['distance'] * (1 + self.alert_level * 0.5)
        
        if dist > vision_dist:
            return False
            
        if not world.has_line_of_sight((self.x, self.y), (player.x, player.y)):
            return False
            
        player_angle = angle_between((self.x, self.y), (player.x, player.y))
        angle_diff = abs((player_angle - self.direction + 180) % 360 - 180)
        vision_angle = GUARD_SETTINGS['vision']['angle'] / (2 - self.alert_level)
        
        return angle_diff <= vision_angle

    def check_catch_player(self, player, world):
        dist = distance((self.x, self.y), (player.x, player.y))
        if dist < GUARD_SETTINGS['behavior']['catch_radius']:
            return world.has_line_of_sight((self.x, self.y), (player.x, player.y))
        return False

    def generate_patrol_route(self):
        """إنشاء مسار دورية أكثر ذكاءً يتجنب الجدران"""
        patrol_points = []
        for _ in range(4):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(150, 300)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            patrol_points.append((x, y))
        return patrol_points

    def handle_player_detected(self, player, world):
        if self.state != "chase":
            self.state = "chase"
            self.alert_level = 0.5
            
        self.last_known_pos = (player.x, player.y)
        
        if self.path_update_timer <= 0:
            self.current_path = AStar.find_path((self.x, self.y), (player.x, player.y), world)
            self.path_update_timer = AI_SETTINGS['pathfinding']['update_interval']

    def handle_lost_player(self, player, world):
        if self.last_known_pos is None:
            self.last_known_pos = (player.x, player.y)
            
        if distance((self.x, self.y), self.last_known_pos) < 20:
            self.state = "investigate"
            self.generate_search_points(world)
        else:
            self.state = "patrol"

    def generate_search_points(self, world):
        self.search_points = []
        search_center = self.last_known_pos if self.last_known_pos else (self.x, self.y)
        
        for angle in range(0, 360, 45):
            dist = random.uniform(
                GUARD_SETTINGS['behavior']['search_radius'] * 0.5,
                GUARD_SETTINGS['behavior']['search_radius'] * 1.5
            )
            x = search_center[0] + math.cos(math.radians(angle)) * dist
            y = search_center[1] + math.sin(math.radians(angle)) * dist
            if world.is_valid_position(x, y, self.radius):
                self.search_points.append((x, y))
        
        if not self.search_points:
            for angle in range(0, 360, 90):
                x = self.x + math.cos(math.radians(angle)) * 50
                y = self.y + math.sin(math.radians(angle)) * 50
                self.search_points.append((x, y))

    def distract(self, pos, world):
        if self.state != "chase":
            self.state = "investigate"
            self.current_path = AStar.find_path((self.x, self.y), pos, world)
            self.path_update_timer = AI_SETTINGS['pathfinding']['update_interval']

    def patrol(self, world):
        if not self.patrol_points or len(self.patrol_points) < 2:
            self.patrol_points = self.generate_patrol_route()
            
        target = self.patrol_points[self.current_point]
        
        # تتبع الوقت الذي يكون فيه الحارس عالقاً
        if distance((self.x, self.y), target) < 10:
            self.stuck_timer = 0
        else:
            self.stuck_timer += 1/FPS
            if self.stuck_timer > self.max_stuck_time:
                self.current_point = (self.current_point + 1) % len(self.patrol_points)
                self.stuck_timer = 0
        
        if self.move_toward(target, world, GUARD_SETTINGS['speed']['patrol']):
            self.current_point = (self.current_point + 1) % len(self.patrol_points)
            
            # بعد كل دورة، أعد توليد المسار لمنع التكرار
            if self.current_point == 0:
                self.patrol_points = self.generate_patrol_route()

    def search(self, world):
        if not self.search_points:
            if self.last_known_pos:
                self.generate_search_points(world)
            else:
                self.state = "patrol"
            return
            
        target = self.search_points[0]
        if self.move_toward(target, world, GUARD_SETTINGS['speed']['search']):
            self.search_points.pop(0)
            if not self.search_points:
                self.state = "patrol"

    def follow_path(self, world):
        if not self.current_path:
            return
            
        target = self.current_path[0]
        if self.move_toward(target, world, self.get_speed()):
            self.current_path.pop(0)
            if not self.current_path:
                if self.state == "investigate":
                    self.state = "search"

    def get_speed(self):
        if self.state == "chase":
            return GUARD_SETTINGS['speed']['chase']
        elif self.state == "investigate":
            return GUARD_SETTINGS['speed']['alert']
        return self.base_speed

    def move_toward(self, target, world, speed):
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 10:
            return True
            
        # تطبيع الاتجاه مع تعديلات لتجنب الجدران
        dx_normalized = dx / dist
        dy_normalized = dy / dist
        
        # حساب الحركة مع اكتشاف العقبات مسبقاً
        move_dist = min(speed, dist)
        new_x = self.x + dx_normalized * move_dist
        new_y = self.y + dy_normalized * move_dist
        
        # التحقق من الجدران في الاتجاهات المحتملة
        can_move_x = world.is_valid_position(new_x, self.y, self.radius + 5)  # زيادة هامش الأمان
        can_move_y = world.is_valid_position(self.x, new_y, self.radius + 5)
        
        # إذا كان عالقاً، حاول تغيير الاتجاه بشكل ذكي
        if not can_move_x and not can_move_y:
            for angle_offset in [45, -45, 90, -90]:
                new_angle = math.radians(self.direction + angle_offset)
                test_x = self.x + math.cos(new_angle) * move_dist
                test_y = self.y + math.sin(new_angle) * move_dist
                
                if world.is_valid_position(test_x, test_y, self.radius + 5):
                    new_x, new_y = test_x, test_y
                    can_move_x = can_move_y = True
                    break
        
        if can_move_x and can_move_y:
            self.x, self.y = new_x, new_y
        elif can_move_x:
            self.x = new_x
        elif can_move_y:
            self.y = new_y
        else:
            return True
            
        # تحديث الاتجاه بحركة أكثر سلاسة
        if dx != 0 or dy != 0:
            target_angle = math.degrees(math.atan2(dy, dx))
            angle_diff = (target_angle - self.direction + 180) % 360 - 180
            self.direction += angle_diff * 0.1  # تعديل تدريجي للاتجاه
            
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        if DEBUG_SETTINGS['visible']['vision']:
            if self.state == "patrol":
                alpha = 60 + int(self.alert_level * 60)
                color = (*get_color('yellow'), alpha)
            elif self.state == "chase":
                color = (*get_color('red'), 180)
            else:
                color = (*get_color('blue'), 120)
                
            draw_vision_cone(
                surface,
                (int(self.x), int(self.y)),
                self.direction,
                GUARD_SETTINGS['vision']['distance'] * (1 + self.alert_level/2),
                GUARD_SETTINGS['vision']['angle']/(2 - self.alert_level),
                color=color
            )

class Objective(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x, self.y = x, y
        self.radius = OBJECTIVE_SETTINGS['size']
        self.color = get_color('blue')
        self.collected = False
        self.pulse_timer = 0
        self.image = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.update()

    def update(self):
        if not self.collected:
            self.pulse_timer += OBJECTIVE_SETTINGS['pulse_speed']
            pulse = 0.7 + 0.3 * math.sin(self.pulse_timer)
            self.image.fill((0,0,0,0))
            
            for alpha in range(30, 0, -5):
                radius = int(self.radius * 2 * pulse + alpha/3)
                pygame.draw.circle(self.image, (*self.color, alpha//2), 
                                 (self.radius*2, self.radius*2), radius)
            
            pygame.draw.circle(self.image, self.color, 
                             (self.radius*2, self.radius*2), int(self.radius * pulse))
            pygame.draw.circle(self.image, get_color('white'), 
                             (self.radius*2, self.radius*2), int(self.radius * pulse/2))

    def draw(self, surface):
        if not self.collected:
            surface.blit(self.image, self.rect.topleft)