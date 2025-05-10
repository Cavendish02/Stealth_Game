import heapq
import math
import random
from settings import *

class AStar:
    @staticmethod
    def find_path(start, end, world):
        """
        البحث عن مسار باستخدام خوارزمية A* مع تحسينات الأداء
        Args:
            start: tuple (x, y) - إحداثيات البداية بالبكسل
            end: tuple (x, y) - إحداثيات النهاية بالبكسل
            world: كائن العالم للتحقق من العوائق
        Returns:
            list - قائمة بنقاط المسار (إحداثيات البكسل)
        """
        # تحويل الإحداثيات إلى خلايا الشبكة
        grid_start = (int(start[0] // world.cell_size), int(start[1] // world.cell_size))
        grid_end = (int(end[0] // world.cell_size), int(end[1] // world.cell_size))

        # حالة خاصة إذا كانت النقطتان في نفس الخلية
        if grid_start == grid_end:
            return [end]

        # التحقق من المسار المباشر إذا كان مفعلاً
        if (AI_SETTINGS['pathfinding']['direct_path'] and 
            world.has_line_of_sight(start, end)):
            return [end]

        # هياكل البيانات الأساسية
        open_set = []
        heapq.heappush(open_set, (0, grid_start))
        came_from = {}
        g_score = {grid_start: 0}
        f_score = {grid_start: AStar.heuristic(grid_start, grid_end)}
        open_set_hash = {grid_start}
        
        while open_set and len(came_from) < AI_SETTINGS['pathfinding']['max_length']:
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == grid_end:
                path = AStar.reconstruct_path(came_from, current)
                if AI_SETTINGS['pathfinding']['smoothing']:
                    path = AStar.smooth_path(path, world)
                return AStar.convert_to_world(path, world.cell_size)

            for neighbor in world.get_neighbors(current):
                if not AStar.is_valid_cell(neighbor, world):
                    continue

                # حساب التكلفة مع عقوبة الجدران القريبة
                tentative_g = g_score[current] + AStar.calculate_cost(current, neighbor, world, came_from)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + AStar.heuristic(neighbor, grid_end)
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

        # إذا فشل في إيجاد مسار كامل، إرجاع أفضل مسار جزئي
        if came_from:
            path = AStar.reconstruct_path(came_from, current)
            if AI_SETTINGS['pathfinding']['smoothing']:
                path = AStar.smooth_path(path, world)
            return AStar.convert_to_world(path, world.cell_size)

        return []  # لا يوجد مسار ممكن

    @staticmethod
    def is_valid_cell(cell, world):
        """التحقق من صلاحية الخلية للحركة"""
        x, y = cell
        world_x = x * world.cell_size + world.cell_size // 2
        world_y = y * world.cell_size + world.cell_size // 2
        return world.is_valid_position(world_x, world_y, PLAYER_SETTINGS['size'] + 2)

    @staticmethod
    def calculate_cost(current, neighbor, world, came_from):
        """حساب تكلفة الحركة مع عقوبات إضافية"""
        base_cost = 1.0
        x, y = neighbor
        
        # عقوبة الجدران المجاورة
        wall_penalty = 0.0
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(world.grid[0]) and 0 <= ny < len(world.grid):
                if world.grid[ny][nx] == 1:
                    wall_penalty += AI_SETTINGS['pathfinding']['wall_avoidance']

        # عقوبة تغيير الاتجاه المفاجئ
        direction_penalty = 0.0
        if current in came_from:
            prev = came_from[current]
            dx1 = current[0] - prev[0]
            dy1 = current[1] - prev[1]
            dx2 = neighbor[0] - current[0]
            dy2 = neighbor[1] - current[1]
            if (dx1 != dx2) or (dy1 != dy2):
                direction_penalty = 0.2

        return base_cost + wall_penalty + direction_penalty

    @staticmethod
    def heuristic(a, b):
        """دالة التقدير المحسنة باستخدام مسافة مانهاتن المعدلة"""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)

    @staticmethod
    def reconstruct_path(came_from, current):
        """إعادة بناء المسار من نقاط العودة"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    @staticmethod
    def smooth_path(path, world):
        """تجانس المسار بإزالة النقاط غير الضرورية"""
        if len(path) < 3:
            return path

        smoothed = [path[0]]
        i = 0
        
        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1:
                start = AStar.grid_to_world(path[i], world.cell_size)
                end = AStar.grid_to_world(path[j], world.cell_size)
                if world.has_line_of_sight(start, end):
                    break
                j -= 1
            smoothed.append(path[j])
            i = j

        return smoothed

    @staticmethod
    def grid_to_world(grid_pos, cell_size):
        """تحويل إحداثيات الشبكة إلى إحداثيات العالم"""
        return (
            grid_pos[0] * cell_size + cell_size // 2,
            grid_pos[1] * cell_size + cell_size // 2
        )

    @staticmethod
    def convert_to_world(path, cell_size):
        """تحويل مسار كامل من إحداثيات الشبكة إلى العالم"""
        return [AStar.grid_to_world(p, cell_size) for p in path]

    @staticmethod
    def find_safe_position_nearby(position, world, attempts=10):
        """إيجاد موقع آمن قريب من موقع معين"""
        for _ in range(attempts):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 50)
            x = position[0] + math.cos(angle) * dist
            y = position[1] + math.sin(angle) * dist
            if world.is_valid_position(x, y, PLAYER_SETTINGS['size'] + 5):
                return (x, y)
        return position