import heapq
import math
from settings import *

class AStar:
    @staticmethod
    def find_path(start, end, world):
        if AI_SETTINGS['use_direct_path'] and world.has_line_of_sight(start, end):
            return [end]
            
        grid_start = (int(start[0] // world.cell_size), int(start[1] // world.cell_size))
        grid_end = (int(end[0] // world.cell_size), int(end[1] // world.cell_size))

        open_set = []
        heapq.heappush(open_set, (0, grid_start))
        came_from = {}
        g_score = {grid_start: 0}
        f_score = {grid_start: AStar.heuristic(grid_start, grid_end)}
        open_set_hash = {grid_start}

        while open_set and len(came_from) < AI_SETTINGS['max_path_length']:
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == grid_end:
                path = AStar.reconstruct_path(came_from, current)
                if AI_SETTINGS['path_smoothing']:
                    path = AStar.smooth_path(path, world)
                return [(x * world.cell_size + world.cell_size//2, 
                        y * world.cell_size + world.cell_size//2) for x, y in path]

            for neighbor in world.get_neighbors(current):
                if not world.is_valid_position(
                    neighbor[0] * world.cell_size + world.cell_size//2,
                    neighbor[1] * world.cell_size + world.cell_size//2,
                    PLAYER_SETTINGS['size']
                ):
                    continue

                tentative_g = g_score[current] + AStar.heuristic(current, neighbor)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + AStar.heuristic(neighbor, grid_end)
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

        return []

    @staticmethod
    def smooth_path(path, world):
        if len(path) < 3:
            return path
            
        smoothed = [path[0]]
        for i in range(1, len(path)-1):
            if not world.has_line_of_sight(smoothed[-1], path[i+1]):
                smoothed.append(path[i])
        smoothed.append(path[-1])
        return smoothed

    @staticmethod
    def heuristic(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return (dx + dy) + 0.1 * math.sqrt(dx*dx + dy*dy)

    @staticmethod
    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path