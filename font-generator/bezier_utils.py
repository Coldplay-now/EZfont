#!/usr/bin/env python3
"""
贝塞尔曲线工具库
提供字体设计所需的曲线计算、平滑、圆角等功能
"""

import math
from typing import Tuple, List, Optional

Point = Tuple[float, float]


def distance(p1: Point, p2: Point) -> float:
    """计算两点之间的距离"""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def lerp(p1: Point, p2: Point, t: float) -> Point:
    """线性插值"""
    return (
        p1[0] + (p2[0] - p1[0]) * t,
        p1[1] + (p2[1] - p1[1]) * t
    )


def normalize_vector(v: Point) -> Point:
    """向量归一化"""
    length = math.sqrt(v[0] ** 2 + v[1] ** 2)
    if length == 0:
        return (0, 0)
    return (v[0] / length, v[1] / length)


def perpendicular(v: Point, clockwise: bool = True) -> Point:
    """获取垂直向量"""
    if clockwise:
        return (v[1], -v[0])
    else:
        return (-v[1], v[0])


def add_points(p1: Point, p2: Point) -> Point:
    """点加法"""
    return (p1[0] + p2[0], p1[1] + p2[1])


def scale_point(p: Point, scale: float) -> Point:
    """点缩放"""
    return (p[0] * scale, p[1] * scale)


