// 共享类型定义，基于PRD JSON Schema标准

export interface FontSpecMetadata {
  specVersion: string;
  generatedAt: string;
  requestId: string;
  fontId: string;
  generator?: string;
}

export interface FontMetrics {
  unitsPerEm: number;
  xHeight: number;
  capHeight: number;
  ascender: number;
  descender: number;
  lineHeight: number;
  baseline: number;
}

export interface FontSpacing {
  letterSpacing: number;
  wordSpacing: number;
  tracking?: number;
  kerning: boolean;
}

export interface FontProportions {
  contrast: 'none' | 'low' | 'medium' | 'high';
  strokeWidth: number;
  xHeightRatio: number;
  capHeightRatio: number;
  aspectRatio: 'condensed' | 'normal' | 'extended';
}

export interface FontBasicInfo {
  fontFamily: string;
  fontName: string;
  style: 'serif' | 'sans-serif' | 'monospace';
  weight: 'thin' | 'light' | 'normal' | 'bold';
  category: 'display' | 'text' | 'decorative';
  language: string;
  version: string;
}

export interface VisualStyle {
  terminals: 'straight' | 'curved' | 'angled';
  corners: 'sharp' | 'rounded' | 'soft';
  aperture: 'closed' | 'open' | 'semi-open';
  axis: 'vertical' | 'angled' | 'mixed';
  stress: 'none' | 'vertical' | 'angled' | 'reverse';
}

export interface StyleDefinition {
  concept: string;
  characteristics: string[];
  visualStyle: VisualStyle;
}

export interface CharacterSet {
  uppercase: string[];
  lowercase: string[];
  numbers: string[];
  punctuation: string[];
  specialChars?: string[];
}

export interface ConsistencyRules {
  strokeWeight: 'uniform' | 'varied' | 'modulated';
  characterWidth: 'monospace' | 'proportional';
  baseline: 'aligned' | 'varied';
  opticalCorrection: boolean;
}

export interface LegibilityRules {
  minSize: number;
  maxSize: number;
  screenOptimized: boolean;
  printOptimized: boolean;
}

export interface DesignRules {
  consistency: ConsistencyRules;
  legibility: LegibilityRules;
}

export interface FontFeatures {
  kerning: boolean;
  ligatures?: boolean;
  alternates?: boolean;
  numerals: 'lining' | 'oldstyle' | 'tabular';
}

export interface TechnicalSpecs {
  format: string[];
  encoding: string;
  hinting: 'none' | 'TrueType' | 'PostScript';
  compression: 'none' | 'standard' | 'optimized';
  features: FontFeatures;
}

export interface QualityMetrics {
  readabilityScore: number;
  aestheticScore: number;
  technicalScore: number;
  overallScore: number;
}

export interface FontDesignSpec {
  metadata: FontSpecMetadata;
  basicInfo: FontBasicInfo;
  designParameters: {
    metrics: FontMetrics;
    spacing: FontSpacing;
    proportions: FontProportions;
  };
  styleDefinition: StyleDefinition;
  characterSet: CharacterSet;
  designRules: DesignRules;
  technicalSpecs: TechnicalSpecs;
  qualityMetrics: QualityMetrics;
}

export interface UserRequirement {
  textDescription: string;
  fontType: 'serif' | 'sans-serif' | 'monospace';
  fontWeight: 'normal' | 'bold';
  characterSet: {
    uppercase: boolean;
    lowercase: boolean;
    numbers: boolean;
    punctuation: boolean;
  };
  useCase?: string;
}

export interface APIResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

// 字体状态枚举
export type FontStatus = 'generating' | 'completed' | 'failed'

// 字体列表项
export interface FontListItem {
  font_id: string
  font_family: string
  font_name: string
  style: 'serif' | 'sans-serif' | 'monospace'
  weight: string
  category: string
  status: FontStatus
  file_path: string | null
  created_at: string
  updated_at: string
}

// 字体列表响应
export interface FontListResponse {
  fonts: FontListItem[]
  total: number
  limit: number
  offset: number
}

// 字体详情（包含规格）
export interface FontWithSpec extends FontListItem {
  spec: FontDesignSpec
}

