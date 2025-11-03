"""
字体规格解析工具
用于解析和验证设计规格JSON
"""

import json
from typing import Dict, Any

def validate_spec(spec: Dict[str, Any]) -> bool:
    """验证规格是否符合要求"""
    required_fields = [
        'metadata',
        'basicInfo',
        'designParameters',
        'styleDefinition',
        'characterSet',
    ]
    
    for field in required_fields:
        if field not in spec:
            raise ValueError(f"缺少必需字段: {field}")
    
    # 验证度量参数
    metrics = spec['designParameters']['metrics']
    if metrics['unitsPerEm'] <= 0:
        raise ValueError("unitsPerEm必须大于0")
    
    if metrics['ascender'] <= metrics['capHeight'] <= metrics['xHeight']:
        raise ValueError("度量参数顺序错误: ascender > capHeight > xHeight")
    
    return True

def parse_spec(spec_path: str) -> Dict[str, Any]:
    """解析规格文件"""
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    validate_spec(spec)
    return spec








