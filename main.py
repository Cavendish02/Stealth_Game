import pygame
import sys
import random
from settings import *
from game.entities import Player, Guard
from game.world import World

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Initialize game world
        self.world = World()
        
        # Create player at valid position
        player_x, player_y = self.world.get_valid_position()
        self.player = Player(player_x, player_y)
        
        # Create guards with patrol routes
        self.guards = []
        for _ in range(2):
            guard_x, guard_y = self.world.get_valid_position()
            patrol_points = []
            for _ in range(4):
                px = guard_x + random.randint(-100, 100)
                py = guard_y + random.randint(-100, 100)
                patrol_points.append((px, py))
            self.guards.append(Guard(guard_x, guard_y, patrol_points))
        
        # Control states
        self.keys = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'sneak': False
        }
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Update key states
            if event.type == pygame.KEYDOWN:
                if event.key in CONTROLS['up']: self.keys['up'] = True
                if event.key in CONTROLS['down']: self.keys['down'] = True
                if event.key in CONTROLS['left']: self.keys['left'] = True
                if event.key in CONTROLS['right']: self.keys['right'] = True
                if event.key == CONTROLS['sneak']: self.keys['sneak'] = True
            
            if event.type == pygame.KEYUP:
                if event.key in CONTROLS['up']: self.keys['up'] = False
                if event.key in CONTROLS['down']: self.keys['down'] = False
                if event.key in CONTROLS['left']: self.keys['left'] = False
                if event.key in CONTROLS['right']: self.keys['right'] = False
                if event.key == CONTROLS['sneak']: self.keys['sneak'] = False
    
    def update(self):
        # Update player
        self.player.is_sneaking = self.keys['sneak']
        self.player.move(self.keys, self.world)
        
        # Update guards
        for guard in self.guards:
            guard.update(self.player, self.world)
    
    def draw(self):
        # Draw background
        self.screen.fill(BLACK)
        
        # Draw world
        self.world.draw(self.screen)
        
        # Draw guards
        for guard in self.guards:
            guard.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Sneak status
        sneak_text = self.font.render(
            f"Sneak: {'ON' if self.player.is_sneaking else 'OFF'}",
            True,
            WHITE
        )
        self.screen.blit(sneak_text, (10, 10))
        
        # Noise level
        noise_text = self.font.render(
            f"Noise: {int(self.player.noise_level)}",
            True,
            WHITE
        )
        self.screen.blit(noise_text, (10, 40))
    
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