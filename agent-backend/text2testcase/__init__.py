"""text2testcase - AI测试用例生成器

使用: from text2testcase import generator
     result = await generator.generate("需求描述", test_type="API")
"""
import sys
import os

# Windows控制台UTF-8编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from .config import Config
from .generator import generator, TestCaseGeneratorV3
from .models import TestCaseState
from .batch_processor import BatchProcessor, BatchConfig, BatchResult

__all__ = [
    'generator',
    'TestCaseGeneratorV3',
    'TestCaseState',
    'Config',
    'BatchProcessor',
    'BatchConfig',
    'BatchResult',
]

__version__ = "5.0.0"