def bezier_point(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    """
    计算三次贝塞尔曲线上的点
    p0: 起点
    p1, p2: 控制点
    p3: 终点
    t: 参数 (0-1)
    """
    t1 = 1 - t
    x = (t1 ** 3 * p0[0] +
         3 * t1 ** 2 * t * p1[0] +
         3 * t1 * t ** 2 * p2[0] +
         t ** 3 * p3[0])
    y = (t1 ** 3 * p0[1] +
         3 * t1 ** 2 * t * p1[1] +
         3 * t1 * t ** 2 * p2[1] +
         t ** 3 * p3[1])
    return (x, y)


def quadratic_bezier_point(p0: Point, p1: Point, p2: Point, t: float) -> Point:
    """
    计算二次贝塞尔曲线上的点
    p0: 起点
    p1: 控制点
    p2: 终点
    t: 参数 (0-1)
    """
    t1 = 1 - t
    x = t1 ** 2 * p0[0] + 2 * t1 * t * p1[0] + t ** 2 * p2[0]
    y = t1 ** 2 * p0[1] + 2 * t1 * t * p1[1] + t ** 2 * p2[1]
    return (x, y)


def smooth_corner_bezier(p0: Point, p_corner: Point, p2: Point, 
                         radius: float) -> Tuple[Point, Point, Point]:
    """
    在拐角处生成圆滑的贝塞尔曲线控制点
    
    返回: (起点, 控制点, 终点)
    """
    # 计算从拐角到两个邻点的向量
    v1 = (p0[0] - p_corner[0], p0[1] - p_corner[1])
    v2 = (p2[0] - p_corner[0], p2[1] - p_corner[1])
    
    # 归一化
    v1_norm = normalize_vector(v1)
    v2_norm = normalize_vector(v2)
    
    # 计算圆角的起点和终点
    start = add_points(p_corner, scale_point(v1_norm, radius))
    end = add_points(p_corner, scale_point(v2_norm, radius))
    
    # 控制点位于拐角处（简化版本）
    # 更复杂的实现可以使用圆弧拟合
    control = p_corner
    
    return (start, control, end)


def offset_line(p1: Point, p2: Point, offset: float, side: str = 'right') -> Tuple[Point, Point]:
    """
    将线段沿垂直方向偏移
    
    side: 'right' 或 'left'
    """
    direction = (p2[0] - p1[0], p2[1] - p1[1])
    perp = perpendicular(direction, clockwise=(side == 'right'))
    perp_norm = normalize_vector(perp)
    
    offset_vector = scale_point(perp_norm, offset)
    
    new_p1 = add_points(p1, offset_vector)
    new_p2 = add_points(p2, offset_vector)
    
    return (new_p1, new_p2)


def create_stroke_outline(skeleton_points: List[Point], 
                          stroke_width: float,
                          closed: bool = False) -> Tuple[List[Point], List[Point]]:
    """
    从骨架路径创建笔画轮廓
    
    返回: (左侧轮廓点, 右侧轮廓点)
    """
    if len(skeleton_points) < 2:
        return ([], [])
    
    left_points = []
    right_points = []
    half_width = stroke_width / 2
    
    for i in range(len(skeleton_points) - 1):
        p1 = skeleton_points[i]
        p2 = skeleton_points[i + 1]
        
        left_p1, left_p2 = offset_line(p1, p2, half_width, 'left')
        right_p1, right_p2 = offset_line(p1, p2, half_width, 'right')
        
        if i == 0:
            left_points.append(left_p1)
            right_points.append(right_p1)
        
        left_points.append(left_p2)
        right_points.append(right_p2)
    
    if closed and len(skeleton_points) > 2:
        # 闭合路径，连接首尾
        p1 = skeleton_points[-1]
        p2 = skeleton_points[0]
        left_p1, left_p2 = offset_line(p1, p2, half_width, 'left')
        right_p1, right_p2 = offset_line(p1, p2, half_width, 'right')
    
    return (left_points, right_points)


def apply_contrast(stroke_width: float, angle: float, contrast: str) -> float:
    """
    根据角度和对比度参数调整笔画宽度
    
    angle: 笔画角度 (弧度)
    contrast: 'none', 'low', 'medium', 'high'
    """
    contrast_factors = {
        'none': 0.0,
        'low': 0.15,
        'medium': 0.3,
        'high': 0.5
    }
    
    factor = contrast_factors.get(contrast, 0.0)
    
    # 垂直笔画保持原宽度，水平笔画减小
    # angle = 0 (水平), angle = π/2 (垂直)
    angle_factor = abs(math.sin(angle))  # 0 for horizontal, 1 for vertical
    
    adjusted_width = stroke_width * (1 - factor * (1 - angle_factor))
    
    return adjusted_width


def create_rounded_rectangle(x: float, y: float, width: float, height: float, 
                            corner_radius: float) -> List[Tuple[str, List[Point]]]:
    """
    创建圆角矩形的路径
    
    返回: [(命令, 点列表), ...]
    命令: 'M' (moveTo), 'L' (lineTo), 'Q' (quadTo)
    """
    # 限制圆角半径
    max_radius = min(width, height) / 2
    r = min(corner_radius, max_radius)
    
    path = []
    
    # 从左上角开始（经过圆角）
    path.append(('M', [(x + r, y)]))
    
    # 上边
    path.append(('L', [(x + width - r, y)]))
    
    # 右上角
    if r > 0:
        path.append(('Q', [(x + width, y), (x + width, y + r)]))
    
    # 右边
    path.append(('L', [(x + width, y + height - r)]))
    
    # 右下角
    if r > 0:
        path.append(('Q', [(x + width, y + height), (x + width - r, y + height)]))
    
    # 下边
    path.append(('L', [(x + r, y + height)]))
    
    # 左下角
    if r > 0:
        path.append(('Q', [(x, y + height), (x, y + height - r)]))
    
    # 左边
    path.append(('L', [(x, y + r)]))
    
    # 左上角
    if r > 0:
        path.append(('Q', [(x, y), (x + r, y)]))
    
    return path


def create_ellipse_points(cx: float, cy: float, rx: float, ry: float, 
                         segments: int = 8) -> List[Tuple[str, List[Point]]]:
    """
    创建椭圆的贝塞尔曲线近似
    
    cx, cy: 中心点
    rx, ry: 半径
    segments: 分段数（通常为4或8）
    """
    # 使用4段三次贝塞尔曲线近似圆
    # 魔数：0.5522847498 用于圆的贝塞尔近似
    kappa = 0.5522847498
    
    path = []
    
    # 右侧点
    path.append(('M', [(cx + rx, cy)]))
    
    # 第一段：右->上
    path.append(('C', [
        (cx + rx, cy - ry * kappa),
        (cx + rx * kappa, cy - ry),
        (cx, cy - ry)
    ]))
    
    # 第二段：上->左
    path.append(('C', [
        (cx - rx * kappa, cy - ry),
        (cx - rx, cy - ry * kappa),
        (cx - rx, cy)
    ]))
    
    # 第三段：左->下
    path.append(('C', [
        (cx - rx, cy + ry * kappa),
        (cx - rx * kappa, cy + ry),
        (cx, cy + ry)
    ]))
    
    # 第四段：下->右
    path.append(('C', [
        (cx + rx * kappa, cy + ry),
        (cx + rx, cy + ry * kappa),
        (cx + rx, cy)
    ]))
    
    return path


def apply_slant(point: Point, angle: float, pivot_y: float = 0) -> Point:
    """
    应用倾斜变换（用于斜体）
    
    angle: 倾斜角度（弧度）
    pivot_y: 倾斜轴的y坐标
    """
    x, y = point
    dx = (y - pivot_y) * math.tan(angle)
    return (x + dx, y)


def rotate_point(point: Point, angle: float, center: Point = (0, 0)) -> Point:
    """
    绕中心点旋转
    
    angle: 旋转角度（弧度）
    """
    x, y = point
    cx, cy = center
    
    # 平移到原点
    x -= cx
    y -= cy
    
    # 旋转
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    # 平移回去
    return (new_x + cx, new_y + cy)
