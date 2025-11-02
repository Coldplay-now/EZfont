# DeepSeek 提示词优化文档

## 优化日期
2025年11月1日

## 优化原因

Phase 2 实现了专业级参数化字形生成系统后，需要确保 DeepSeek AI 能够：
1. 理解所有新增的 visualStyle 参数的含义
2. 根据用户描述智能选择合适的参数值
3. 确保各参数之间协调一致，形成统一的视觉风格
4. 避免参数冲突或不合理组合

## 优化内容

### 1. 添加详细参数说明

为每个关键参数添加了详细说明和使用场景：

#### proportions.contrast（笔画对比度）
- **none**: 无对比，横竖笔画等宽 → 现代几何字体
- **low**: 15% 对比度 → 简洁 sans-serif
- **medium**: 30% 对比度 → 平衡的设计
- **high**: 50% 对比度 → 优雅的 serif 字体

#### proportions.strokeWidth（基础笔画宽度）
- **60-70**: 细线条 → thin, elegant, delicate
- **75-85**: 标准线条 → normal, balanced
- **90-105**: 粗线条 → bold, strong
- **110-120**: 超粗线条 → black, heavy, display

#### visualStyle.terminals（笔画末端）
- **straight**: 直线末端 → 现代、极简、几何
- **curved**: 圆形末端 → 友好、圆润、有机
- **angled**: 斜切末端 → 时尚、创意、动态

#### visualStyle.corners（拐角处理）
- **sharp**: 尖锐拐角，0% 圆角 → 现代、几何、锐利
- **rounded**: 圆润拐角，30% 圆角 → 友好、平易近人
- **soft**: 柔和拐角，50% 圆角 → 温柔、有机、流畅

#### visualStyle.aperture（字怀开口度）
- **closed**: 小开口，10% → 紧凑、正式、传统
- **semi-open**: 中等开口，25% → 平衡、实用
- **open**: 大开口，40% → 现代、清晰、易读

#### visualStyle.axis（笔画轴线）
- **vertical**: 垂直轴线 → 稳定、正式、现代
- **angled**: 倾斜轴线 → 动感、优雅、书法风格
- **mixed**: 混合轴线 → 创意、独特、变化

#### visualStyle.stress（笔画重心）
- **none**: 无应力，笔画均匀 → 几何、现代
- **vertical**: 垂直应力，上下粗左右细 → 经典 serif
- **angled**: 倾斜应力 → 书法风格、动态
- **reverse**: 反向应力，左右粗上下细 → 创意、独特

### 2. 智能参数选择指南

为常见风格提供了参数组合建议：

| 风格 | contrast | terminals | corners | aperture | axis | stress | strokeWidth |
|------|----------|-----------|---------|----------|------|--------|-------------|
| 几何/现代 | none | straight | sharp/rounded | - | vertical | none | 75-85 |
| 优雅/衬线 | medium/high | curved | soft | - | angled | vertical | 70-85 |
| 友好/圆润 | low | curved | soft | open | vertical | none | 75-85 |
| 动感/创意 | - | angled | sharp | - | angled | angled | 80-95 |
| 哥特/尖锐 | high | angled | sharp | - | vertical | vertical | 85-100 |
| 简洁/清晰 | low/medium | straight | - | open | vertical | none | 70-80 |

### 3. 增强用户提示

优化了用户提示词（generateUserPrompt），添加了：

1. **特征分析指导**：
   - 分析用户描述中的关键词
   - 参考智能参数选择指南
   - 确保参数协调一致

2. **strokeWidth 选择指导**：
   - 根据用户描述的字重和风格智能选择
   - 细腻/纤细 → 60-70
   - 粗壮/厚重 → 100-120
   - 普通情况 → 75-85

3. **contrast 选择指导**：
   - 根据字体类型和风格选择
   - 几何/现代 sans-serif → none/low
   - 传统 serif → medium/high
   - 人文主义 sans-serif → low/medium

## 优化效果预期

### 1. 更准确的参数生成
AI 能够根据用户描述生成更符合预期的参数组合，例如：
- "现代几何风格" → contrast: none, terminals: straight, corners: sharp
- "优雅衬线字体" → contrast: high, terminals: curved, stress: vertical

### 2. 更好的参数协调
避免出现不协调的参数组合，例如：
- ❌ 不应该：contrast: high + terminals: straight + stress: none（矛盾）
- ✅ 应该：contrast: high + terminals: curved + stress: vertical（协调）

### 3. 更智能的风格理解
能够理解更复杂的描述，例如：
- "现代的哥特风格，有动感，平衡且优雅"
  → contrast: medium-high, terminals: angled, corners: sharp, axis: angled

## 测试建议

使用不同风格的描述测试 AI 的参数生成能力：

### 测试用例 1：几何现代风格
**描述**："生成一个现代的几何风格字体，干净简洁"
**期望参数**：
```json
{
  "proportions": {
    "contrast": "none",
    "strokeWidth": 75
  },
  "visualStyle": {
    "terminals": "straight",
    "corners": "rounded",
    "aperture": "open",
    "axis": "vertical",
    "stress": "none"
  }
}
```

### 测试用例 2：优雅衬线风格
**描述**："生成一个优雅的衬线字体，适合印刷"
**期望参数**：
```json
{
  "proportions": {
    "contrast": "high",
    "strokeWidth": 70
  },
  "visualStyle": {
    "terminals": "curved",
    "corners": "soft",
    "aperture": "semi-open",
    "axis": "angled",
    "stress": "vertical"
  }
}
```

### 测试用例 3：动感创意风格
**描述**："生成一个现代的哥特风格字体，有动感，平衡且优雅"
**期望参数**：
```json
{
  "proportions": {
    "contrast": "medium",
    "strokeWidth": 85
  },
  "visualStyle": {
    "terminals": "angled",
    "corners": "sharp",
    "aperture": "semi-open",
    "axis": "angled",
    "stress": "vertical"
  }
}
```

### 测试用例 4：友好圆润风格
**描述**："生成一个友好温暖的字体，适合儿童读物"
**期望参数**：
```json
{
  "proportions": {
    "contrast": "low",
    "strokeWidth": 80
  },
  "visualStyle": {
    "terminals": "curved",
    "corners": "soft",
    "aperture": "open",
    "axis": "vertical",
    "stress": "none"
  }
}
```

## 监控要点

1. **参数准确性**：检查生成的参数是否符合描述
2. **参数协调性**：检查参数组合是否合理
3. **视觉效果**：检查生成的字体是否符合预期风格
4. **错误率**：监控 AI 生成无效参数的频率

## 持续优化

如果发现 AI 生成的参数不准确，可以：

1. **扩展智能参数选择指南**：添加更多风格的参数组合
2. **添加反例说明**：告诉 AI 哪些组合是不合理的
3. **增加参数约束**：在提示词中添加参数之间的依赖关系
4. **调整 temperature**：如果生成结果太随机，降低 temperature（当前 0.7）

## 相关文件

- `/Users/xt/LXT/code/trae/1101-cursor2/QuickFont/backend/src/services/aiAnalyzer.ts` - AI 分析服务
- `/Users/xt/LXT/code/trae/1101-cursor2/QuickFont/font-generator/glyph_designer.py` - 字形设计器
- `/Users/xt/LXT/code/trae/1101-cursor2/QuickFont/PHASE2_IMPLEMENTATION.md` - Phase 2 实现文档

---

**优化版本**: v1.0  
**兼容系统版本**: Phase 2 Complete


