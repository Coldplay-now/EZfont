# 字体文件修复说明

## 问题描述
之前生成的 TTF 字体文件无法在 macOS 上安装，提示"不包含可安装在macOS上的字体"。

## 根本原因
使用了 CFF（PostScript）格式而不是标准的 TrueType 格式，macOS 对 CFF 字体有更严格的验证要求。

## 修复方案

### 1. 重写字体生成器
- 改用 **TrueType 格式** (`isTTF=True`)
- 使用 `TTGlyphPen` 而不是 `T2CharStringPen`
- 使用 `setupGlyf()` 而不是 `setupCFF()`
- 添加所有必需的字体表（head, hhea, maxp, OS/2, post, name, cmap, glyf, hmtx）

### 2. 字形设计
MVP 版本使用简单的**矩形占位符**：
- 大写字母：高度 = capHeight（750）
- 小写字母：高度 = xHeight（550）
- 数字：高度 = capHeight
- 标点符号：较小尺寸

### 3. 包含的字符
- **大写字母**: A-Z (26个)
- **小写字母**: a-z (26个)
- **数字**: 0-9 (10个)
- **标点符号**: .,;:!?\'"()-[]{}/@#$%&*+=<> (23个)
- **特殊字形**: .notdef, space

总计: **87个字形**

## 测试步骤

### 1. 重启后端服务
```bash
cd /Users/xt/LXT/code/trae/1101-cursor2/QuickFont
./stop.sh
./start.sh
```

### 2. 生成新字体
1. 打开前端页面: http://localhost:5174/create
2. 填写字体描述（至少10个字符）
3. 点击 "Generate My Font" 按钮
4. 等待生成完成

### 3. 下载并测试
1. 在字体规格页面点击 "Download Font" 按钮
2. 双击下载的 `.ttf` 文件
3. macOS Font Book 应该能正常打开并显示字体预览
4. 点击"安装字体"按钮应该能成功安装

### 4. 验证字体
在 Font Book 中检查：
- ✅ 字体名称正确显示
- ✅ 包含 A-Z, a-z, 0-9 等字符
- ✅ 字形显示为简单的矩形（MVP版本）
- ✅ 可以在文本编辑器中使用

## 已知限制（MVP版本）

1. **字形设计**: 所有字符使用简单的矩形，不是真实的字母形状
2. **样式应用**: AI分析的设计参数暂未完全应用到字形上
3. **高级特性**: 不支持连字（ligatures）、字距微调（kerning）等

## 未来改进

1. **Phase 2**: 实现参数化字形生成，根据设计参数绘制真实字母
2. **Phase 3**: 应用AI分析的视觉风格（圆角、笔画宽度、对比度等）
3. **Phase 4**: 支持高级 OpenType 特性

## 技术细节

### 字体表结构
```
TrueType Font Tables:
├── head  - 字体头部（unitsPerEm, 版本等）
├── hhea  - 水平头部（ascent, descent）
├── maxp  - 最大配置（字形数量等）
├── OS/2  - OS/2 和 Windows 度量
├── post  - PostScript 信息
├── name  - 命名表（字体名称、版本等）
├── cmap  - 字符到字形映射
├── glyf  - 字形轮廓数据
└── hmtx  - 水平度量（字形宽度）
```

### FontBuilder 调用顺序
1. `FontBuilder(unitsPerEm, isTTF=True)`
2. `setupGlyphOrder()`
3. `setupCharacterMap()`
4. `setupGlyf()` ← TrueType 格式
5. `setupHorizontalMetrics()`
6. `setupHead()`
7. `setupHhea()`
8. `setupMaxp()`
9. `setupNameTable()`
10. `setupOS2()`
11. `setupPost()`
12. `save()`

## 相关文件

- `font-generator/generator.py` - 字体生成器主程序
- `backend/src/services/fontGenerator.ts` - 后端调用服务
- `backend/src/services/aiAnalyzer.ts` - AI 设计分析

## 参考资料

- [FontTools Documentation](https://fonttools.readthedocs.io/)
- [TrueType Reference Manual](https://developer.apple.com/fonts/TrueType-Reference-Manual/)
- [OpenType Specification](https://docs.microsoft.com/en-us/typography/opentype/spec/)


