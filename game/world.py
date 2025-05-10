import pygame
import math
import random
from settings import *

class World:
    def __init__(self):
        # خريطة اللعب (1 = جدار، 0 = أرضية، 2 = نقطة البداية، 3 = نقطة النهاية)
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,2,0,0,1,0,0,0,1,0,0,0,1,0,0,1],
            [1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,1],
            [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1],
            [1,1,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,1,1,0,1,1,0,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,0,1,1,0,1,1,1,3,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        self.cell_size = WORLD_SETTINGS['cell_size']
        self.wall_thickness = WORLD_SETTINGS['wall_thickness']
        self.wall_color = get_color('light_gray')
        self.wall_highlight = get_color('white')
        self.floor_color = get_color('dark_gray')
        self.floor_highlight = get_color('dark_gray', 50)
        self.start_color = get_color('green')
        self.end_color = get_color('blue')

    def draw(self, surface):
        """رسم خريطة اللعب مع تأثيرات بصرية محسنة"""
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                if tile == 1:  # جدار
                    self.draw_wall(surface, rect)
                elif tile == 2:  # نقطة البداية
                    self.draw_start(surface, rect)
                elif tile == 3:  # نقطة النهاية
                    self.draw_end(surface, rect)
                else:  # أرضية
                    self.draw_floor(surface, rect)

    def draw_wall(self, surface, rect):
        """رسم الجدار مع تأثيرات ثلاثية الأبعاد"""
        pygame.draw.rect(surface, self.wall_color, rect)
        
        # تأثير الإضاءة على الحواف
        highlight_rect = rect.inflate(-self.wall_thickness, -self.wall_thickness)
        pygame.draw.rect(surface, self.wall_highlight, highlight_rect, 2)
        
        # تأثير النقش على الجدار
        if (rect.x // self.cell_size + rect.y // self.cell_size) % 3 == 0:
            pygame.draw.line(surface, self.wall_highlight, 
                           (rect.left + 5, rect.top + 5),
                           (rect.right - 5, rect.bottom - 5), 1)

    def draw_floor(self, surface, rect):
        """رسم الأرضية مع تأثيرات بصرية"""
        pygame.draw.rect(surface, self.floor_color, rect)
        
        # تأثير النقش الخفيف
        if (rect.x // self.cell_size + rect.y // self.cell_size) % 4 == 0:
            pattern_rect = rect.inflate(-self.cell_size//2, -self.cell_size//2)
            pygame.draw.rect(surface, self.floor_highlight, pattern_rect)

    def draw_start(self, surface, rect):
        """رسم نقطة البداية"""
        pygame.draw.rect(surface, self.floor_color, rect)
        center = rect.center
        radius = self.cell_size // 4
        pygame.draw.circle(surface, self.start_color, center, radius)
        
        # تأثير النبض
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.005)
        pygame.draw.circle(surface, get_color('white'), center, int(radius * pulse), 2)

    def draw_end(self, surface, rect):
        """رسم نقطة النهاية"""
        pygame.draw.rect(surface, self.floor_color, rect)
        center = rect.center
        radius = self.cell_size // 3
        
        # تأثير التوهج
        glow_surface = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.end_color, 50), 
                         (radius*2, radius*2), radius*2)
        surface.blit(glow_surface, (center[0]-radius*2, center[1]-radius*2))
        
        pygame.draw.circle(surface, self.end_color, center, radius)

    def get_start_position(self):
        """الحصول على موقع نقطة البداية"""
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == 2:
                    return (
                        x * self.cell_size + self.cell_size // 2,
                        y * self.cell_size + self.cell_size // 2
                    )
        return (self.cell_size, self.cell_size)  # موقع افتراضي

    def get_end_position(self):
        """الحصول على موقع نقطة النهاية"""
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == 3:
                    return (
                        x * self.cell_size + self.cell_size // 2,
                        y * self.cell_size + self.cell_size // 2
                    )
        return (
            len(self.grid[0]) * self.cell_size - self.cell_size,
            len(self.grid) * self.cell_size - self.cell_size
        )

    def is_wall(self, x, y):
        """تحقق إذا كانت الخلية في الموقع (x,y) هي جدار"""
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        
        if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
            return self.grid[grid_y][grid_x] == 1
        return True  # اعتبار كل شيء خارج الخريطة جدارًا

    def is_valid_position(self, x, y, radius):
        """تحقق إذا كان الموقع صالحًا لكائن بحجم معين"""
        # التحقق من المركز
        if self.is_wall(x, y):
            return False
            
        # التحقق من الزوايا الأربع
        points = [
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius)
        ]
        
        return not any(self.is_wall(px, py) for px, py in points)

    def has_line_of_sight(self, pos1, pos2, precision=2):
        """
        تحقق إذا كان هناك خط رؤية مباشر بين نقطتين
        مع تحسينات للدقة والأداء
        """
        steps = max(10, int(math.dist(pos1, pos2) // precision))
        
        for step in range(1, steps):
            t = step / steps
            x = pos1[0] + (pos2[0] - pos1[0]) * t
            y = pos1[1] + (pos2[1] - pos1[1]) * t
            
            if self.is_wall(x, y):
                return False
        
        # تحقق إضافي من النقاط المحيطة بالهدف
        for offset in [(5,5), (-5,5), (5,-5), (-5,-5)]:
            x = pos2[0] + offset[0]
            y = pos2[1] + offset[1]
            if self.is_wall(x, y):
                return False
                
        return True

    def get_valid_position(self, min_dist=200, exclude_pos=None, max_attempts=100):
        """
        الحصول على موقع عشوائي صالح في الخريطة
        مع ضوابط للمسافة الآمنة
        """
        radius = PLAYER_SETTINGS['size'] + 5  # هامش أمان
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(1, len(self.grid[0])-2)
            y = random.randint(1, len(self.grid)-2)
            
            if self.grid[y][x] == 0:  # تأكد أنها أرضية
                pos = (
                    x * self.cell_size + self.cell_size // 2,
                    y * self.cell_size + self.cell_size // 2
                )
                
                # التحقق من المسافة الآمنة
                if exclude_pos and math.dist(pos, exclude_pos) < min_dist:
                    attempts += 1
                    continue
                    
                if self.is_valid_position(pos[0], pos[1], radius):
                    return pos
                    
            attempts += 1
            
        return None  # إذا لم يتم العثور على موقع صالح

    def get_neighbors(self, cell):
        """
        الحصول على الخلايا المجاورة لخلية معينة
        مع تحسينات للحركة القطرية
        """
        x, y = cell
        neighbors = []
        
        # الجوار الأساسي (أعلى، أسفل، يمين، يسار)
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.grid[0]) and 0 <= ny < len(self.grid):
                if self.grid[ny][nx] != 1:  # تأكد أنها ليست جدارًا
                    neighbors.append((nx, ny))
        
        # الجوار القطري (إذا كانت الحركة القطرية مسموحة)
        if AI_SETTINGS['pathfinding'].get('allow_diagonal', True):
            for dx, dy in [(1,1), (-1,-1), (1,-1), (-1,1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(self.grid[0]) and 0 <= ny < len(self.grid) and
                    self.grid[ny][nx] != 1 and
                    self.grid[y][nx] != 1 and  # تأكد من عدم وجود جدار في المنتصف
                    self.grid[ny][x] != 1):
                    neighbors.append((nx, ny))
        
        return neighbors

    def get_cell_center(self, cell):
        """الحصول على مركز الخلية في إحداثيات العالم"""
        x, y = cell
        return (
            x * self.cell_size + self.cell_size // 2,
            y * self.cell_size + self.cell_size // 2
        )