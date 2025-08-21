"""
指标参数请求DTO
定义指标参数相关的请求数据结构
"""

from typing import Optional, List, Any, Dict
from pydantic import Field, validator
from app.dto.base import BaseRequest, SearchRequest


class IndicatorParameterCreateRequest(BaseRequest):
    """
    创建指标参数请求DTO
    """
    indicator_name: str = Field(min_length=1, max_length=100, description="指标名称")
    sequence_number: int = Field(ge=0, description="序列号")
    parameter_name: str = Field(min_length=1, max_length=100, description="参数名称")
    parameter_value: Optional[str] = Field(default=None, description="参数值")
    parameter_type: str = Field(default="string", description="参数类型")
    parameter_description: Optional[str] = Field(default=None, description="参数描述")
    is_required: int = Field(default=0, ge=0, le=1, description="是否必需(0:否,1:是)")
    default_value: Optional[str] = Field(default=None, description="默认值")
    validation_rule: Optional[str] = Field(default=None, description="验证规则")
    parameter_group: Optional[str] = Field(default=None, max_length=50, description="参数分组")
    sort_order: int = Field(default=0, ge=0, description="排序顺序")
    
    @validator('parameter_type')
    def validate_parameter_type(cls, v):
        """验证参数类型"""
        allowed_types = ['string', 'number', 'boolean', 'json']
        if v not in allowed_types:
            raise ValueError(f'Parameter type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('indicator_name', 'parameter_name')
    def validate_names(cls, v):
        """验证名称格式"""
        return v.strip()
    
    @validator('parameter_group')
    def validate_parameter_group(cls, v):
        """验证参数分组"""
        if v is not None:
            return v.strip()
        return v


class IndicatorParameterUpdateRequest(BaseRequest):
    """
    更新指标参数请求DTO
    """
    parameter_value: Optional[str] = Field(default=None, description="参数值")
    parameter_type: Optional[str] = Field(default=None, description="参数类型")
    parameter_description: Optional[str] = Field(default=None, description="参数描述")
    is_required: Optional[int] = Field(default=None, ge=0, le=1, description="是否必需(0:否,1:是)")
    default_value: Optional[str] = Field(default=None, description="默认值")
    validation_rule: Optional[str] = Field(default=None, description="验证规则")
    parameter_group: Optional[str] = Field(default=None, max_length=50, description="参数分组")
    sort_order: Optional[int] = Field(default=None, ge=0, description="排序顺序")
    
    @validator('parameter_type')
    def validate_parameter_type(cls, v):
        """验证参数类型"""
        if v is not None:
            allowed_types = ['string', 'number', 'boolean', 'json']
            if v not in allowed_types:
                raise ValueError(f'Parameter type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('parameter_group')
    def validate_parameter_group(cls, v):
        """验证参数分组"""
        if v is not None:
            return v.strip()
        return v


class IndicatorParameterBatchSaveRequest(BaseRequest):
    """
    批量保存指标参数请求DTO
    """
    indicator_name: str = Field(min_length=1, max_length=100, description="指标名称")
    sequence_number: int = Field(ge=0, description="序列号")
    parameters: List[Dict[str, Any]] = Field(min_items=1, description="参数列表")
    
    @validator('indicator_name')
    def validate_indicator_name(cls, v):
        """验证指标名称"""
        return v.strip()
    
    @validator('parameters')
    def validate_parameters(cls, v):
        """验证参数列表"""
        if not v:
            raise ValueError('Parameters list cannot be empty')
        
        # 检查参数名称唯一性
        parameter_names = []
        for param in v:
            if 'parameter_name' not in param:
                raise ValueError('Each parameter must have a parameter_name')
            
            param_name = param['parameter_name'].strip()
            if param_name in parameter_names:
                raise ValueError(f'Duplicate parameter name: {param_name}')
            parameter_names.append(param_name)
            
            # 验证参数类型
            param_type = param.get('parameter_type', 'string')
            allowed_types = ['string', 'number', 'boolean', 'json']
            if param_type not in allowed_types:
                raise ValueError(f'Invalid parameter type for {param_name}: {param_type}')
        
        return v


class IndicatorParameterQueryRequest(BaseRequest):
    """
    查询指标参数请求DTO
    """
    indicator_name: str = Field(min_length=1, max_length=100, description="指标名称")
    sequence_number: int = Field(ge=0, description="序列号")
    parameter_group: Optional[str] = Field(default=None, description="参数分组")
    include_config: bool = Field(default=False, description="是否包含配置信息")
    
    @validator('indicator_name')
    def validate_indicator_name(cls, v):
        """验证指标名称"""
        return v.strip()


class IndicatorParameterSearchRequest(SearchRequest):
    """
    搜索指标参数请求DTO
    """
    indicator_name: Optional[str] = Field(default=None, description="指标名称")
    parameter_type: Optional[str] = Field(default=None, description="参数类型")
    parameter_group: Optional[str] = Field(default=None, description="参数分组")
    is_required: Optional[int] = Field(default=None, ge=0, le=1, description="是否必需")
    
    @validator('parameter_type')
    def validate_parameter_type(cls, v):
        """验证参数类型"""
        if v is not None:
            allowed_types = ['string', 'number', 'boolean', 'json']
            if v not in allowed_types:
                raise ValueError(f'Parameter type must be one of: {", ".join(allowed_types)}')
        return v


class IndicatorParameterDeleteRequest(BaseRequest):
    """
    删除指标参数请求DTO
    """
    indicator_name: str = Field(min_length=1, max_length=100, description="指标名称")
    sequence_number: int = Field(ge=0, description="序列号")
    parameter_names: Optional[List[str]] = Field(default=None, description="要删除的参数名称列表")
    delete_all: bool = Field(default=False, description="是否删除所有参数")
    
    @validator('indicator_name')
    def validate_indicator_name(cls, v):
        """验证指标名称"""
        return v.strip()
    
    @validator('parameter_names')
    def validate_parameter_names(cls, v, values):
        """验证参数名称列表"""
        delete_all = values.get('delete_all', False)
        
        if not delete_all and (not v or len(v) == 0):
            raise ValueError('Must specify parameter_names or set delete_all to true')
        
        if delete_all and v:
            raise ValueError('Cannot specify parameter_names when delete_all is true')
        
        if v:
            # 去重并清理空白字符
            cleaned_names = [name.strip() for name in v if name.strip()]
            return list(set(cleaned_names))
        
        return v


class IndicatorParameterValidateRequest(BaseRequest):
    """
    验证指标参数请求DTO
    """
    indicator_name: str = Field(min_length=1, max_length=100, description="指标名称")
    sequence_number: int = Field(ge=0, description="序列号")
    parameter_values: Dict[str, Any] = Field(description="参数值字典")
    
    @validator('indicator_name')
    def validate_indicator_name(cls, v):
        """验证指标名称"""
        return v.strip()


class IndicatorParameterCopyRequest(BaseRequest):
    """
    复制指标参数请求DTO
    """
    source_indicator_name: str = Field(min_length=1, max_length=100, description="源指标名称")
    source_sequence_number: int = Field(ge=0, description="源序列号")
    target_indicator_name: str = Field(min_length=1, max_length=100, description="目标指标名称")
    target_sequence_number: int = Field(ge=0, description="目标序列号")
    overwrite_existing: bool = Field(default=False, description="是否覆盖已存在的参数")
    
    @validator('source_indicator_name', 'target_indicator_name')
    def validate_indicator_names(cls, v):
        """验证指标名称"""
        return v.strip()
    
    @validator('target_indicator_name')
    def validate_different_target(cls, v, values):
        """验证目标指标不能与源指标相同"""
        source_name = values.get('source_indicator_name')
        source_seq = values.get('source_sequence_number')
        target_seq = values.get('target_sequence_number')
        
        if (source_name and v == source_name and 
            source_seq is not None and target_seq is not None and 
            source_seq == target_seq):
            raise ValueError('Target indicator cannot be the same as source indicator')
        
        return v


# 导出所有请求DTO
__all__ = [
    "IndicatorParameterCreateRequest",
    "IndicatorParameterUpdateRequest",
    "IndicatorParameterBatchSaveRequest",
    "IndicatorParameterQueryRequest",
    "IndicatorParameterSearchRequest",
    "IndicatorParameterDeleteRequest",
    "IndicatorParameterValidateRequest",
    "IndicatorParameterCopyRequest",
]
