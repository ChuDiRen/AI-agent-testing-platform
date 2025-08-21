"""
指标参数响应DTO
定义指标参数相关的响应数据结构
"""

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import Field
from app.dto.base import BaseResponse, PaginatedResponse


class IndicatorParameterResponse(BaseResponse):
    """
    指标参数响应DTO
    """
    id: int = Field(description="参数ID")
    indicator_name: str = Field(description="指标名称")
    sequence_number: int = Field(description="序列号")
    parameter_name: str = Field(description="参数名称")
    parameter_value: Optional[str] = Field(description="参数值")
    parameter_type: str = Field(description="参数类型")
    parameter_description: Optional[str] = Field(description="参数描述")
    is_required: int = Field(description="是否必需(0:否,1:是)")
    default_value: Optional[str] = Field(description="默认值")
    validation_rule: Optional[str] = Field(description="验证规则")
    parameter_group: Optional[str] = Field(description="参数分组")
    sort_order: int = Field(description="排序顺序")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    @classmethod
    def from_entity(cls, parameter) -> "IndicatorParameterResponse":
        """
        从指标参数实体创建响应对象
        
        Args:
            parameter: 指标参数实体对象
            
        Returns:
            指标参数响应对象
        """
        return cls(
            id=parameter.id,
            indicator_name=parameter.indicator_name,
            sequence_number=parameter.sequence_number,
            parameter_name=parameter.parameter_name,
            parameter_value=parameter.parameter_value,
            parameter_type=parameter.parameter_type,
            parameter_description=parameter.parameter_description,
            is_required=parameter.is_required,
            default_value=parameter.default_value,
            validation_rule=parameter.validation_rule,
            parameter_group=parameter.parameter_group,
            sort_order=parameter.sort_order,
            created_at=parameter.created_at,
            updated_at=parameter.updated_at
        )


class IndicatorParameterConfigResponse(BaseResponse):
    """
    指标参数配置响应DTO
    """
    name: str = Field(description="参数名称")
    value: Any = Field(description="参数值（已转换类型）")
    type: str = Field(description="参数类型")
    description: Optional[str] = Field(description="参数描述")
    required: bool = Field(description="是否必需")
    default: Any = Field(description="默认值（已转换类型）")
    group: Optional[str] = Field(description="参数分组")
    order: int = Field(description="排序顺序")
    validation_rule: Optional[str] = Field(description="验证规则")
    
    @classmethod
    def from_entity(cls, parameter) -> "IndicatorParameterConfigResponse":
        """
        从指标参数实体创建配置响应对象
        
        Args:
            parameter: 指标参数实体对象
            
        Returns:
            指标参数配置响应对象
        """
        return cls(
            name=parameter.parameter_name,
            value=parameter.get_typed_value(),
            type=parameter.parameter_type,
            description=parameter.parameter_description,
            required=parameter.is_required_parameter(),
            default=parameter.get_typed_default_value(),
            group=parameter.parameter_group,
            order=parameter.sort_order,
            validation_rule=parameter.validation_rule
        )


class IndicatorParameterListResponse(PaginatedResponse):
    """
    指标参数列表响应DTO
    """
    items: List[IndicatorParameterResponse] = Field(description="参数列表")
    
    @classmethod
    def from_entities(cls, parameters: List, page: int, page_size: int, total: int) -> "IndicatorParameterListResponse":
        """
        从指标参数实体列表创建响应对象
        
        Args:
            parameters: 指标参数实体列表
            page: 当前页码
            page_size: 每页大小
            total: 总记录数
            
        Returns:
            指标参数列表响应对象
        """
        parameter_responses = [IndicatorParameterResponse.from_entity(param) for param in parameters]
        return cls.create(parameter_responses, page, page_size, total)


class IndicatorConfigResponse(BaseResponse):
    """
    指标完整配置响应DTO
    """
    indicator_name: str = Field(description="指标名称")
    sequence_number: int = Field(description="序列号")
    parameters: Dict[str, IndicatorParameterConfigResponse] = Field(description="参数字典")
    groups: Dict[str, List[str]] = Field(description="参数分组")
    required_parameters: List[str] = Field(description="必需参数列表")
    parameter_count: int = Field(description="参数数量")
    
    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> "IndicatorConfigResponse":
        """
        从配置字典创建响应对象
        
        Args:
            config: 配置字典
            
        Returns:
            指标配置响应对象
        """
        # 转换参数字典
        parameters = {}
        for param_name, param_config in config.get('parameters', {}).items():
            parameters[param_name] = IndicatorParameterConfigResponse(**param_config)
        
        return cls(
            indicator_name=config['indicator_name'],
            sequence_number=config['sequence_number'],
            parameters=parameters,
            groups=config.get('groups', {}),
            required_parameters=config.get('required_parameters', []),
            parameter_count=config.get('parameter_count', 0)
        )


