#!/usr/bin/env python3
"""
字体生成器主程序
根据设计规格JSON生成TTF/OTF字体文件
"""

import json
import sys
import argparse
import os
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
try:
    from fontTools.fontBuilder import FontBuilder
except ImportError:
    # 如果FontBuilder不可用，使用替代方案
    FontBuilder = None
import math

# 导入专业字形设计器
try:
    from glyph_designer import GlyphDesigner
    PROFESSIONAL_MODE = True
except ImportError:
    print("警告: 无法导入专业字形设计器，使用简化模式")
    PROFESSIONAL_MODE = False

def load_spec(spec_path):
    """加载设计规格JSON"""
    with open(spec_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_char_path(char, spec):
    """根据字符和规格生成SVG路径"""
    design_params = spec['designParameters']
    metrics = design_params['metrics']
    proportions = design_params['proportions']
    visual_style = spec['styleDefinition']['visualStyle']
    
    units_per_em = metrics['unitsPerEm']
    x_height = metrics['xHeight']
    cap_height = metrics['capHeight']
    stroke_width = proportions['strokeWidth']
    
    # 字符宽度（根据字符类型确定）
    if char.isupper():
        char_height = cap_height
    elif char.islower():
        char_height = x_height
    else:
        char_height = x_height
    
    # 基础字符宽度
    char_width = int(char_height * 0.6)
    
    # 生成简单的字符路径（MVP版本使用参数化模板）
    return generate_template_char(char, char_width, char_height, stroke_width, visual_style, units_per_em)

def generate_template_char(char, width, height, stroke_width, visual_style, units_per_em):
    """基于模板生成字符路径"""
    # MVP版本：使用简单的几何形状组合生成字符
    # 实际实现应该根据字符特征生成更复杂的路径
    
    path_data = []
    
    if char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        # 大写字母：使用矩形和直线组合
        if char in 'I':
            # I: 单竖线
            path_data.append(f'M {width//2} 0 L {width//2} {height}')
        elif char in 'O':
            # O: 圆形
            center_x = width // 2
            center_y = height // 2
            radius = min(width, height) // 2 - stroke_width // 2
            path_data.append(f'M {center_x + radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y - radius} A {radius} {radius} 0 0 1 {center_x - radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y + radius} A {radius} {radius} 0 0 1 {center_x + radius} {center_y} Z')
        else:
            # 其他字母：使用矩形框架
            path_data.append(f'M {stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {height - stroke_width//2} L {stroke_width//2} {height - stroke_width//2} Z')
    
    elif char in 'abcdefghijklmnopqrstuvwxyz':
        # 小写字母：类似处理但高度较小
        if char in 'i':
            path_data.append(f'M {width//2} 0 L {width//2} {height}')
        elif char in 'o':
            center_x = width // 2
            center_y = height // 2
            radius = min(width, height) // 2 - stroke_width // 2
            path_data.append(f'M {center_x + radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y - radius} A {radius} {radius} 0 0 1 {center_x - radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y + radius} A {radius} {radius} 0 0 1 {center_x + radius} {center_y} Z')
        else:
            path_data.append(f'M {stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {height - stroke_width//2} L {stroke_width//2} {height - stroke_width//2} Z')
    
    elif char.isdigit():
        # 数字：使用圆形和矩形组合
        if char in '0':
            center_x = width // 2
            center_y = height // 2
            radius = min(width, height) // 2 - stroke_width // 2
            path_data.append(f'M {center_x + radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y - radius} A {radius} {radius} 0 0 1 {center_x - radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y + radius} A {radius} {radius} 0 0 1 {center_x + radius} {center_y} Z')
        else:
            path_data.append(f'M {stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {height - stroke_width//2} L {stroke_width//2} {height - stroke_width//2} Z')
    
    else:
        # 标点符号：使用简单形状
        if char == '.':
            center_x = width // 2
            center_y = height // 2
            radius = stroke_width // 2
            path_data.append(f'M {center_x + radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y - radius} A {radius} {radius} 0 0 1 {center_x - radius} {center_y} A {radius} {radius} 0 0 1 {center_x} {center_y + radius} A {radius} {radius} 0 0 1 {center_x + radius} {center_y} Z')
        else:
            path_data.append(f'M {stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {stroke_width//2} L {width - stroke_width//2} {height - stroke_width//2} L {stroke_width//2} {height - stroke_width//2} Z')
    
    return ' '.join(path_data)

def create_font(spec, output_path):
    """创建字体文件"""
    print(f"🎨 开始生成字体文件...")
    
    # MVP版本：直接使用简化的 TrueType 字体生成
    # 后续版本将实现完整的字形绘制和样式应用
    success = create_minimal_font(spec, output_path)
    
    if success:
        print(f"✅ 字体文件已成功生成: {output_path}")
    else:
        print(f"❌ 字体文件生成失败")
        raise Exception("字体生成失败")

def create_minimal_font(spec, output_path):
    """创建专业级 TrueType 字体文件"""
    print(f"📝 正在创建专业级 TrueType 字体文件...")
    print(f"✨ 使用参数化贝塞尔曲线字形设计")
    
    try:
        from fontTools import fontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        from glyph_designer import GlyphDesigner
        
        metrics = spec['designParameters']['metrics']
        basic_info = spec['basicInfo']
        visual_style = spec['styleDefinition']['visualStyle']
        proportions = spec['designParameters']['proportions']
        
        # 创建 FontBuilder 实例
        fb = fontBuilder.FontBuilder(unitsPerEm=metrics['unitsPerEm'], isTTF=True)
        
        # 准备字形设计器参数
        designer_params = {
            'strokeWidth': proportions.get('strokeWidth', 80),
            'contrast': proportions.get('contrast', 'medium'),
            'terminals': visual_style.get('terminals', 'straight'),
            'corners': visual_style.get('corners', 'rounded'),
            'aperture': visual_style.get('aperture', 'semi-open'),
            'axis': visual_style.get('axis', 'vertical'),
            'stress': visual_style.get('stress', 'vertical'),
            'capHeight': metrics['capHeight'],
            'xHeight': metrics['xHeight'],
            'unitsPerEm': metrics['unitsPerEm']
        }
        
        # 创建字形设计器
        designer = GlyphDesigner(designer_params)
        
        print(f"🎨 设计参数: strokeWidth={designer_params['strokeWidth']}, "
              f"contrast={designer_params['contrast']}, "
              f"terminals={designer_params['terminals']}")
        
        # 字形字典和度量
        glyphs = {}
        metrics_dict = {}  # {glyph_name: (width, lsb)}
        
        # 旧的创建字形函数（作为后备）
        def create_glyph_for_char_fallback(char, width, height):
            """为特定字符创建简化的字形"""
            pen = TTGlyphPen(None)
            margin = width // 10
            stroke = width // 8
            
            # 根据字符类型创建不同的形状
            if char.isupper():
                # 大写字母：使用垂直线条 + 水平线条组合
                # 左侧垂直线
                pen.moveTo((margin, 0))
                pen.lineTo((margin + stroke, 0))
                pen.lineTo((margin + stroke, height))
                pen.lineTo((margin, height))
                pen.closePath()
                
                # 顶部水平线
                pen.moveTo((margin, height - stroke))
                pen.lineTo((width - margin, height - stroke))
                pen.lineTo((width - margin, height))
                pen.lineTo((margin, height))
                pen.closePath()
                
            elif char.islower():
                # 小写字母：使用较小的形状
                # 中间垂直线
                center_x = width // 2
                pen.moveTo((center_x - stroke // 2, 0))
                pen.lineTo((center_x + stroke // 2, 0))
                pen.lineTo((center_x + stroke // 2, height))
                pen.lineTo((center_x - stroke // 2, height))
                pen.closePath()
                
            elif char.isdigit():
                # 数字：使用圆形轮廓
                # 外框
                pen.moveTo((margin, 0))
                pen.lineTo((width - margin, 0))
                pen.lineTo((width - margin, height))
                pen.lineTo((margin, height))
                pen.closePath()
                
                # 内框（挖空）
                inner_margin = margin + stroke
                pen.moveTo((inner_margin, stroke))
                pen.lineTo((inner_margin, height - stroke))
                pen.lineTo((width - inner_margin, height - stroke))
                pen.lineTo((width - inner_margin, stroke))
                pen.closePath()
                
            elif char in '.,;:':
                # 标点符号：小圆点
                center_x = width // 2
                center_y = height // 4
                radius = stroke
                pen.moveTo((center_x - radius, center_y - radius))
                pen.lineTo((center_x + radius, center_y - radius))
                pen.lineTo((center_x + radius, center_y + radius))
                pen.lineTo((center_x - radius, center_y + radius))
                pen.closePath()
                
            elif char in '!?':
                # 感叹号问号：垂直线
                center_x = width // 2
                pen.moveTo((center_x - stroke // 2, height // 3))
                pen.lineTo((center_x + stroke // 2, height // 3))
                pen.lineTo((center_x + stroke // 2, height))
                pen.lineTo((center_x - stroke // 2, height))
                pen.closePath()
                
            else:
                # 其他符号：简单矩形
                pen.moveTo((margin, 0))
                pen.lineTo((width - margin, 0))
                pen.lineTo((width - margin, height))
                pen.lineTo((margin, height))
                pen.closePath()
            
            return pen.glyph(), margin
        
        # .notdef 字形（必需）- 使用问号框表示
        pen_notdef = TTGlyphPen(None)
        margin = 50
        pen_notdef.moveTo((margin, 0))
        pen_notdef.lineTo((500 - margin, 0))
        pen_notdef.lineTo((500 - margin, 700))
        pen_notdef.lineTo((margin, 700))
        pen_notdef.closePath()
        glyphs['.notdef'] = pen_notdef.glyph()
        metrics_dict['.notdef'] = (500, margin)
        
        # space 字形（空白）
        pen_space = TTGlyphPen(None)
        glyphs['space'] = pen_space.glyph()
        metrics_dict['space'] = (250, 0)
        
        # 计算基础宽度
        base_width = int(metrics['xHeight'] * 0.6)
        if base_width < 300:
            base_width = 400
        
        print(f"📐 基础字符宽度: {base_width}")
        
        # 使用专业字形设计器生成所有字符
        print(f"🎨 使用专业设计器生成字形...")
        
        # A-Z 大写字母
        for i in range(65, 91):
            char = chr(i)
            try:
                glyph, lsb = designer.create_glyph(char, base_width, metrics['capHeight'])
                glyphs[char] = glyph
                metrics_dict[char] = (base_width, lsb)
            except Exception as e:
                print(f"⚠️  字符 {char} 生成失败，使用后备方案: {e}")
                glyph, lsb = create_glyph_for_char_fallback(char, base_width, metrics['capHeight'])
                glyphs[char] = glyph
                metrics_dict[char] = (base_width, lsb)
        
        # a-z 小写字母
        for i in range(97, 123):
            char = chr(i)
            try:
                glyph, lsb = designer.create_glyph(char, base_width, metrics['xHeight'])
                glyphs[char] = glyph
                metrics_dict[char] = (base_width, lsb)
            except Exception as e:
                print(f"⚠️  字符 {char} 生成失败，使用后备方案: {e}")
                glyph, lsb = create_glyph_for_char_fallback(char, base_width, metrics['xHeight'])
                glyphs[char] = glyph
                metrics_dict[char] = (base_width, lsb)
        
        # 0-9 数字
        for i in range(48, 58):
            char = chr(i)
            try:
                glyph, lsb = designer.create_glyph(char, base_width, metrics['capHeight'])
                glyphs[char] = glyph
                metrics_dict[char] = (base_width, lsb)
            except Exception as e:
                print(f"⚠️  字符 {char} 生成失败，使用后备方案: {e}")
                glyph, lsb = create_glyph_for_char_fallback(char, base_width, metrics['capHeight'])
                glyphs[char] = glyph
                metrics_dict[char] = (base_width, lsb)
        
        # 常用标点符号
        punctuation_width = base_width // 2
        for char in '.,;:!?\'"()-[]{}/@#$%&*+=<>':
            try:
                glyph, lsb = designer.create_glyph(char, punctuation_width, metrics['xHeight'] // 2)
                glyphs[char] = glyph
                metrics_dict[char] = (punctuation_width, lsb)
            except Exception as e:
                print(f"⚠️  字符 {char} 生成失败，使用后备方案: {e}")
                glyph, lsb = create_glyph_for_char_fallback(char, punctuation_width, metrics['xHeight'] // 2)
                glyphs[char] = glyph
                metrics_dict[char] = (punctuation_width, lsb)
        
        print(f"✅ 成功生成 {len(glyphs)} 个字形")
        
        # 设置字形顺序
        glyph_order = ['.notdef', 'space']
        glyph_order.extend([chr(i) for i in range(65, 91)])  # A-Z
        glyph_order.extend([chr(i) for i in range(97, 123)])  # a-z
        glyph_order.extend([chr(i) for i in range(48, 58)])  # 0-9
        glyph_order.extend(list('.,;:!?\'"()-[]{}/@#$%&*+=<>'))
        
        fb.setupGlyphOrder(glyph_order)
        
        # 设置字符映射（Unicode -> 字形名称）
        cmap = {}
        for glyph_name in glyph_order:
            if glyph_name not in ['.notdef', 'space']:
                cmap[ord(glyph_name)] = glyph_name
        cmap[32] = 'space'  # 空格
        fb.setupCharacterMap(cmap)
        
        # 设置字形表（TrueType格式）
        # 如果有三次贝塞尔曲线，fontTools会自动转换为二次贝塞尔
        try:
            from cu2qu.pens import Cu2QuPen
            from fontTools.pens.recordingPen import RecordingPen
            from fontTools.pens.ttGlyphPen import TTGlyphPen as TTGlyphPenReplay
            
            # 转换所有字形从三次贝塞尔到二次贝塞尔
            converted_glyphs = {}
            for glyph_name, glyph in glyphs.items():
                if glyph_name in ['.notdef', 'space']:
                    converted_glyphs[glyph_name] = glyph
                    continue
                
                try:
                    # 创建录制pen来捕获原始字形的绘制操作
                    recording_pen = RecordingPen()
                    glyph.draw(recording_pen, glyphs)
                    
                    # 创建cu2qu转换pen
                    new_pen = TTGlyphPenReplay(None)
                    cu2qu_pen = Cu2QuPen(new_pen, 1.0)  # 1.0 is max_err
                    
                    # 重放并转换
                    recording_pen.replay(cu2qu_pen)
                    converted_glyphs[glyph_name] = new_pen.glyph()
                except Exception as e:
                    print(f"⚠️  字形 {glyph_name} 转换失败，使用原始字形: {e}")
                    converted_glyphs[glyph_name] = glyph
            
            fb.setupGlyf(converted_glyphs)
            print("✅ 字形已转换为二次贝塞尔曲线")
        except ImportError:
            print("⚠️  cu2qu未安装，尝试直接使用字形...")
            fb.setupGlyf(glyphs)
        
        # 设置水平度量
        fb.setupHorizontalMetrics(metrics_dict)
        
        # 设置字体头部信息
        fb.setupHead(unitsPerEm=metrics['unitsPerEm'])
        
        # 设置水平头部信息
        fb.setupHorizontalHeader(
            ascent=metrics['ascender'],
            descent=metrics['descender']
        )
        
        # 设置最大轮廓信息
        fb.setupMaxp()
        
        # 设置名称表
        fb.setupNameTable({
            'familyName': basic_info['fontFamily'],
            'styleName': 'Regular',
            'uniqueFontIdentifier': f"{basic_info['fontFamily']}-Regular-1.0",
            'fullName': basic_info['fontName'],
            'version': 'Version 1.0',
            'psName': basic_info['fontFamily'].replace(' ', '') + '-Regular',
            'designer': 'QuickFont AI',
            'description': 'Generated by QuickFont AI',
            'vendorURL': 'https://quickfont.ai',
        })
        
        # 设置 OS/2 表
        fb.setupOS2(
            sTypoAscender=metrics['ascender'],
            sTypoDescender=metrics['descender'],
            sTypoLineGap=200,
            usWinAscent=metrics['ascender'],
            usWinDescent=abs(metrics['descender'])
        )
        
        # 设置 post 表
        fb.setupPost()
        
        # 保存字体文件
        fb.save(output_path)
        print(f"✅ 成功创建 TrueType 字体文件: {output_path}")
        print(f"📊 包含 {len(glyphs)} 个字形")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ 创建字体失败: {e}")
        print(traceback.format_exc())
        return False

def main():
    parser = argparse.ArgumentParser(description='生成字体文件')
    parser.add_argument('--spec', required=True, help='设计规格JSON文件路径')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--font-id', required=True, help='字体ID')
    
    args = parser.parse_args()
    
    # 加载规格
    spec = load_spec(args.spec)
    
    # 确保输出目录存在
    os.makedirs(args.output, exist_ok=True)
    
    # 生成字体文件
    output_path = os.path.join(args.output, f"{args.font_id}.ttf")
    create_font(spec, output_path)
    
    print(f"成功生成字体: {output_path}")

if __name__ == '__main__':
    main()

