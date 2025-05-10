import pygame
import sys
import math
import random
from settings import *
from game.entities import Player, Guard, Objective
from game.world import World
from game.utils import distance

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    PLAYER_SETTINGS, GUARD_SETTINGS, CONTROLS, AI_SETTINGS,
    DARK_GRAY, GREEN, RED, WHITE, ORANGE
)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.game_state = "playing"
        self.additional_guards_spawned = False
        
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.guards_group = pygame.sprite.Group()
        
        # Initialize world
        self.world = World()
        
        # Set positions
        self.start_pos = self.world.get_start_position()
        end_pos = self.world.get_end_position()
        
        # Create player and objective
        self.player = Player(*self.start_pos)
        self.objective = Objective(*end_pos)
        self.all_sprites.add(self.player)
        
        # Create initial guards
        self.guards = []
        self.create_initial_guards()
        
        # Controls
        self.keys = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'sneak': False
        }

    def create_initial_guards(self):
        guard_positions = []
        
        for _ in range(2):  # Initial guards
            while True:
                pos = self.world.get_valid_position(
                    min_dist=GUARD_SETTINGS['behavior']['min_spawn_distance'],
                    exclude_pos=(self.player.x, self.player.y)
                )
                if pos:
                    if all(distance(pos, (g.x, g.y)) > 150 for g in self.guards):
                        guard_positions.append(pos)
                        break
        
        for x, y in guard_positions:
            patrol_points = self.generate_patrol_points(x, y)
            guard = Guard(x, y, patrol_points)
            
            if self.world.is_valid_position(guard.x, guard.y, guard.radius):
                self.guards.append(guard)
                self.guards_group.add(guard)
                self.all_sprites.add(guard)

    def generate_patrol_points(self, x, y):
        patrol_points = []
        directions = [(1,0), (0,1), (-1,0), (0,-1)]
        
        for dx, dy in directions:
            for dist in [2, 4]:
                px = x + dx * self.world.cell_size * dist
                py = y + dy * self.world.cell_size * dist
                
                if (0 <= px < SCREEN_WIDTH and 
                    0 <= py < SCREEN_HEIGHT and 
                    self.world.is_valid_position(px, py, PLAYER_SETTINGS['size'])):
                    patrol_points.append((px, py))
        
        if not patrol_points:
            for angle in range(0, 360, 90):
                rad = math.radians(angle)
                patrol_points.append((
                    x + math.cos(rad) * 100,
                    y + math.sin(rad) * 100
                ))
        
        return patrol_points

    def spawn_additional_guards(self):
        for _ in range(4):
            pos = None
            attempts = 0
            
            while attempts < 50:
                pos = self.world.get_valid_position(
                    min_dist=GUARD_SETTINGS['min_spawn_distance'],
                    exclude_pos=(self.player.x, self.player.y)
                )
                
                if pos and all(distance(pos, (g.x, g.y)) > 150 for g in self.guards):
                    break
                    
                attempts += 1
            
            if not pos:
                continue
                
            patrol_points = []
            for _ in range(4):
                angle = random.uniform(0, 2*math.pi)
                dist = random.uniform(50, 120)
                point = (
                    pos[0] + math.cos(angle) * dist,
                    pos[1] + math.sin(angle) * dist
                )
                if self.world.is_valid_position(point[0], point[1], PLAYER_SETTINGS['size']):
                    patrol_points.append(point)
            
            if patrol_points:
                guard = Guard(*pos, patrol_points)
                self.guards.append(guard)
                self.guards_group.add(guard)
                self.all_sprites.add(guard)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key in CONTROLS['up']: self.keys['up'] = True
                if event.key in CONTROLS['down']: self.keys['down'] = True
                if event.key in CONTROLS['left']: self.keys['left'] = True
                if event.key in CONTROLS['right']: self.keys['right'] = True
                if event.key == CONTROLS['sneak']: self.keys['sneak'] = True
                if event.key == pygame.K_r and self.game_state != "playing":
                    self.__init__()
            
            if event.type == pygame.KEYUP:
                if event.key in CONTROLS['up']: self.keys['up'] = False
                if event.key in CONTROLS['down']: self.keys['down'] = False
                if event.key in CONTROLS['left']: self.keys['left'] = False
                if event.key in CONTROLS['right']: self.keys['right'] = False
                if event.key == CONTROLS['sneak']: self.keys['sneak'] = False

    def update(self):
        # تحديث الحراس أولاً
        for guard in self.guards:
            result = guard.update(self.player, self.world)
            if result == "caught":
                self.game_state = "lose"
                return
        
        if self.game_state != "playing":
            return
            
        self.player.move(self.keys, self.world)
        
        # Check objective
        if not self.objective.collected:
            dist = distance((self.player.x, self.player.y), (self.objective.x, self.objective.y))
            if dist < self.player.radius + self.objective.radius:
                self.objective.collected = True
                if not self.additional_guards_spawned:
                    self.spawn_additional_guards()
                    self.additional_guards_spawned = True
        
        # Check win condition
        if self.objective.collected:
            dist_to_start = distance((self.player.x, self.player.y), self.start_pos)
            if dist_to_start < self.player.radius + 20:
                self.game_state = "win"

    def draw(self):
        self.screen.fill(DARK_GRAY)
        self.world.draw(self.screen)
        
        # Draw light effect
        light_radius = 180 if not self.player.is_sneaking else 100
        light = pygame.Surface((light_radius*2, light_radius*2), pygame.SRCALPHA)
        for r in range(light_radius, 0, -15):
            alpha = max(0, min(80, 100 - r//2))
            pygame.draw.circle(light, (40, 40, 60, alpha), 
                             (light_radius, light_radius), r)
        self.screen.blit(light, (self.player.x-light_radius, self.player.y-light_radius))
        
        # Draw all sprites
        if not self.objective.collected:
            self.objective.draw(self.screen)
        
        for guard in self.guards:
            guard.draw(self.screen)
        
        self.player.draw(self.screen)
        self.draw_ui()
        
        if self.game_state != "playing":
            self.draw_game_over()
        
        pygame.display.flip()

    def draw_ui(self):
        ui_bg = pygame.Surface((170, 130), pygame.SRCALPHA)
        ui_bg.fill((30, 30, 40, 180))
        self.screen.blit(ui_bg, (5, 5))
        
        sneak_status = "ON" if self.player.is_sneaking else "OFF"
        sneak_color = GREEN if self.player.is_sneaking else RED
        sneak_text = self.font.render(f"STEALTH: {sneak_status}", True, sneak_color)
        self.screen.blit(sneak_text, (10, 10))
        
        noise_level = min(100, int(self.player.noise_level * 33))
        noise_text = self.font.render(f"NOISE: {int(self.player.noise_level)}", True, WHITE)
        self.screen.blit(noise_text, (10, 40))
        pygame.draw.rect(self.screen, (80, 80, 80), (10, 65, 100, 15))
        pygame.draw.rect(self.screen, (noise_level, 100-noise_level, 0), (10, 65, noise_level, 15))
        
        obj_status = "FOUND" if self.objective.collected else "HIDDEN"
        obj_color = GREEN if self.objective.collected else ORANGE
        obj_text = self.font.render(f"OBJECTIVE: {obj_status}", True, obj_color)
        self.screen.blit(obj_text, (10, 90))
        
        guards_text = self.font.render(f"GUARDS: {len(self.guards)}", True, RED)
        self.screen.blit(guards_text, (10, 115))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        if self.game_state == "win":
            text = self.font.render("MISSION ACCOMPLISHED!", True, GREEN)
        else:
            text = self.font.render("YOU WERE CAUGHT!", True, RED)
        
        subtext = self.font.render("Press R to restart", True, WHITE)
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        subtext_rect = subtext.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        
        self.screen.blit(text, text_rect)
        self.screen.blit(subtext, subtext_rect)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()