class IndicatorListResponse(BaseResponse):
    """
    指标列表响应DTO
    """
    indicators: List[Dict[str, Any]] = Field(description="指标列表")
    total_count: int = Field(description="总指标数量")
    
    @classmethod
    def from_indicators(cls, indicators: List[Dict[str, Any]]) -> "IndicatorListResponse":
        """
        从指标列表创建响应对象
        
        Args:
            indicators: 指标信息列表
            
        Returns:
            指标列表响应对象
        """
        return cls(
            indicators=indicators,
            total_count=len(indicators)
        )


class IndicatorParameterValidationResponse(BaseResponse):
    """
    指标参数验证响应DTO
    """
    is_valid: bool = Field(description="是否验证通过")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="验证错误列表")
    warnings: List[Dict[str, str]] = Field(default_factory=list, description="验证警告列表")
    validated_values: Dict[str, Any] = Field(description="验证后的参数值")
    missing_required: List[str] = Field(default_factory=list, description="缺失的必需参数")
    
    @classmethod
    def create_success(cls, validated_values: Dict[str, Any]) -> "IndicatorParameterValidationResponse":
        """
        创建验证成功响应
        
        Args:
            validated_values: 验证后的参数值
            
        Returns:
            验证响应对象
        """
        return cls(
            is_valid=True,
            validated_values=validated_values
        )
    
    @classmethod
    def create_failure(cls, errors: List[Dict[str, str]], 
                      missing_required: List[str] = None,
                      warnings: List[Dict[str, str]] = None) -> "IndicatorParameterValidationResponse":
        """
        创建验证失败响应
        
        Args:
            errors: 错误列表
            missing_required: 缺失的必需参数
            warnings: 警告列表
            
        Returns:
            验证响应对象
        """
        return cls(
            is_valid=False,
            errors=errors or [],
            warnings=warnings or [],
            validated_values={},
            missing_required=missing_required or []
        )


class IndicatorParameterBatchOperationResponse(BaseResponse):
    """
    指标参数批量操作响应DTO
    """
    total: int = Field(description="总操作数量")
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    created_parameters: List[IndicatorParameterResponse] = Field(default_factory=list, description="创建的参数列表")
    failed_parameters: List[Dict[str, str]] = Field(default_factory=list, description="失败的参数信息")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.success_count / self.total if self.total > 0 else 0.0


class IndicatorParameterStatsResponse(BaseResponse):
    """
    指标参数统计响应DTO
    """
    total_indicators: int = Field(description="总指标数量")
    total_parameters: int = Field(description="总参数数量")
    parameters_by_type: Dict[str, int] = Field(description="按类型统计的参数数量")
    parameters_by_group: Dict[str, int] = Field(description="按分组统计的参数数量")
    required_parameters_count: int = Field(description="必需参数数量")
    optional_parameters_count: int = Field(description="可选参数数量")
    avg_parameters_per_indicator: float = Field(description="每个指标的平均参数数量")


class IndicatorParameterSimpleResponse(BaseResponse):
    """
    指标参数简单响应DTO（用于下拉选择等场景）
    """
    id: int = Field(description="参数ID")
    parameter_name: str = Field(description="参数名称")
    parameter_type: str = Field(description="参数类型")
    is_required: bool = Field(description="是否必需")
    parameter_group: Optional[str] = Field(description="参数分组")
    
    @classmethod
    def from_entity(cls, parameter) -> "IndicatorParameterSimpleResponse":
        """
        从指标参数实体创建简单响应对象
        
        Args:
            parameter: 指标参数实体对象
            
        Returns:
            指标参数简单响应对象
        """
        return cls(
            id=parameter.id,
            parameter_name=parameter.parameter_name,
            parameter_type=parameter.parameter_type,
            is_required=parameter.is_required_parameter(),
            parameter_group=parameter.parameter_group
        )


# 导出所有响应DTO
__all__ = [
    "IndicatorParameterResponse",
    "IndicatorParameterConfigResponse",
    "IndicatorParameterListResponse",
    "IndicatorConfigResponse",
    "IndicatorListResponse",
    "IndicatorParameterValidationResponse",
    "IndicatorParameterBatchOperationResponse",
    "IndicatorParameterStatsResponse",
    "IndicatorParameterSimpleResponse",
]
