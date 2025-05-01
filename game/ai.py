import heapq
from settings import *  # استيراد مباشر
from .world import World  # استيراد نسبي

def a_star(start, end, world):
    """خوارزمية A* لإيجاد المسار"""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == end:
            return reconstruct_path(came_from, current)
        
        for neighbor in world.get_neighbors(current):
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return []  # لا يوجد مسار

def heuristic(a, b):
    """دالة تقدير المسافة (مانهاتن)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    """إعادة بناء المسار من النهاية إلى البداية"""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path