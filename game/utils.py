import pygame
import math
from settings import *

from settings import YELLOW, RED  # أضف هذه في الأعلى

def draw_vision_cone(surface, pos, angle, distance, angle_width, color=None):
    """
    رسم مخروط رؤية مع تأثيرات ضوئية متدرجة
    
    Args:
        surface: السطح المراد الرسم عليه
        pos: (x, y) مركز المخروط
        angle: زاوية الاتجاه بالدرجات
        distance: مسافة الرؤية
        angle_width: عرض زاوية الرؤية بالدرجات
        color: لون المخروط (اختياري)
    """
    if color is None:
        color = (*YELLOW, 80)  # لون افتراضي مع شفافية
    
    half_angle = angle_width / 2
    points = [pos]
    
    # زيادة دقة الرسم
    steps = max(5, int(angle_width // 5))
    for i in range(steps + 1):
        current_angle = -half_angle + (i * angle_width / steps)
        rad = math.radians(angle + current_angle)
        end_x = pos[0] + distance * math.cos(rad)
        end_y = pos[1] + distance * math.sin(rad)
        points.append((end_x, end_y))
    
    # إنشاء سطح شفاف للمخروط
    cone_surface = pygame.Surface((distance*2, distance*2), pygame.SRCALPHA)
    
    # رسم المخروط الرئيسي
    pygame.draw.polygon(cone_surface, color,
                      [(p[0]-pos[0]+distance, p[1]-pos[1]+distance) for p in points])
    
    # إضافة حدود للمخروط
    pygame.draw.polygon(cone_surface, (*color[:3], min(200, color[3]+40)),
                      [(p[0]-pos[0]+distance, p[1]-pos[1]+distance) for p in points], 2)
    
    # إضافة تأثير إشعاعي
    for r in range(distance//4, 0, -distance//20):
        alpha = max(10, color[3] - r*2)
        pygame.draw.circle(cone_surface, (*color[:3], alpha),
                          (distance, distance), r)
    
    # رسم المخروط على السطح الرئيسي
    surface.blit(cone_surface, (pos[0]-distance, pos[1]-distance))

def distance(p1, p2):
    """
    حساب المسافة الإقليدية بين نقطتين
    
    Args:
        p1: (x, y) النقطة الأولى
        p2: (x, y) النقطة الثانية
        
    Returns:
        float: المسافة بين النقطتين
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def angle_between(p1, p2):
    """
    حساب الزاوية بين نقطتين (بالدرجات)
    
    Args:
        p1: (x, y) النقطة الأولى
        p2: (x, y) النقطة الثانية
        
    Returns:
        float: الزاوية بالدرجات (0-360)
    """
    return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

def lerp(a, b, t):
    """
    حساب القيمة المتوسطة بين قيمتين (Linear Interpolation)
    
    Args:
        a: القيمة الأولى
        b: القيمة الثانية
        t: النسبة (0-1)
        
    Returns:
        float: القيمة المتوسطة
    """
    return a + (b - a) * t

def clamp(value, min_val, max_val):
    """
    تقييد قيمة بين حدين أدنى وأعلى
    
    Args:
        value: القيمة المدخلة
        min_val: الحد الأدنى
        max_val: الحد الأعلى
        
    Returns:
        float: القيمة المقيدة
    """
    return max(min_val, min(value, max_val))

def smoothstep(edge0, edge1, x):
    """
    دالة انتقال سلسة بين قيمتين
    
    Args:
        edge0: الحد الأدنى
        edge1: الحد الأعلى
        x: القيمة المدخلة
        
    Returns:
        float: القيمة بعد التسهيل
    """
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * (3 - 2 * x)

def calculate_noise_level(speed, is_sneaking):
    """
    حساب مستوى الضوضاء بناء على سرعة الحركة وحالة التخفي
    
    Args:
        speed: سرعة الحركة الحالية
        is_sneaking: هل اللاعب في وضع التخفي؟
        
    Returns:
        float: مستوى الضوضاء (0-1)
    """
    base_noise = speed / PLAYER_SETTINGS['speed']['normal']
    if is_sneaking:
        return base_noise * PLAYER_SETTINGS['noise']['sneak_multiplier']
    return base_noise

def pulse_effect(base_value, speed, time):
    """
    تأثير النبض للعناصر الخاصة
    
    Args:
        base_value: القيمة الأساسية
        speed: سرعة النبض
        time: الوقت الحالي
        
    Returns:
        float: القيمة بعد تطبيق النبض
    """
    return base_value * (1 + 0.1 * math.sin(time * speed))

def draw_debug_line(surface, start, end, color=RED, width=1):
    """
    رسم خط للمساعدة في التصحيح (Debugging)
    
    Args:
        surface: السطح المراد الرسم عليه
        start: (x, y) نقطة البداية
        end: (x, y) نقطة النهاية
        color: لون الخط (اختياري)
        width: عرض الخط (اختياري)
    """
    if DEBUG_SETTINGS['visible']['paths']:
        pygame.draw.line(surface, color, start, end, width)

def is_point_in_circle(point, circle_center, radius):
    """
    التحقق إذا كانت النقطة داخل دائرة
    
    Args:
        point: (x, y) النقطة المطلوب التحقق منها
        circle_center: (x, y) مركز الدائرة
        radius: نصف قطر الدائرة
        
    Returns:
        bool: True إذا كانت النقطة داخل الدائرة
    """
    return distance(point, circle_center) <= radius

def rotate_point(origin, point, angle):
    """
    تدوير نقطة حول مركز معين
    
    Args:
        origin: (x, y) مركز الدوران
        point: (x, y) النقطة المراد تدويرها
        angle: زاوية الدوران بالدرجات
        
    Returns:
        tuple: (x, y) إحداثيات النقطة بعد الدوران
    """
    ox, oy = origin
    px, py = point
    
    angle_rad = math.radians(angle)
    cos_val = math.cos(angle_rad)
    sin_val = math.sin(angle_rad)
    
    qx = ox + cos_val * (px - ox) - sin_val * (py - oy)
    qy = oy + sin_val * (px - ox) + cos_val * (py - oy)
    
    return (qx, qy)

def ease_out_quad(x):
    """
    دالة تبطئ نهاية الحركة (Easing Function)
    
    Args:
        x: القيمة المدخلة (0-1)
        
    Returns:
        float: القيمة بعد التبطيئ
    """
    return 1 - (1 - x) * (1 - x)

def calculate_light_intensity(distance, max_distance):
    """
    حساب شدة الإضاءة بناء على المسافة
    
    Args:
        distance: المسافة الحالية
        max_distance: أقصى مسافة تأثير
        
    Returns:
        float: شدة الإضاءة (0-1)
    """
    return clamp(1 - (distance / max_distance)**2, 0, 1)

def get_angled_offset(angle, distance):
    """
    الحصول على إزاحة في اتجاه معين
    
    Args:
        angle: زاوية الاتجاه بالدرجات
        distance: مسافة الإزاحة
        
    Returns:
        tuple: (x_offset, y_offset)
    """
    rad = math.radians(angle)
    return (math.cos(rad) * distance, math.sin(rad) * distance)