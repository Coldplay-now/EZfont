#!/usr/bin/env python3
"""
专业字形设计器
为每个字符创建参数化的贝塞尔曲线字形
"""

import math
from typing import Dict, List, Tuple, Optional
from fontTools.pens.ttGlyphPen import TTGlyphPen
import bezier_utils as bez

Point = Tuple[float, float]


class GlyphDesigner:
    """
    参数化字形设计器
    根据设计参数生成专业级字形
    """
    
    def __init__(self, design_params: Dict):
        """
        初始化设计器
        
        design_params包含:
        - metrics: 字体度量信息
        - proportions: 比例信息（strokeWidth, contrast等）
        - visualStyle: 视觉样式（terminals, corners等）
        """
        self.metrics = design_params.get('metrics', {})
        self.proportions = design_params.get('proportions', {})
        self.visual_style = design_params.get('visualStyle', {})
        
        # 提取关键参数
        self.units_per_em = self.metrics.get('unitsPerEm', 1000)
        self.cap_height = self.metrics.get('capHeight', 750)
        self.x_height = self.metrics.get('xHeight', 550)
        self.ascender = self.metrics.get('ascender', 850)
        self.descender = self.metrics.get('descender', -220)
        
        self.stroke_width = self.proportions.get('strokeWidth', 80)
        self.contrast = self.proportions.get('contrast', 'medium')
        
        self.terminals = self.visual_style.get('terminals', 'straight')
        self.corners = self.visual_style.get('corners', 'rounded')
        self.aperture = self.visual_style.get('aperture', 'open')
        self.axis = self.visual_style.get('axis', 'vertical')
        self.stress = self.visual_style.get('stress', 'none')
        
        # 计算派生参数
        self.corner_radius = self._calculate_corner_radius()
        self.horizontal_stroke = self._calculate_horizontal_stroke()
        
    def _calculate_corner_radius(self) -> float:
        """根据corners参数计算圆角半径"""
        corner_factors = {
            'sharp': 0.0,
            'rounded': 0.3,
            'soft': 0.5
        }
        factor = corner_factors.get(self.corners, 0.3)
        return self.stroke_width * factor
    
    def _calculate_horizontal_stroke(self) -> float:
        """根据contrast参数计算水平笔画宽度（增强视觉差异）"""
        contrast_factors = {
            'none': 1.0,
            'low': 0.75,    # 从0.85改为0.75，增强差异
            'medium': 0.6,  # 从0.70改为0.60
            'high': 0.4     # 从0.50改为0.40
        }
        factor = contrast_factors.get(self.contrast, 0.7)
        return self.stroke_width * factor
    
    def _apply_terminal(self, pen: TTGlyphPen, p1: Point, p2: Point, 
                       terminal_type: str = 'end'):
        """
        应用笔画末端样式
        
        terminal_type: 'start' 或 'end'
        """
        if self.terminals == 'straight':
            # 直接连接
            pen.lineTo(p2)
        elif self.terminals == 'curved':
            # 添加圆形末端
            direction = (p2[0] - p1[0], p2[1] - p1[1])
            length = math.sqrt(direction[0]**2 + direction[1]**2)
            if length > 0:
                norm_dir = (direction[0]/length, direction[1]/length)
                perp = bez.perpendicular(norm_dir)
                
                # 控制点用于创建圆弧
                control_offset = self.stroke_width * 0.276  # 圆弧近似常数
                cp = bez.add_points(p1, bez.scale_point(perp, control_offset))
                pen.qCurveTo(cp, p2)
            else:
                pen.lineTo(p2)
        elif self.terminals == 'angled':
            # 斜切末端
            mid = bez.lerp(p1, p2, 0.7)
            pen.lineTo(mid)
            pen.lineTo(p2)
        else:
            pen.lineTo(p2)
    
    def create_glyph(self, char: str, width: float, height: float) -> Tuple[any, float]:
        """
        创建单个字符的字形
        
        返回: (TTGlyph对象, 左侧边距)
        """
        pen = TTGlyphPen(None)
        margin = width * 0.1
        
        # 根据字符调用相应的设计方法
        if char.isupper():
            glyph_func = getattr(self, f'_create_{char.lower()}', None)
            if glyph_func:
                glyph_func(pen, width, height, margin, is_upper=True)
            else:
                self._create_default_uppercase(pen, width, height, margin, char)
        elif char.islower():
            glyph_func = getattr(self, f'_create_{char}', None)
            if glyph_func:
                glyph_func(pen, width, height, margin, is_upper=False)
            else:
                self._create_default_lowercase(pen, width, height, margin, char)
        elif char.isdigit():
            glyph_func = getattr(self, f'_create_digit_{char}', None)
            if glyph_func:
                glyph_func(pen, width, height, margin)
            else:
                self._create_default_digit(pen, width, height, margin, char)
        else:
            self._create_punctuation(pen, char, width, height, margin)
        
        return pen.glyph(), margin
    
    # ==================== 大写字母设计 ====================
    
    def _create_a(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母A的设计 - 应用corners参数到顶点"""
        if is_upper:
            # 大写A：三角形结构
            stroke = self.stroke_width
            half_stroke = stroke / 2
            corner_r = self.corner_radius
            
            # 顶点
            apex_x = w / 2
            apex_y = h
            
            # 底部外侧点
            left_bottom = (m, 0)
            right_bottom = (w - m, 0)
            
            # 底部内侧点（考虑笔画宽度）
            left_inner = (m + stroke * 0.7, 0)
            right_inner = (w - m - stroke * 0.7, 0)
            
            # 顶部内侧点
            apex_inner_left = (apex_x - half_stroke, h - stroke)
            apex_inner_right = (apex_x + half_stroke, h - stroke)
            
            # 外轮廓 - 应用corners参数
            pen.moveTo(left_bottom)
            if corner_r > 0:
                # 应用圆角到顶点
                pen.lineTo((apex_x - half_stroke - corner_r, apex_y - corner_r))
                pen.qCurveTo((apex_x - half_stroke, apex_y), (apex_x, apex_y))
                pen.qCurveTo((apex_x + half_stroke, apex_y), (apex_x + half_stroke + corner_r, apex_y - corner_r))
                pen.lineTo(right_bottom)
            else:
                # 尖角
                pen.lineTo((apex_x - half_stroke, apex_y))
                pen.lineTo((apex_x + half_stroke, apex_y))
                pen.lineTo(right_bottom)
            
            # 横杠 - 使用horizontal_stroke体现contrast
            crossbar_y = h * 0.4
            crossbar_h = self.horizontal_stroke
            pen.lineTo((w - m - stroke * 0.5, crossbar_y))
            pen.lineTo((w - m - stroke * 0.5, crossbar_y + crossbar_h))
            pen.lineTo((m + stroke * 0.5, crossbar_y + crossbar_h))
            pen.lineTo((m + stroke * 0.5, crossbar_y))
            
            # 回到起点
            pen.lineTo(right_inner)
            if corner_r > 0:
                pen.lineTo((apex_inner_right[0] + corner_r, apex_inner_right[1]))
                pen.lineTo((apex_inner_left[0] - corner_r, apex_inner_left[1]))
            else:
                pen.lineTo(apex_inner_right)
                pen.lineTo(apex_inner_left)
            pen.lineTo(left_inner)
            pen.closePath()
        else:
            # 小写a：圆形+竖杆
            self._create_default_lowercase(pen, w, h, m, 'a')
    
    def _create_b(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母B的设计（大写和小写）"""
        if not is_upper:
            # 调用小写版本
            self._create_b_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        
        if True:  # 大写B
            # 大写B：垂直杆+两个碗
            # 左侧垂直杆
            pen.moveTo((m, 0))
            pen.lineTo((m + stroke, 0))
            pen.lineTo((m + stroke, h))
            pen.lineTo((m, h))
            pen.closePath()
            
            # 上碗
            bowl_width = w - m - stroke - m
            bowl_center_x = m + stroke + bowl_width / 2
            upper_bowl_y = h * 0.5
            
            # 使用椭圆近似
            rx = bowl_width / 2
            ry = h * 0.25
            cy = h * 0.75
            
            # 简化的碗形（实际应该用贝塞尔曲线）
            pen.moveTo((m + stroke, h))
            pen.lineTo((w - m, h - ry * 0.2))
            pen.qCurveTo((w - m, cy), (bowl_center_x, upper_bowl_y))
            pen.qCurveTo((m + stroke, upper_bowl_y), (m + stroke, upper_bowl_y + ry * 0.1))
            pen.closePath()
            
            # 下碗
            lower_bowl_y = h * 0.25
            cy2 = h * 0.35
            pen.moveTo((m + stroke, upper_bowl_y))
            pen.lineTo((w - m, upper_bowl_y - ry * 0.1))
            pen.qCurveTo((w - m, lower_bowl_y), (bowl_center_x, 0))
            pen.qCurveTo((m + stroke, 0), (m + stroke, ry * 0.1))
            pen.closePath()
    
    def _create_o(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母O的设计"""
        # O字母：椭圆
        cx = w / 2
        cy = h / 2
        rx = (w - 2 * m) / 2
        ry = h / 2
        
        # 应用stress参数调整椭圆
        if self.stress == 'vertical':
            # 垂直应力：上下粗，左右细
            outer_rx = rx
            outer_ry = ry
            inner_rx = rx - self.stroke_width
            inner_ry = ry - self.horizontal_stroke
        else:
            # 无应力或其他：均匀笔画
            outer_rx = rx
            outer_ry = ry
            inner_rx = rx - self.stroke_width / 2
            inner_ry = ry - self.stroke_width / 2
        
        # 外轮廓
        kappa = 0.5522847498
        pen.moveTo((cx + outer_rx, cy))
        pen.curveTo(
            (cx + outer_rx, cy - outer_ry * kappa),
            (cx + outer_rx * kappa, cy - outer_ry),
            (cx, cy - outer_ry)
        )
        pen.curveTo(
            (cx - outer_rx * kappa, cy - outer_ry),
            (cx - outer_rx, cy - outer_ry * kappa),
            (cx - outer_rx, cy)
        )
        pen.curveTo(
            (cx - outer_rx, cy + outer_ry * kappa),
            (cx - outer_rx * kappa, cy + outer_ry),
            (cx, cy + outer_ry)
        )
        pen.curveTo(
            (cx + outer_rx * kappa, cy + outer_ry),
            (cx + outer_rx, cy + outer_ry * kappa),
            (cx + outer_rx, cy)
        )
        pen.closePath()
        
        # 内轮廓（反向）
        pen.moveTo((cx + inner_rx, cy))
        pen.curveTo(
            (cx + inner_rx, cy + inner_ry * kappa),
            (cx + inner_rx * kappa, cy + inner_ry),
            (cx, cy + inner_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, cy + inner_ry),
            (cx - inner_rx, cy + inner_ry * kappa),
            (cx - inner_rx, cy)
        )
        pen.curveTo(
            (cx - inner_rx, cy - inner_ry * kappa),
            (cx - inner_rx * kappa, cy - inner_ry),
            (cx, cy - inner_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, cy - inner_ry),
            (cx + inner_rx, cy - inner_ry * kappa),
            (cx + inner_rx, cy)
        )
        pen.closePath()
    
    def _create_c(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母C的设计"""
        cx = w / 2
        cy = h / 2
        rx = (w - 2 * m) / 2
        ry = h / 2
        
        # C字母：开口的圆形
        outer_rx = rx
        outer_ry = ry
        inner_rx = rx - self.stroke_width
        inner_ry = ry - self.stroke_width
        
        # 开口角度
        aperture_factors = {'closed': 0.1, 'semi-open': 0.25, 'open': 0.4}
        aperture_angle = aperture_factors.get(self.aperture, 0.25)
        
        kappa = 0.5522847498
        
        # 外轮廓（从开口开始）
        start_angle = aperture_angle * math.pi
        pen.moveTo((cx + outer_rx * math.cos(start_angle), cy - outer_ry * math.sin(start_angle)))
        
        # 下半圆
        pen.curveTo(
            (cx + outer_rx, cy + outer_ry * kappa),
            (cx + outer_rx * kappa, cy + outer_ry),
            (cx, cy + outer_ry)
        )
        # 左半圆
        pen.curveTo(
            (cx - outer_rx * kappa, cy + outer_ry),
            (cx - outer_rx, cy + outer_ry * kappa),
            (cx - outer_rx, cy)
        )
        # 上半圆
        pen.curveTo(
            (cx - outer_rx, cy - outer_ry * kappa),
            (cx - outer_rx * kappa, cy - outer_ry),
            (cx, cy - outer_ry)
        )
        # 到开口
        pen.curveTo(
            (cx + outer_rx * kappa, cy - outer_ry),
            (cx + outer_rx, cy - outer_ry * kappa),
            (cx + outer_rx * math.cos(-start_angle), cy - outer_ry * math.sin(-start_angle))
        )
        
        # 内轮廓
        pen.lineTo((cx + inner_rx * math.cos(-start_angle), cy - inner_ry * math.sin(-start_angle)))
        pen.curveTo(
            (cx + inner_rx, cy - inner_ry * kappa),
            (cx + inner_rx * kappa, cy - inner_ry),
            (cx, cy - inner_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, cy - inner_ry),
            (cx - inner_rx, cy - inner_ry * kappa),
            (cx - inner_rx, cy)
        )
        pen.curveTo(
            (cx - inner_rx, cy + inner_ry * kappa),
            (cx - inner_rx * kappa, cy + inner_ry),
            (cx, cy + inner_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, cy + inner_ry),
            (cx + inner_rx, cy + inner_ry * kappa),
            (cx + inner_rx * math.cos(start_angle), cy - inner_ry * math.sin(start_angle))
        )
        pen.closePath()
    
    def _create_d(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母D的设计（大写和小写）"""
        if not is_upper:
            self._create_d_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 右侧弧形（合并内外轮廓为一个路径）
        cx = w - m - (w - 2 * m - stroke) / 2
        cy = h / 2
        rx = (w - 2 * m - stroke) / 2
        ry = h / 2
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        
        kappa = 0.5522847498
        
        # 从外轮廓开始
        pen.moveTo((m + stroke, h))
        pen.lineTo((cx, h))
        pen.curveTo(
            (cx + rx * kappa, h),
            (cx + rx, cy + ry * kappa),
            (cx + rx, cy)
        )
        pen.curveTo(
            (cx + rx, cy - ry * kappa),
            (cx + rx * kappa, 0),
            (cx, 0)
        )
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, stroke))
        
        # 内轮廓（反向）
        pen.lineTo((cx, stroke))
        pen.curveTo(
            (cx + inner_rx * kappa, stroke),
            (cx + inner_rx, cy - inner_ry * kappa),
            (cx + inner_rx, cy)
        )
        pen.curveTo(
            (cx + inner_rx, cy + inner_ry * kappa),
            (cx + inner_rx * kappa, h - stroke),
            (cx, h - stroke)
        )
        pen.lineTo((m + stroke, h - stroke))
        pen.lineTo((m + stroke, h))
        pen.closePath()
    
    def _create_e(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母E的设计 - 应用terminals参数到横杠末端（大写和小写）"""
        if not is_upper:
            self._create_e_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        corner_r = self.corner_radius
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 顶部横杆 - 应用terminals到右侧末端
        pen.moveTo((m, h - h_stroke))
        if self.terminals == 'curved':
            # 圆形末端
            pen.lineTo((w - m - stroke/4, h - h_stroke))
            pen.qCurveTo((w - m, h - h_stroke), (w - m, h - h_stroke/2))
            pen.qCurveTo((w - m, h), (w - m - stroke/4, h))
        elif self.terminals == 'angled':
            # 斜切末端
            pen.lineTo((w - m - stroke/3, h - h_stroke))
            pen.lineTo((w - m, h - h_stroke * 0.7))
            pen.lineTo((w - m, h))
            pen.lineTo((w - m - stroke/3, h))
        else:
            # straight末端
            pen.lineTo((w - m, h - h_stroke))
            pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 中间横杆 - 应用terminals到右侧末端
        pen.moveTo((m, h / 2 - h_stroke / 2))
        if self.terminals == 'curved':
            pen.lineTo((w - m * 2 - stroke/4, h / 2 - h_stroke / 2))
            pen.qCurveTo((w - m * 2, h / 2 - h_stroke / 2), (w - m * 2, h / 2))
            pen.qCurveTo((w - m * 2, h / 2 + h_stroke / 2), (w - m * 2 - stroke/4, h / 2 + h_stroke / 2))
        elif self.terminals == 'angled':
            pen.lineTo((w - m * 2 - stroke/3, h / 2 - h_stroke / 2))
            pen.lineTo((w - m * 2, h / 2))
            pen.lineTo((w - m * 2 - stroke/3, h / 2 + h_stroke / 2))
        else:
            pen.lineTo((w - m * 2, h / 2 - h_stroke / 2))
            pen.lineTo((w - m * 2, h / 2 + h_stroke / 2))
        pen.lineTo((m, h / 2 + h_stroke / 2))
        pen.closePath()
        
        # 底部横杆 - 应用terminals到右侧末端
        pen.moveTo((m, 0))
        if self.terminals == 'curved':
            pen.lineTo((w - m - stroke/4, 0))
            pen.qCurveTo((w - m, 0), (w - m, h_stroke/2))
            pen.qCurveTo((w - m, h_stroke), (w - m - stroke/4, h_stroke))
        elif self.terminals == 'angled':
            pen.lineTo((w - m - stroke/3, 0))
            pen.lineTo((w - m, h_stroke * 0.3))
            pen.lineTo((w - m, h_stroke))
            pen.lineTo((w - m - stroke/3, h_stroke))
        else:
            pen.lineTo((w - m, 0))
            pen.lineTo((w - m, h_stroke))
        pen.lineTo((m, h_stroke))
        pen.closePath()
    
    def _create_f(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母F的设计 - 应用terminals参数到横杠末端"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 顶部横杆 - 应用terminals
        pen.moveTo((m, h - h_stroke))
        if self.terminals == 'curved':
            pen.lineTo((w - m - stroke/4, h - h_stroke))
            pen.qCurveTo((w - m, h - h_stroke), (w - m, h - h_stroke/2))
            pen.qCurveTo((w - m, h), (w - m - stroke/4, h))
        elif self.terminals == 'angled':
            pen.lineTo((w - m - stroke/3, h - h_stroke))
            pen.lineTo((w - m, h - h_stroke * 0.7))
            pen.lineTo((w - m, h))
            pen.lineTo((w - m - stroke/3, h))
        else:
            pen.lineTo((w - m, h - h_stroke))
            pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 中间横杆 - 应用terminals
        pen.moveTo((m, h / 2 - h_stroke / 2))
        if self.terminals == 'curved':
            pen.lineTo((w - m * 2 - stroke/4, h / 2 - h_stroke / 2))
            pen.qCurveTo((w - m * 2, h / 2 - h_stroke / 2), (w - m * 2, h / 2))
            pen.qCurveTo((w - m * 2, h / 2 + h_stroke / 2), (w - m * 2 - stroke/4, h / 2 + h_stroke / 2))
        elif self.terminals == 'angled':
            pen.lineTo((w - m * 2 - stroke/3, h / 2 - h_stroke / 2))
            pen.lineTo((w - m * 2, h / 2))
            pen.lineTo((w - m * 2 - stroke/3, h / 2 + h_stroke / 2))
        else:
            pen.lineTo((w - m * 2, h / 2 - h_stroke / 2))
            pen.lineTo((w - m * 2, h / 2 + h_stroke / 2))
        pen.lineTo((m, h / 2 + h_stroke / 2))
        pen.closePath()
    
    def _create_g(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母G的设计（类似C but with 横杆）"""
        self._create_c(pen, w, h, m, is_upper)
        
        # 添加右侧横杆
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        pen.moveTo((w / 2, h / 2 - h_stroke / 2))
        pen.lineTo((w - m, h / 2 - h_stroke / 2))
        pen.lineTo((w - m, h / 2 + h_stroke / 2))
        pen.lineTo((w / 2, h / 2 + h_stroke / 2))
        pen.closePath()
    
    def _create_h(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母H的设计"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 右侧垂直杆
        pen.moveTo((w - m - stroke, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke, h))
        pen.closePath()
        
        # 中间横杆
        pen.moveTo((m, h / 2 - h_stroke / 2))
        pen.lineTo((w - m, h / 2 - h_stroke / 2))
        pen.lineTo((w - m, h / 2 + h_stroke / 2))
        pen.lineTo((m, h / 2 + h_stroke / 2))
        pen.closePath()
    
    def _create_i(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母I的设计 - 应用terminals参数到横杠末端（大写和小写）"""
        if not is_upper:
            self._create_i_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        center_x = w / 2
        
        # 中间垂直杆
        pen.moveTo((center_x - stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, h))
        pen.lineTo((center_x - stroke / 2, h))
        pen.closePath()
        
        if True:  # 大写I的横杠
            h_stroke = self.horizontal_stroke
            # 顶部横杆 - 应用terminals到两端
            pen.moveTo((m, h - h_stroke))
            if self.terminals == 'curved':
                pen.lineTo((w - m - stroke/4, h - h_stroke))
                pen.qCurveTo((w - m, h - h_stroke), (w - m, h - h_stroke/2))
                pen.qCurveTo((w - m, h), (w - m - stroke/4, h))
                pen.lineTo((m + stroke/4, h))
                pen.qCurveTo((m, h), (m, h - h_stroke/2))
                pen.qCurveTo((m, h - h_stroke), (m + stroke/4, h - h_stroke))
            elif self.terminals == 'angled':
                pen.lineTo((w - m - stroke/3, h - h_stroke))
                pen.lineTo((w - m, h - h_stroke * 0.7))
                pen.lineTo((w - m, h))
                pen.lineTo((m, h))
                pen.lineTo((m + stroke/3, h - h_stroke * 0.7))
                pen.lineTo((m + stroke/3, h - h_stroke))
            else:
                pen.lineTo((w - m, h - h_stroke))
                pen.lineTo((w - m, h))
                pen.lineTo((m, h))
            pen.closePath()
            
            # 底部横杆 - 应用terminals到两端
            pen.moveTo((m, 0))
            if self.terminals == 'curved':
                pen.lineTo((w - m - stroke/4, 0))
                pen.qCurveTo((w - m, 0), (w - m, h_stroke/2))
                pen.qCurveTo((w - m, h_stroke), (w - m - stroke/4, h_stroke))
                pen.lineTo((m + stroke/4, h_stroke))
                pen.qCurveTo((m, h_stroke), (m, h_stroke/2))
                pen.qCurveTo((m, 0), (m + stroke/4, 0))
            elif self.terminals == 'angled':
                pen.lineTo((w - m - stroke/3, 0))
                pen.lineTo((w - m, h_stroke * 0.3))
                pen.lineTo((w - m, h_stroke))
                pen.lineTo((m, h_stroke))
                pen.lineTo((m + stroke/3, h_stroke * 0.3))
                pen.lineTo((m + stroke/3, 0))
            else:
                pen.lineTo((w - m, 0))
                pen.lineTo((w - m, h_stroke))
                pen.lineTo((m, h_stroke))
            pen.closePath()
    
    def _create_j(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母J的设计"""
        stroke = self.stroke_width
        
        if is_upper:
            # 顶部横杆
            h_stroke = self.horizontal_stroke
            pen.moveTo((m, h - h_stroke))
            pen.lineTo((w - m, h - h_stroke))
            pen.lineTo((w - m, h))
            pen.lineTo((m, h))
            pen.closePath()
        
        # 垂直部分
        pen.moveTo((w - m - stroke, h / 4))
        pen.lineTo((w - m, h / 4))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke, h))
        pen.closePath()
        
        # 底部弧形
        cx = w / 2
        cy = h / 4
        rx = (w - 2 * m - stroke) / 2
        ry = h / 4
        
        kappa = 0.5522847498
        pen.moveTo((w - m - stroke, cy))
        pen.curveTo(
            (w - m - stroke, cy + ry * kappa),
            (cx + rx * kappa, cy + ry),
            (cx, cy + ry)
        )
        pen.curveTo(
            (cx - rx * kappa, cy + ry),
            (m + stroke, cy + ry * kappa),
            (m + stroke, cy)
        )
        pen.lineTo((m, cy))
        pen.curveTo(
            (m, cy + (ry + stroke) * kappa),
            (cx - (rx + stroke) * kappa, cy + ry + stroke),
            (cx, cy + ry + stroke)
        )
        pen.curveTo(
            (cx + (rx + stroke) * kappa, cy + ry + stroke),
            (w - m, cy + (ry + stroke) * kappa),
            (w - m, cy)
        )
        pen.closePath()
    
    def _create_k(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母K的设计"""
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 上斜线
        pen.moveTo((m + stroke, h / 2))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke * 0.7, h))
        pen.lineTo((m + stroke * 1.5, h / 2))
        pen.closePath()
        
        # 下斜线
        pen.moveTo((m + stroke, h / 2))
        pen.lineTo((m + stroke * 1.5, h / 2))
        pen.lineTo((w - m - stroke * 0.7, 0))
        pen.lineTo((w - m, 0))
        pen.closePath()
    
    def _create_l(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母L的设计 - 应用terminals参数到横杠末端（大写和小写）"""
        if not is_upper:
            self._create_l_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 底部横杆 - 应用terminals到右侧末端
        pen.moveTo((m, 0))
        if self.terminals == 'curved':
            pen.lineTo((w - m - stroke/4, 0))
            pen.qCurveTo((w - m, 0), (w - m, h_stroke/2))
            pen.qCurveTo((w - m, h_stroke), (w - m - stroke/4, h_stroke))
        elif self.terminals == 'angled':
            pen.lineTo((w - m - stroke/3, 0))
            pen.lineTo((w - m, h_stroke * 0.3))
            pen.lineTo((w - m, h_stroke))
            pen.lineTo((w - m - stroke/3, h_stroke))
        else:
            pen.lineTo((w - m, 0))
            pen.lineTo((w - m, h_stroke))
        pen.lineTo((m, h_stroke))
        pen.closePath()
    
    def _create_m(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母M的设计"""
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 左斜线
        apex_x = w / 2
        pen.moveTo((m, h))
        pen.lineTo((m + stroke * 0.7, h))
        pen.lineTo((apex_x, h / 3))
        pen.lineTo((apex_x - stroke * 0.5, h / 3))
        pen.closePath()
        
        # 右斜线
        pen.moveTo((apex_x + stroke * 0.5, h / 3))
        pen.lineTo((apex_x, h / 3))
        pen.lineTo((w - m - stroke * 0.7, h))
        pen.lineTo((w - m, h))
        pen.closePath()
        
        # 右侧垂直杆
        pen.moveTo((w - m - stroke, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke, h))
        pen.closePath()
    
    def _create_n(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母N的设计（大写和小写）"""
        if not is_upper:
            self._create_n_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 斜线
        pen.moveTo((m, h))
        pen.lineTo((m + stroke * 0.7, h))
        pen.lineTo((w - m, stroke))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m - stroke * 0.7, 0))
        pen.lineTo((m, h - stroke))
        pen.closePath()
        
        # 右侧垂直杆
        pen.moveTo((w - m - stroke, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke, h))
        pen.closePath()
    
    def _create_p(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母P的设计"""
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 上半部分的碗（合并内外轮廓）
        bowl_y_top = h
        bowl_y_bottom = h * 0.5
        cx = m + stroke + (w - m - stroke - m) / 2
        cy = (bowl_y_top + bowl_y_bottom) / 2
        rx = (w - m - stroke - m) / 2
        ry = (bowl_y_top - bowl_y_bottom) / 2
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        bowl_inner_top = bowl_y_top - stroke
        bowl_inner_bottom = bowl_y_bottom + stroke
        cy_inner = (bowl_inner_top + bowl_inner_bottom) / 2
        
        kappa = 0.5522847498
        
        # 外轮廓
        pen.moveTo((m + stroke, bowl_y_top))
        pen.lineTo((cx, bowl_y_top))
        pen.curveTo(
            (cx + rx * kappa, bowl_y_top),
            (cx + rx, cy + ry * kappa),
            (cx + rx, cy)
        )
        pen.curveTo(
            (cx + rx, cy - ry * kappa),
            (cx + rx * kappa, bowl_y_bottom),
            (cx, bowl_y_bottom)
        )
        pen.lineTo((m + stroke, bowl_y_bottom))
        pen.lineTo((m + stroke, bowl_inner_bottom))
        
        # 内轮廓（反向）
        pen.lineTo((cx, bowl_inner_bottom))
        pen.curveTo(
            (cx + inner_rx * kappa, bowl_inner_bottom),
            (cx + inner_rx, cy_inner - inner_ry * kappa),
            (cx + inner_rx, cy_inner)
        )
        pen.curveTo(
            (cx + inner_rx, cy_inner + inner_ry * kappa),
            (cx + inner_rx * kappa, bowl_inner_top),
            (cx, bowl_inner_top)
        )
        pen.lineTo((m + stroke, bowl_inner_top))
        pen.lineTo((m + stroke, bowl_y_top))
        pen.closePath()
    
    def _create_q(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母Q的设计（O + 尾巴）"""
        self._create_o(pen, w, h, m, is_upper)
        
        # 添加尾巴
        stroke = self.stroke_width
        pen.moveTo((w - m - stroke, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h / 3))
        pen.lineTo((w - m - stroke, h / 3))
        pen.closePath()
    
    def _create_r(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母R的设计（大写和小写）"""
        if not is_upper:
            self._create_r_lowercase(pen, w, h, m)
            return
        
        # 先绘制P的部分
        self._create_p(pen, w, h, m, is_upper)
        
        # 添加腿
        stroke = self.stroke_width
        pen.moveTo((m + stroke + (w - m - stroke - m) / 2, h * 0.5))
        pen.lineTo((m + stroke + (w - m - stroke - m) / 2 + stroke * 0.7, h * 0.5))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m - stroke * 0.7, 0))
        pen.closePath()
    
    def _create_s(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母S的设计"""
        # S字母：简化版本，使用直线连接的两个圆形
        cx = w / 2
        upper_cy = h * 0.75
        lower_cy = h * 0.25
        rx = (w - 2 * m) / 2
        ry = h / 4
        
        stroke = self.stroke_width
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        kappa = 0.5522847498
        
        # 外轮廓：从右上开始
        pen.moveTo((cx + rx, upper_cy))
        pen.curveTo(
            (cx + rx, upper_cy + ry * kappa),
            (cx + rx * kappa, upper_cy + ry),
            (cx, upper_cy + ry)
        )
        pen.curveTo(
            (cx - rx * kappa, upper_cy + ry),
            (cx - rx, upper_cy + ry * kappa),
            (cx - rx, upper_cy)
        )
        pen.curveTo(
            (cx - rx, upper_cy - ry * kappa),
            (cx - rx * kappa, upper_cy - ry),
            (cx, upper_cy - ry)
        )
        # 连接到下半圆
        pen.lineTo((cx, lower_cy + ry))
        pen.curveTo(
            (cx + rx * kappa, lower_cy + ry),
            (cx + rx, lower_cy + ry * kappa),
            (cx + rx, lower_cy)
        )
        pen.curveTo(
            (cx + rx, lower_cy - ry * kappa),
            (cx + rx * kappa, lower_cy - ry),
            (cx, lower_cy - ry)
        )
        pen.curveTo(
            (cx - rx * kappa, lower_cy - ry),
            (cx - rx, lower_cy - ry * kappa),
            (cx - rx, lower_cy)
        )
        pen.lineTo((cx - rx, lower_cy + stroke))
        
        # 内轮廓：从左下开始（反向）
        pen.lineTo((cx - inner_rx, lower_cy))
        pen.curveTo(
            (cx - inner_rx, lower_cy - inner_ry * kappa),
            (cx - inner_rx * kappa, lower_cy - inner_ry),
            (cx, lower_cy - inner_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, lower_cy - inner_ry),
            (cx + inner_rx, lower_cy - inner_ry * kappa),
            (cx + inner_rx, lower_cy)
        )
        # 连接到上半圆
        pen.lineTo((cx + inner_rx, upper_cy))
        pen.curveTo(
            (cx + inner_rx, upper_cy + inner_ry * kappa),
            (cx + inner_rx * kappa, upper_cy + inner_ry),
            (cx, upper_cy + inner_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, upper_cy + inner_ry),
            (cx - inner_rx, upper_cy + inner_ry * kappa),
            (cx - inner_rx, upper_cy)
        )
        pen.lineTo((cx + rx, upper_cy))
        pen.closePath()
    
    def _create_t(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母T的设计 - 应用terminals参数到横杠末端（大写和小写）"""
        if not is_upper:
            self._create_t_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        center_x = w / 2
        
        # 顶部横杆 - 应用terminals到两端
        pen.moveTo((m, h - h_stroke))
        if self.terminals == 'curved':
            pen.lineTo((w - m - stroke/4, h - h_stroke))
            pen.qCurveTo((w - m, h - h_stroke), (w - m, h - h_stroke/2))
            pen.qCurveTo((w - m, h), (w - m - stroke/4, h))
            pen.lineTo((m + stroke/4, h))
            pen.qCurveTo((m, h), (m, h - h_stroke/2))
            pen.qCurveTo((m, h - h_stroke), (m + stroke/4, h - h_stroke))
        elif self.terminals == 'angled':
            pen.lineTo((w - m - stroke/3, h - h_stroke))
            pen.lineTo((w - m, h - h_stroke * 0.7))
            pen.lineTo((w - m, h))
            pen.lineTo((m, h))
            pen.lineTo((m + stroke/3, h - h_stroke * 0.7))
            pen.lineTo((m + stroke/3, h - h_stroke))
        else:
            pen.lineTo((w - m, h - h_stroke))
            pen.lineTo((w - m, h))
            pen.lineTo((m, h))
        pen.closePath()
        
        # 中间垂直杆
        pen.moveTo((center_x - stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, h))
        pen.lineTo((center_x - stroke / 2, h))
        pen.closePath()
    
    def _create_u(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母U的设计（大写和小写）"""
        if not is_upper:
            self._create_u_lowercase(pen, w, h, m)
            return
        
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, h / 3))
        pen.lineTo((m + stroke, h / 3))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 右侧垂直杆
        pen.moveTo((w - m - stroke, h / 3))
        pen.lineTo((w - m, h / 3))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke, h))
        pen.closePath()
        
        # 底部弧形
        cx = w / 2
        cy = h / 3
        rx = (w - 2 * m - stroke) / 2
        ry = h / 3
        
        kappa = 0.5522847498
        pen.moveTo((m + stroke, cy))
        pen.curveTo(
            (m + stroke, cy - ry * kappa),
            (cx - rx * kappa, cy - ry),
            (cx, cy - ry)
        )
        pen.curveTo(
            (cx + rx * kappa, cy - ry),
            (w - m - stroke, cy - ry * kappa),
            (w - m - stroke, cy)
        )
        pen.lineTo((w - m, cy))
        pen.curveTo(
            (w - m, cy - (ry + stroke) * kappa),
            (cx + (rx + stroke) * kappa, cy - ry - stroke),
            (cx, cy - ry - stroke)
        )
        pen.curveTo(
            (cx - (rx + stroke) * kappa, cy - ry - stroke),
            (m, cy - (ry + stroke) * kappa),
            (m, cy)
        )
        pen.closePath()
    
    def _create_v(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母V的设计"""
        stroke = self.stroke_width
        apex_x = w / 2
        
        # 左斜线
        pen.moveTo((m, h))
        pen.lineTo((m + stroke * 0.7, h))
        pen.lineTo((apex_x + stroke * 0.3, 0))
        pen.lineTo((apex_x - stroke * 0.3, 0))
        pen.closePath()
        
        # 右斜线
        pen.moveTo((apex_x - stroke * 0.3, 0))
        pen.lineTo((apex_x + stroke * 0.3, 0))
        pen.lineTo((w - m - stroke * 0.7, h))
        pen.lineTo((w - m, h))
        pen.closePath()
    
    def _create_w(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母W的设计（倒M）"""
        stroke = self.stroke_width
        
        # 左斜线
        pen.moveTo((m, h))
        pen.lineTo((m + stroke * 0.5, h))
        pen.lineTo((w * 0.25, 0))
        pen.lineTo((w * 0.25 - stroke * 0.3, 0))
        pen.closePath()
        
        # 左中斜线
        pen.moveTo((w * 0.25 + stroke * 0.3, 0))
        pen.lineTo((w * 0.25, 0))
        pen.lineTo((w * 0.5 - stroke * 0.3, h * 0.67))
        pen.lineTo((w * 0.5 + stroke * 0.3, h * 0.67))
        pen.closePath()
        
        # 右中斜线
        pen.moveTo((w * 0.5 - stroke * 0.3, h * 0.67))
        pen.lineTo((w * 0.5 + stroke * 0.3, h * 0.67))
        pen.lineTo((w * 0.75, 0))
        pen.lineTo((w * 0.75 - stroke * 0.3, 0))
        pen.closePath()
        
        # 右斜线
        pen.moveTo((w * 0.75 + stroke * 0.3, 0))
        pen.lineTo((w * 0.75, 0))
        pen.lineTo((w - m - stroke * 0.5, h))
        pen.lineTo((w - m, h))
        pen.closePath()
    
    def _create_x(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母X的设计"""
        stroke = self.stroke_width
        center_x = w / 2
        center_y = h / 2
        
        # 左上到右下斜线
        pen.moveTo((m, h))
        pen.lineTo((m + stroke * 0.7, h))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m - stroke * 0.7, 0))
        pen.closePath()
        
        # 右上到左下斜线
        pen.moveTo((w - m, h))
        pen.lineTo((w - m - stroke * 0.7, h))
        pen.lineTo((m, 0))
        pen.lineTo((m + stroke * 0.7, 0))
        pen.closePath()
    
    def _create_y(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母Y的设计"""
        stroke = self.stroke_width
        center_x = w / 2
        join_y = h * 0.5
        
        # 左上斜线
        pen.moveTo((m, h))
        pen.lineTo((m + stroke * 0.7, h))
        pen.lineTo((center_x + stroke * 0.3, join_y))
        pen.lineTo((center_x - stroke * 0.3, join_y))
        pen.closePath()
        
        # 右上斜线
        pen.moveTo((center_x - stroke * 0.3, join_y))
        pen.lineTo((center_x + stroke * 0.3, join_y))
        pen.lineTo((w - m - stroke * 0.7, h))
        pen.lineTo((w - m, h))
        pen.closePath()
        
        # 下方垂直杆
        pen.moveTo((center_x - stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, join_y))
        pen.lineTo((center_x - stroke / 2, join_y))
        pen.closePath()
    
    def _create_z(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母Z的设计"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 顶部横杆
        pen.moveTo((m, h - h_stroke))
        pen.lineTo((w - m, h - h_stroke))
        pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 对角线
        pen.moveTo((w - m, h - h_stroke))
        pen.lineTo((w - m - stroke * 0.7, h - h_stroke))
        pen.lineTo((m + stroke * 0.7, h_stroke))
        pen.lineTo((m, h_stroke))
        pen.closePath()
        
        # 底部横杆
        pen.moveTo((m, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h_stroke))
        pen.lineTo((m, h_stroke))
        pen.closePath()
    
    def _create_default_uppercase(self, pen: TTGlyphPen, w: float, h: float, m: float, char: str):
        """默认大写字母设计（L型）"""
        stroke = self.stroke_width
        
        # 左侧垂直杆
        pen.moveTo((m, 0))
        pen.lineTo((m + stroke, 0))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 顶部横杆
        h_stroke = self.horizontal_stroke
        pen.moveTo((m, h - h_stroke))
        pen.lineTo((w - m, h - h_stroke))
        pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
    
    # ==================== 小写字母设计 ====================
    
    def _create_a(self, pen: TTGlyphPen, w: float, h: float, m: float, is_upper: bool = False):
        """字母A/a的设计"""
        if is_upper:
            # 大写A：三角形结构
            stroke = self.stroke_width
            half_stroke = stroke / 2
            
            # 顶点
            apex_x = w / 2
            apex_y = h
            
            # 底部外侧点
            left_bottom = (m, 0)
            right_bottom = (w - m, 0)
            
            # 底部内侧点（考虑笔画宽度）
            left_inner = (m + stroke * 0.7, 0)
            right_inner = (w - m - stroke * 0.7, 0)
            
            # 顶部内侧点
            apex_inner_left = (apex_x - half_stroke, h - stroke)
            apex_inner_right = (apex_x + half_stroke, h - stroke)
            
            # 外轮廓
            pen.moveTo(left_bottom)
            pen.lineTo((apex_x - half_stroke, apex_y))
            pen.lineTo((apex_x + half_stroke, apex_y))
            pen.lineTo(right_bottom)
            
            # 横杠
            crossbar_y = h * 0.4
            crossbar_h = self.horizontal_stroke
            pen.lineTo((w - m - stroke * 0.5, crossbar_y))
            pen.lineTo((w - m - stroke * 0.5, crossbar_y + crossbar_h))
            pen.lineTo((m + stroke * 0.5, crossbar_y + crossbar_h))
            pen.lineTo((m + stroke * 0.5, crossbar_y))
            
            # 回到起点
            pen.lineTo(right_inner)
            pen.lineTo(apex_inner_right)
            pen.lineTo(apex_inner_left)
            pen.lineTo(left_inner)
            pen.closePath()
        else:
            # 小写a：圆形+竖杆
            stroke = self.stroke_width
            
            # 圆形部分（左侧）
            cx = w * 0.35
            cy = h / 2
            rx = (w * 0.35 - m)
            ry = h / 2
            
            kappa = 0.5522847498
            # 外轮廓
            pen.moveTo((cx + rx, cy))
            pen.curveTo(
                (cx + rx, cy - ry * kappa),
                (cx + rx * kappa, cy - ry),
                (cx, cy - ry)
            )
            pen.curveTo(
                (cx - rx * kappa, cy - ry),
                (cx - rx, cy - ry * kappa),
                (cx - rx, cy)
            )
            pen.curveTo(
                (cx - rx, cy + ry * kappa),
                (cx - rx * kappa, cy + ry),
                (cx, cy + ry)
            )
            pen.curveTo(
                (cx + rx * kappa, cy + ry),
                (cx + rx, cy + ry * kappa),
                (cx + rx, cy)
            )
            
            # 内轮廓
            inner_rx = rx - stroke
            inner_ry = ry - stroke
            pen.lineTo((cx + inner_rx, cy))
            pen.curveTo(
                (cx + inner_rx, cy + inner_ry * kappa),
                (cx + inner_rx * kappa, cy + inner_ry),
                (cx, cy + inner_ry)
            )
            pen.curveTo(
                (cx - inner_rx * kappa, cy + inner_ry),
                (cx - inner_rx, cy + inner_ry * kappa),
                (cx - inner_rx, cy)
            )
            pen.curveTo(
                (cx - inner_rx, cy - inner_ry * kappa),
                (cx - inner_rx * kappa, cy - inner_ry),
                (cx, cy - inner_ry)
            )
            pen.curveTo(
                (cx + inner_rx * kappa, cy - inner_ry),
                (cx + inner_rx, cy - inner_ry * kappa),
                (cx + inner_rx, cy)
            )
            pen.closePath()
            
            # 右侧垂直杆
            pen.moveTo((w - m - stroke, 0))
            pen.lineTo((w - m, 0))
            pen.lineTo((w - m, h))
            pen.lineTo((w - m - stroke, h))
            pen.closePath()
    
    def _create_b_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写b的设计（独立函数，避免覆盖大写B）"""
        if True:  # 保持缩进
            stroke = self.stroke_width
            ascender_h = h * 1.4  # ascender 高度
            
            # 左侧垂直杆（延伸到 ascender）
            pen.moveTo((m, 0))
            pen.lineTo((m + stroke, 0))
            pen.lineTo((m + stroke, ascender_h))
            pen.lineTo((m, ascender_h))
            pen.closePath()
            
            # 右侧圆形碗
            cx = w - m - (w - 2 * m - stroke) / 2
            cy = h / 2
            rx = (w - 2 * m - stroke) / 2
            ry = h / 2
            inner_rx = rx - stroke
            inner_ry = ry - stroke
            
            kappa = 0.5522847498
            
            # 类似大写D的碗形
            pen.moveTo((m + stroke, h))
            pen.lineTo((cx, h))
            pen.curveTo(
                (cx + rx * kappa, h),
                (cx + rx, cy + ry * kappa),
                (cx + rx, cy)
            )
            pen.curveTo(
                (cx + rx, cy - ry * kappa),
                (cx + rx * kappa, 0),
                (cx, 0)
            )
            pen.lineTo((m + stroke, 0))
            pen.lineTo((m + stroke, stroke))
            pen.lineTo((cx, stroke))
            pen.curveTo(
                (cx + inner_rx * kappa, stroke),
                (cx + inner_rx, cy - inner_ry * kappa),
                (cx + inner_rx, cy)
            )
            pen.curveTo(
                (cx + inner_rx, cy + inner_ry * kappa),
                (cx + inner_rx * kappa, h - stroke),
                (cx, h - stroke)
            )
            pen.lineTo((m + stroke, h - stroke))
            pen.lineTo((m + stroke, h))
            pen.closePath()
    
    def _create_d_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写d的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            ascender_h = h * 1.4
            
            # 右侧垂直杆（延伸到 ascender）
            pen.moveTo((w - m - stroke, 0))
            pen.lineTo((w - m, 0))
            pen.lineTo((w - m, ascender_h))
            pen.lineTo((w - m - stroke, ascender_h))
            pen.closePath()
            
            # 左侧圆形碗
            cx = m + (w - 2 * m - stroke) / 2
            cy = h / 2
            rx = (w - 2 * m - stroke) / 2
            ry = h / 2
            inner_rx = rx - stroke
            inner_ry = ry - stroke
            
            kappa = 0.5522847498
            
            pen.moveTo((w - m - stroke, h))
            pen.lineTo((cx, h))
            pen.curveTo(
                (cx - rx * kappa, h),
                (cx - rx, cy + ry * kappa),
                (cx - rx, cy)
            )
            pen.curveTo(
                (cx - rx, cy - ry * kappa),
                (cx - rx * kappa, 0),
                (cx, 0)
            )
            pen.lineTo((w - m - stroke, 0))
            pen.lineTo((w - m - stroke, stroke))
            pen.lineTo((cx, stroke))
            pen.curveTo(
                (cx - inner_rx * kappa, stroke),
                (cx - inner_rx, cy - inner_ry * kappa),
                (cx - inner_rx, cy)
            )
            pen.curveTo(
                (cx - inner_rx, cy + inner_ry * kappa),
                (cx - inner_rx * kappa, h - stroke),
                (cx, h - stroke)
            )
            pen.lineTo((w - m - stroke, h - stroke))
            pen.lineTo((w - m - stroke, h))
            pen.closePath()
    
    def _create_e_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写e的设计（独立函数）"""
        if True:
            # e字母：圆形+横杆
            stroke = self.stroke_width
            cx = w / 2
            cy = h / 2
            rx = (w - 2 * m) / 2
            ry = h / 2
            
            kappa = 0.5522847498
            
            # 简化版：圆形+中间横杆
            # 外轮廓
            pen.moveTo((cx + rx, cy))
            pen.curveTo(
                (cx + rx, cy - ry * kappa),
                (cx + rx * kappa, cy - ry),
                (cx, cy - ry)
            )
            pen.curveTo(
                (cx - rx * kappa, cy - ry),
                (cx - rx, cy - ry * kappa),
                (cx - rx, cy)
            )
            pen.lineTo((w - m, cy))
            pen.lineTo((w - m, cy + stroke))
            pen.lineTo((cx - rx, cy + stroke))
            pen.curveTo(
                (cx - rx, cy + ry * kappa),
                (cx - rx * kappa, cy + ry),
                (cx, cy + ry)
            )
            pen.curveTo(
                (cx + rx * kappa, cy + ry),
                (cx + rx, cy + ry * kappa),
                (cx + rx, cy)
            )
            
            # 内轮廓
            inner_rx = rx - stroke
            inner_ry = ry - stroke
            pen.lineTo((cx + inner_rx, cy))
            pen.curveTo(
                (cx + inner_rx, cy + inner_ry * kappa),
                (cx + inner_rx * kappa, cy + inner_ry),
                (cx, cy + inner_ry)
            )
            pen.curveTo(
                (cx - inner_rx * kappa, cy + inner_ry),
                (cx - inner_rx, cy + inner_ry * kappa),
                (cx - inner_rx, cy + stroke)
            )
            pen.lineTo((cx - inner_rx, cy))
            pen.curveTo(
                (cx - inner_rx, cy - inner_ry * kappa),
                (cx - inner_rx * kappa, cy - inner_ry),
                (cx, cy - inner_ry)
            )
            pen.curveTo(
                (cx + inner_rx * kappa, cy - inner_ry),
                (cx + inner_rx, cy - inner_ry * kappa),
                (cx + inner_rx, cy)
            )
            pen.closePath()
    
    def _create_i_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写i的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            center_x = w / 2
            
            # 垂直杆
            pen.moveTo((center_x - stroke / 2, 0))
            pen.lineTo((center_x + stroke / 2, 0))
            pen.lineTo((center_x + stroke / 2, h))
            pen.lineTo((center_x - stroke / 2, h))
            pen.closePath()
            
            # 顶部点
            dot_y = h * 1.3
            radius = stroke * 0.7
            pen.moveTo((center_x - radius, dot_y - radius))
            pen.lineTo((center_x + radius, dot_y - radius))
            pen.lineTo((center_x + radius, dot_y + radius))
            pen.lineTo((center_x - radius, dot_y + radius))
            pen.closePath()
    
    def _create_l_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写l的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            center_x = w / 2
            ascender_h = h * 1.4
            
            # 垂直杆（延伸到 ascender）
            pen.moveTo((center_x - stroke / 2, 0))
            pen.lineTo((center_x + stroke / 2, 0))
            pen.lineTo((center_x + stroke / 2, ascender_h))
            pen.lineTo((center_x - stroke / 2, ascender_h))
            pen.closePath()
    
    def _create_n_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写n的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            
            # 左侧垂直杆
            pen.moveTo((m, 0))
            pen.lineTo((m + stroke, 0))
            pen.lineTo((m + stroke, h))
            pen.lineTo((m, h))
            pen.closePath()
            
            # 右侧垂直杆
            pen.moveTo((w - m - stroke, 0))
            pen.lineTo((w - m, 0))
            pen.lineTo((w - m, h))
            pen.lineTo((w - m - stroke, h))
            pen.closePath()
            
            # 顶部弧形连接
            cx = w / 2
            cy = h * 0.7
            rx = (w - 2 * m - stroke) / 2
            ry = h * 0.3
            
            kappa = 0.5522847498
            pen.moveTo((m + stroke, h))
            pen.curveTo(
                (m + stroke, h - ry * kappa),
                (cx - rx * kappa, cy),
                (cx, cy)
            )
            pen.curveTo(
                (cx + rx * kappa, cy),
                (w - m - stroke, h - ry * kappa),
                (w - m - stroke, h))
            pen.closePath()
    
    def _create_r_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写r的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            
            # 左侧垂直杆
            pen.moveTo((m, 0))
            pen.lineTo((m + stroke, 0))
            pen.lineTo((m + stroke, h))
            pen.lineTo((m, h))
            pen.closePath()
            
            # 顶部弧形
            pen.moveTo((m + stroke, h - stroke))
            pen.lineTo((w - m - stroke, h - stroke))
            pen.qCurveTo((w - m, h * 0.7), (w - m, h * 0.5))
            pen.lineTo((w - m - stroke, h * 0.5))
            pen.qCurveTo((w - m - stroke, h * 0.7), (m + stroke, h))
            pen.closePath()
    
    def _create_t_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写t的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            center_x = w / 2
            ascender_h = h * 1.2
            h_stroke = self.horizontal_stroke
            
            # 垂直杆
            pen.moveTo((center_x - stroke / 2, 0))
            pen.lineTo((center_x + stroke / 2, 0))
            pen.lineTo((center_x + stroke / 2, ascender_h))
            pen.lineTo((center_x - stroke / 2, ascender_h))
            pen.closePath()
            
            # 横杆
            pen.moveTo((m, h - h_stroke / 2))
            pen.lineTo((w - m, h - h_stroke / 2))
            pen.lineTo((w - m, h + h_stroke / 2))
            pen.lineTo((m, h + h_stroke / 2))
            pen.closePath()
    
    def _create_u_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """小写u的设计（独立函数）"""
        if True:
            stroke = self.stroke_width
            
            # 左侧垂直杆
            pen.moveTo((m, h * 0.3))
            pen.lineTo((m + stroke, h * 0.3))
            pen.lineTo((m + stroke, h))
            pen.lineTo((m, h))
            pen.closePath()
            
            # 右侧垂直杆
            pen.moveTo((w - m - stroke, h * 0.3))
            pen.lineTo((w - m, h * 0.3))
            pen.lineTo((w - m, h))
            pen.lineTo((w - m - stroke, h))
            pen.closePath()
            
            # 底部弧形
            cx = w / 2
            cy = h * 0.3
            rx = (w - 2 * m - stroke) / 2
            ry = h * 0.3
            
            kappa = 0.5522847498
            pen.moveTo((m + stroke, cy))
            pen.curveTo(
                (m + stroke, cy - ry * kappa),
                (cx - rx * kappa, cy - ry),
                (cx, cy - ry)
            )
            pen.curveTo(
                (cx + rx * kappa, cy - ry),
                (w - m - stroke, cy - ry * kappa),
                (w - m - stroke, cy)
            )
            pen.lineTo((w - m, cy))
            pen.curveTo(
                (w - m, cy - (ry + stroke) * kappa),
                (cx + (rx + stroke) * kappa, cy - ry - stroke),
                (cx, cy - ry - stroke)
            )
            pen.curveTo(
                (cx - (rx + stroke) * kappa, cy - ry - stroke),
                (m, cy - (ry + stroke) * kappa),
                (m, cy)
            )
            pen.closePath()
    
    def _create_default_lowercase(self, pen: TTGlyphPen, w: float, h: float, m: float, char: str):
        """默认小写字母设计（单竖线）"""
        stroke = self.stroke_width
        center_x = w / 2
        
        pen.moveTo((center_x - stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, h))
        pen.lineTo((center_x - stroke / 2, h))
        pen.closePath()
    
    # ==================== 数字设计 ====================
    
    def _create_digit_0(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字0：类似O"""
        self._create_o(pen, w, h, m, is_upper=True)
    
    def _create_digit_1(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字1：垂直杆"""
        stroke = self.stroke_width
        center_x = w / 2
        
        pen.moveTo((center_x - stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, 0))
        pen.lineTo((center_x + stroke / 2, h))
        pen.lineTo((center_x - stroke / 2, h))
        pen.closePath()
    
    def _create_digit_2(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字2：上圆弧+对角线+底横线"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 上半圆
        cx = w / 2
        cy = h * 0.75
        rx = (w - 2 * m) / 2
        ry = h * 0.25
        
        kappa = 0.5522847498
        pen.moveTo((m + stroke, cy))
        pen.curveTo(
            (m + stroke, cy + ry * kappa),
            (cx - rx * kappa, cy + ry),
            (cx, cy + ry)
        )
        pen.curveTo(
            (cx + rx * kappa, cy + ry),
            (w - m - stroke, cy + ry * kappa),
            (w - m - stroke, cy)
        )
        pen.lineTo((w - m, cy))
        pen.curveTo(
            (w - m, cy + (ry + stroke) * kappa),
            (cx + (rx + stroke) * kappa, h),
            (cx, h)
        )
        pen.curveTo(
            (cx - (rx + stroke) * kappa, h),
            (m, cy + (ry + stroke) * kappa),
            (m, cy)
        )
        pen.closePath()
        
        # 对角线
        pen.moveTo((w - m, cy))
        pen.lineTo((w - m - stroke * 0.7, cy))
        pen.lineTo((m + stroke * 0.7, h_stroke))
        pen.lineTo((m, h_stroke))
        pen.closePath()
        
        # 底部横线
        pen.moveTo((m, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h_stroke))
        pen.lineTo((m, h_stroke))
        pen.closePath()
    
    def _create_digit_3(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字3：两个半圆（类似S的一半）"""
        stroke = self.stroke_width
        cx = w - m - (w - 2 * m) / 2
        upper_cy = h * 0.75
        lower_cy = h * 0.25
        rx = (w - 2 * m) / 2
        ry = h / 4
        
        kappa = 0.5522847498
        
        # 上半圆
        pen.moveTo((m, h))
        pen.lineTo((cx, h))
        pen.curveTo(
            (cx + rx * kappa, h),
            (cx + rx, upper_cy + ry * kappa),
            (cx + rx, upper_cy)
        )
        pen.curveTo(
            (cx + rx, upper_cy - ry * kappa),
            (cx + rx * kappa, upper_cy - ry),
            (cx, upper_cy - ry)
        )
        pen.lineTo((cx, lower_cy + ry))
        pen.curveTo(
            (cx + rx * kappa, lower_cy + ry),
            (cx + rx, lower_cy + ry * kappa),
            (cx + rx, lower_cy)
        )
        pen.curveTo(
            (cx + rx, lower_cy - ry * kappa),
            (cx + rx * kappa, 0),
            (cx, 0)
        )
        pen.lineTo((m, 0))
        pen.lineTo((m, stroke))
        pen.lineTo((cx, stroke))
        
        # 内轮廓
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        pen.curveTo(
            (cx + inner_rx * kappa, stroke),
            (cx + inner_rx, lower_cy - inner_ry * kappa),
            (cx + inner_rx, lower_cy)
        )
        pen.curveTo(
            (cx + inner_rx, lower_cy + inner_ry * kappa),
            (cx + inner_rx * kappa, lower_cy + inner_ry),
            (cx, lower_cy + inner_ry)
        )
        pen.lineTo((cx, upper_cy - inner_ry))
        pen.curveTo(
            (cx + inner_rx * kappa, upper_cy - inner_ry),
            (cx + inner_rx, upper_cy + inner_ry * kappa),
            (cx + inner_rx, upper_cy)
        )
        pen.curveTo(
            (cx + inner_rx, upper_cy + inner_ry * kappa),
            (cx + inner_rx * kappa, h - stroke),
            (cx, h - stroke)
        )
        pen.lineTo((m, h - stroke))
        pen.lineTo((m, h))
        pen.closePath()
    
    def _create_digit_4(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字4：垂直杆+对角线+横线"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 右侧垂直杆
        pen.moveTo((w - m - stroke, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h))
        pen.lineTo((w - m - stroke, h))
        pen.closePath()
        
        # 对角线
        pen.moveTo((m, h * 0.3))
        pen.lineTo((m + stroke * 0.7, h * 0.3))
        pen.lineTo((w - m - stroke, h - stroke * 0.7))
        pen.lineTo((w - m - stroke, h))
        pen.lineTo((w - m - stroke * 1.5, h))
        pen.lineTo((m, h * 0.3 + stroke * 0.7))
        pen.closePath()
        
        # 横线
        pen.moveTo((m, h * 0.3))
        pen.lineTo((w - m, h * 0.3))
        pen.lineTo((w - m, h * 0.3 + h_stroke))
        pen.lineTo((m, h * 0.3 + h_stroke))
        pen.closePath()
    
    def _create_digit_5(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字5：顶横线+垂直线+底圆弧"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 顶部横线
        pen.moveTo((m, h - h_stroke))
        pen.lineTo((w - m, h - h_stroke))
        pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 左侧垂直线
        pen.moveTo((m, h / 2))
        pen.lineTo((m + stroke, h / 2))
        pen.lineTo((m + stroke, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 底部圆弧
        cx = w - m - (w - 2 * m - stroke) / 2
        cy = h * 0.25
        rx = (w - 2 * m - stroke) / 2
        ry = h * 0.25
        
        kappa = 0.5522847498
        pen.moveTo((m + stroke, h / 2))
        pen.lineTo((cx, h / 2))
        pen.curveTo(
            (cx + rx * kappa, h / 2),
            (cx + rx, cy + ry * kappa),
            (cx + rx, cy)
        )
        pen.curveTo(
            (cx + rx, cy - ry * kappa),
            (cx + rx * kappa, 0),
            (cx, 0)
        )
        pen.lineTo((m, 0))
        pen.lineTo((m, stroke))
        pen.lineTo((cx, stroke))
        
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        pen.curveTo(
            (cx + inner_rx * kappa, stroke),
            (cx + inner_rx, cy - inner_ry * kappa),
            (cx + inner_rx, cy)
        )
        pen.curveTo(
            (cx + inner_rx, cy + inner_ry * kappa),
            (cx + inner_rx * kappa, h / 2 - stroke),
            (cx, h / 2 - stroke)
        )
        pen.lineTo((m + stroke, h / 2 - stroke))
        pen.lineTo((m + stroke, h / 2))
        pen.closePath()
    
    def _create_digit_6(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字6：圆形+顶部弧线"""
        stroke = self.stroke_width
        
        # 底部圆形
        cx = w / 2
        cy = h * 0.25
        rx = (w - 2 * m) / 2
        ry = h * 0.25
        
        kappa = 0.5522847498
        
        # 外轮廓
        pen.moveTo((cx + rx, cy))
        pen.curveTo(
            (cx + rx, cy - ry * kappa),
            (cx + rx * kappa, cy - ry),
            (cx, cy - ry)
        )
        pen.curveTo(
            (cx - rx * kappa, cy - ry),
            (cx - rx, cy - ry * kappa),
            (cx - rx, cy)
        )
        pen.curveTo(
            (cx - rx, cy + ry * kappa),
            (cx - rx * kappa, cy + ry),
            (cx, cy + ry)
        )
        pen.curveTo(
            (cx + rx * kappa, cy + ry),
            (cx + rx, cy + ry * kappa),
            (cx + rx, cy)
        )
        
        # 内轮廓
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        pen.lineTo((cx + inner_rx, cy))
        pen.curveTo(
            (cx + inner_rx, cy + inner_ry * kappa),
            (cx + inner_rx * kappa, cy + inner_ry),
            (cx, cy + inner_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, cy + inner_ry),
            (cx - inner_rx, cy + inner_ry * kappa),
            (cx - inner_rx, cy)
        )
        pen.curveTo(
            (cx - inner_rx, cy - inner_ry * kappa),
            (cx - inner_rx * kappa, cy - inner_ry),
            (cx, cy - inner_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, cy - inner_ry),
            (cx + inner_rx, cy - inner_ry * kappa),
            (cx + inner_rx, cy)
        )
        pen.closePath()
        
        # 顶部弧线
        pen.moveTo((cx - rx, cy))
        pen.lineTo((cx - rx - stroke, cy))
        pen.lineTo((cx - rx - stroke, h))
        pen.qCurveTo((cx + rx, h), (cx + rx, cy))
        pen.lineTo((cx + rx - stroke, cy))
        pen.qCurveTo((cx + rx - stroke, h - stroke * 2), (cx - rx, cy))
        pen.closePath()
    
    def _create_digit_7(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字7：顶横线+对角线"""
        stroke = self.stroke_width
        h_stroke = self.horizontal_stroke
        
        # 顶部横线
        pen.moveTo((m, h - h_stroke))
        pen.lineTo((w - m, h - h_stroke))
        pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 对角线
        pen.moveTo((w - m, h - h_stroke))
        pen.lineTo((w - m - stroke * 0.7, h - h_stroke))
        pen.lineTo((m + stroke * 0.7, 0))
        pen.lineTo((m, 0))
        pen.closePath()
    
    def _create_digit_8(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字8：两个圆形"""
        stroke = self.stroke_width
        cx = w / 2
        upper_cy = h * 0.7
        lower_cy = h * 0.3
        rx = (w - 2 * m) / 2
        upper_ry = h * 0.2
        lower_ry = h * 0.3
        
        kappa = 0.5522847498
        
        # 上圆
        pen.moveTo((cx + rx, upper_cy))
        pen.curveTo(
            (cx + rx, upper_cy - upper_ry * kappa),
            (cx + rx * kappa, upper_cy - upper_ry),
            (cx, upper_cy - upper_ry)
        )
        pen.curveTo(
            (cx - rx * kappa, upper_cy - upper_ry),
            (cx - rx, upper_cy - upper_ry * kappa),
            (cx - rx, upper_cy)
        )
        pen.curveTo(
            (cx - rx, upper_cy + upper_ry * kappa),
            (cx - rx * kappa, upper_cy + upper_ry),
            (cx, upper_cy + upper_ry)
        )
        pen.curveTo(
            (cx + rx * kappa, upper_cy + upper_ry),
            (cx + rx, upper_cy + upper_ry * kappa),
            (cx + rx, upper_cy)
        )
        
        inner_rx = rx - stroke
        inner_upper_ry = upper_ry - stroke
        pen.lineTo((cx + inner_rx, upper_cy))
        pen.curveTo(
            (cx + inner_rx, upper_cy + inner_upper_ry * kappa),
            (cx + inner_rx * kappa, upper_cy + inner_upper_ry),
            (cx, upper_cy + inner_upper_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, upper_cy + inner_upper_ry),
            (cx - inner_rx, upper_cy + inner_upper_ry * kappa),
            (cx - inner_rx, upper_cy)
        )
        pen.curveTo(
            (cx - inner_rx, upper_cy - inner_upper_ry * kappa),
            (cx - inner_rx * kappa, upper_cy - inner_upper_ry),
            (cx, upper_cy - inner_upper_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, upper_cy - inner_upper_ry),
            (cx + inner_rx, upper_cy - inner_upper_ry * kappa),
            (cx + inner_rx, upper_cy)
        )
        pen.closePath()
        
        # 下圆
        pen.moveTo((cx + rx, lower_cy))
        pen.curveTo(
            (cx + rx, lower_cy - lower_ry * kappa),
            (cx + rx * kappa, lower_cy - lower_ry),
            (cx, lower_cy - lower_ry)
        )
        pen.curveTo(
            (cx - rx * kappa, lower_cy - lower_ry),
            (cx - rx, lower_cy - lower_ry * kappa),
            (cx - rx, lower_cy)
        )
        pen.curveTo(
            (cx - rx, lower_cy + lower_ry * kappa),
            (cx - rx * kappa, lower_cy + lower_ry),
            (cx, lower_cy + lower_ry)
        )
        pen.curveTo(
            (cx + rx * kappa, lower_cy + lower_ry),
            (cx + rx, lower_cy + lower_ry * kappa),
            (cx + rx, lower_cy)
        )
        
        inner_lower_ry = lower_ry - stroke
        pen.lineTo((cx + inner_rx, lower_cy))
        pen.curveTo(
            (cx + inner_rx, lower_cy + inner_lower_ry * kappa),
            (cx + inner_rx * kappa, lower_cy + inner_lower_ry),
            (cx, lower_cy + inner_lower_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, lower_cy + inner_lower_ry),
            (cx - inner_rx, lower_cy + inner_lower_ry * kappa),
            (cx - inner_rx, lower_cy)
        )
        pen.curveTo(
            (cx - inner_rx, lower_cy - inner_lower_ry * kappa),
            (cx - inner_rx * kappa, lower_cy - inner_lower_ry),
            (cx, lower_cy - inner_lower_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, lower_cy - inner_lower_ry),
            (cx + inner_rx, lower_cy - inner_lower_ry * kappa),
            (cx + inner_rx, lower_cy)
        )
        pen.closePath()
    
    def _create_digit_9(self, pen: TTGlyphPen, w: float, h: float, m: float):
        """数字9：圆形+底部弧线（6的倒置）"""
        stroke = self.stroke_width
        
        # 顶部圆形
        cx = w / 2
        cy = h * 0.75
        rx = (w - 2 * m) / 2
        ry = h * 0.25
        
        kappa = 0.5522847498
        
        # 外轮廓
        pen.moveTo((cx + rx, cy))
        pen.curveTo(
            (cx + rx, cy - ry * kappa),
            (cx + rx * kappa, cy - ry),
            (cx, cy - ry)
        )
        pen.curveTo(
            (cx - rx * kappa, cy - ry),
            (cx - rx, cy - ry * kappa),
            (cx - rx, cy)
        )
        pen.curveTo(
            (cx - rx, cy + ry * kappa),
            (cx - rx * kappa, cy + ry),
            (cx, cy + ry)
        )
        pen.curveTo(
            (cx + rx * kappa, cy + ry),
            (cx + rx, cy + ry * kappa),
            (cx + rx, cy)
        )
        
        # 内轮廓
        inner_rx = rx - stroke
        inner_ry = ry - stroke
        pen.lineTo((cx + inner_rx, cy))
        pen.curveTo(
            (cx + inner_rx, cy + inner_ry * kappa),
            (cx + inner_rx * kappa, cy + inner_ry),
            (cx, cy + inner_ry)
        )
        pen.curveTo(
            (cx - inner_rx * kappa, cy + inner_ry),
            (cx - inner_rx, cy + inner_ry * kappa),
            (cx - inner_rx, cy)
        )
        pen.curveTo(
            (cx - inner_rx, cy - inner_ry * kappa),
            (cx - inner_rx * kappa, cy - inner_ry),
            (cx, cy - inner_ry)
        )
        pen.curveTo(
            (cx + inner_rx * kappa, cy - inner_ry),
            (cx + inner_rx, cy - inner_ry * kappa),
            (cx + inner_rx, cy)
        )
        pen.closePath()
        
        # 底部弧线
        pen.moveTo((cx + rx, cy))
        pen.lineTo((cx + rx + stroke, cy))
        pen.lineTo((cx + rx + stroke, 0))
        pen.qCurveTo((cx - rx, 0), (cx - rx, cy))
        pen.lineTo((cx - rx + stroke, cy))
        pen.qCurveTo((cx - rx + stroke, stroke * 2), (cx + rx, cy))
        pen.closePath()
    
    def _create_default_digit(self, pen: TTGlyphPen, w: float, h: float, m: float, char: str):
        """默认数字设计（空心方框）"""
        stroke = self.stroke_width
        
        # 外框
        pen.moveTo((m, 0))
        pen.lineTo((w - m, 0))
        pen.lineTo((w - m, h))
        pen.lineTo((m, h))
        pen.closePath()
        
        # 内框（反向）
        inner_m = m + stroke
        pen.moveTo((inner_m, stroke))
        pen.lineTo((inner_m, h - stroke))
        pen.lineTo((w - inner_m, h - stroke))
        pen.lineTo((w - inner_m, stroke))
        pen.closePath()
    
    # ==================== 标点符号设计 ====================
    
    def _create_punctuation(self, pen: TTGlyphPen, char: str, w: float, h: float, m: float):
        """创建标点符号"""
        stroke = self.stroke_width
        center_x = w / 2
        
        if char == '.':
            # 句号：小圆点
            radius = stroke * 0.6
            cy = h * 0.15
            pen.moveTo((center_x - radius, cy - radius))
            pen.lineTo((center_x + radius, cy - radius))
            pen.lineTo((center_x + radius, cy + radius))
            pen.lineTo((center_x - radius, cy + radius))
            pen.closePath()
        
        elif char == ',':
            # 逗号：小圆点+尾巴
            radius = stroke * 0.6
            cy = h * 0.15
            pen.moveTo((center_x - radius, cy - radius))
            pen.lineTo((center_x + radius, cy - radius))
            pen.lineTo((center_x + radius, cy))
            pen.lineTo((center_x, cy - h * 0.2))
            pen.lineTo((center_x - radius, cy))
            pen.closePath()
        
        elif char in '!?':
            # 感叹号/问号：垂直杆
            pen.moveTo((center_x - stroke / 2, h * 0.3))
            pen.lineTo((center_x + stroke / 2, h * 0.3))
            pen.lineTo((center_x + stroke / 2, h))
            pen.lineTo((center_x - stroke / 2, h))
            pen.closePath()
            
            # 底部点
            radius = stroke * 0.6
            cy = h * 0.1
            pen.moveTo((center_x - radius, cy - radius))
            pen.lineTo((center_x + radius, cy - radius))
            pen.lineTo((center_x + radius, cy + radius))
            pen.lineTo((center_x - radius, cy + radius))
            pen.closePath()
        
        elif char in '()':
            # 括号：弧线
            if char == '(':
                pen.moveTo((w - m, h))
                pen.qCurveTo((m + stroke, h / 2), (w - m, 0))
                pen.lineTo((w - m - stroke, 0))
                pen.qCurveTo((m + stroke * 2, h / 2), (w - m - stroke, h))
                pen.closePath()
            else:  # ')'
                pen.moveTo((m, 0))
                pen.qCurveTo((w - m - stroke, h / 2), (m, h))
                pen.lineTo((m + stroke, h))
                pen.qCurveTo((w - m - stroke * 2, h / 2), (m + stroke, 0))
                pen.closePath()
        
        else:
            # 其他符号：简单矩形
            pen.moveTo((m, h * 0.4))
            pen.lineTo((w - m, h * 0.4))
            pen.lineTo((w - m, h * 0.6))
            pen.lineTo((m, h * 0.6))
            pen.closePath()
