"""
插件校验服务
提供 config_schema 校验、用例格式校验等功能
"""
import json
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PluginValidator:
    """插件校验器"""
    
    # 支持的参数类型（扩展支持 UI 组件类型）
    VALID_PARAM_TYPES = {
        # 标准 JSON Schema 类型
        "string", "integer", "number", "boolean", "array", "object",
        # 扩展 UI 组件类型
        "select", "file", "path", "text", "password", "date", "datetime", "enum"
    }
    
    @staticmethod
    def compute_hash(content: bytes) -> str:
        """
        计算内容的 SHA256 哈希值
        
        Args:
            content: 字节内容
        
        Returns:
            SHA256 哈希字符串（64位十六进制）
        """
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def validate_config_schema(config_schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        校验 config_schema 格式是否正确
        
        Args:
            config_schema: 配置参数 Schema
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        if not config_schema:
            return True, []  # 空 schema 视为有效
        
        # 检查基本结构
        if not isinstance(config_schema, dict):
            errors.append("config_schema 必须是字典类型")
            return False, errors
        
        # 检查 properties
        properties = config_schema.get("properties", {})
        params = config_schema.get("params", [])
        
        # 校验 params 列表
        for idx, param in enumerate(params):
            if not isinstance(param, dict):
                errors.append(f"params[{idx}] 必须是字典类型")
                continue
            
            # 必填字段
            if "name" not in param:
                errors.append(f"params[{idx}] 缺少必填字段 'name'")
            # 参数名格式校验已移除，允许任意格式的参数名
            # 因为不同插件可能有不同的参数命名规范
            
            # 类型校验（宽松模式，仅记录警告不报错）
            # param_type = param.get("type", "string")
            # 不再强制校验类型，允许插件自定义类型
            
            # 选项校验（如果有）
            options = param.get("options")
            if options is not None and not isinstance(options, list):
                errors.append(f"params[{idx}].options 必须是列表类型")
        
        # 校验 properties（宽松模式，只检查基本结构）
        for prop_name, prop_def in properties.items():
            if not isinstance(prop_def, dict):
                errors.append(f"properties.{prop_name} 必须是字典类型")
                continue
            # 不再强制校验 type 字段，允许插件自定义类型
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_test_case_yaml(content: str) -> Tuple[bool, List[str]]:
        """
        校验测试用例 YAML 格式
        
        Args:
            content: YAML 内容字符串
        
        Returns:
            (是否有效, 错误列表)
        """
        import yaml
        
        errors = []
        
        if not content or not content.strip():
            errors.append("用例内容不能为空")
            return False, errors
        
        try:
            # 支持多文档 YAML
            docs = list(yaml.safe_load_all(content))
            
            if not docs:
                errors.append("YAML 解析结果为空")
                return False, errors
            
            for idx, doc in enumerate(docs):
                if doc is None:
                    continue
                
                if not isinstance(doc, dict):
                    errors.append(f"文档[{idx}] 必须是字典类型")
                    continue
                
                # 检查必要字段（根据实际用例格式调整）
                # 常见必填字段: desc/name, steps
                if "desc" not in doc and "name" not in doc and "case_name" not in doc:
                    errors.append(f"文档[{idx}] 缺少描述字段 (desc/name/case_name)")
                
                # 检查 steps 字段
                steps = doc.get("steps")
                if steps is not None:
                    if not isinstance(steps, list):
                        errors.append(f"文档[{idx}].steps 必须是列表类型")
                    elif len(steps) == 0:
                        errors.append(f"文档[{idx}].steps 不能为空列表")
        
        except yaml.YAMLError as e:
            errors.append(f"YAML 解析错误: {str(e)}")
        except Exception as e:
            errors.append(f"校验异常: {str(e)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_test_case_json(content: str) -> Tuple[bool, List[str]]:
        """
        校验测试用例 JSON 格式
        
        Args:
            content: JSON 内容字符串
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        if not content or not content.strip():
            errors.append("用例内容不能为空")
            return False, errors
        
        try:
            data = json.loads(content)
            
            # 支持单个用例或用例列表
            cases = data if isinstance(data, list) else [data]
            
            for idx, case in enumerate(cases):
                if not isinstance(case, dict):
                    errors.append(f"用例[{idx}] 必须是字典类型")
                    continue
                
                # 检查必要字段
                if "desc" not in case and "name" not in case and "case_name" not in case:
                    errors.append(f"用例[{idx}] 缺少描述字段 (desc/name/case_name)")
                
                # 检查 steps 字段
                steps = case.get("steps")
                if steps is not None:
                    if not isinstance(steps, list):
                        errors.append(f"用例[{idx}].steps 必须是列表类型")
                    elif len(steps) == 0:
                        errors.append(f"用例[{idx}].steps 不能为空列表")
        
        except json.JSONDecodeError as e:
            errors.append(f"JSON 解析错误: {str(e)}")
        except Exception as e:
            errors.append(f"校验异常: {str(e)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_test_case(content: str) -> Tuple[bool, List[str], str]:
        """
        自动检测并校验测试用例格式（JSON 或 YAML）
        
        Args:
            content: 用例内容字符串
        
        Returns:
            (是否有效, 错误列表, 检测到的格式 'json'/'yaml')
        """
        if not content or not content.strip():
            return False, ["用例内容不能为空"], "unknown"
        
        stripped = content.strip()
        
        # 检测格式
        if stripped.startswith('{') or stripped.startswith('['):
            # JSON 格式
            valid, errors = PluginValidator.validate_test_case_json(content)
            return valid, errors, "json"
        else:
            # YAML 格式
            valid, errors = PluginValidator.validate_test_case_yaml(content)
            return valid, errors, "yaml"
    
    @staticmethod
    def validate_plugin_package(zip_path: Path) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        校验插件 ZIP 包结构
        
        Args:
            zip_path: ZIP 文件路径
        
        Returns:
            (是否有效, 错误列表, 解析出的元信息)
        """
        import zipfile
        
        errors = []
        meta = {}
        
        if not zip_path.exists():
            errors.append(f"文件不存在: {zip_path}")
            return False, errors, meta
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                names = zf.namelist()
                
                # 检查是否有 setup.py
                has_setup = any('setup.py' in n for n in names)
                if not has_setup:
                    errors.append("缺少 setup.py 文件")
                
                # 检查是否有 requirements.txt（可选但推荐）
                has_requirements = any('requirements.txt' in n for n in names)
                meta["has_requirements"] = has_requirements
                
                # 检查是否有 plugin.yaml（推荐）
                has_plugin_yaml = any('plugin.yaml' in n for n in names)
                meta["has_plugin_yaml"] = has_plugin_yaml
                
                # 检查是否有 keywords.yaml（可选）
                has_keywords = any('keywords.yaml' in n for n in names)
                meta["has_keywords"] = has_keywords
                
                meta["file_count"] = len(names)
        
        except zipfile.BadZipFile:
            errors.append("无效的 ZIP 文件")
        except Exception as e:
            errors.append(f"解析 ZIP 失败: {str(e)}")
        
        return len(errors) == 0, errors, meta


# 全局校验器实例
plugin_validator = PluginValidator()
