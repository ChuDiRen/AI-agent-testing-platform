"""
指标参数实体
定义指标参数相关的数据库模型
"""

from sqlalchemy import Column, String, Integer, Text, Index
from typing import Optional, Dict, Any
from .base import BaseEntity


class IndicatorParameter(BaseEntity):
    """
    指标参数实体类
    用于存储指标的参数配置信息
    """
    __tablename__ = "indicator_parameters"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 指标信息
    indicator_name = Column(String(100), nullable=False, index=True, comment="指标名称")
    sequence_number = Column(Integer, nullable=False, comment="序列号")
    
    # 参数信息
    parameter_name = Column(String(100), nullable=False, comment="参数名称")
    parameter_value = Column(Text, comment="参数值")
    parameter_type = Column(String(50), default="string", comment="参数类型(string/number/boolean/json)")
    parameter_description = Column(Text, comment="参数描述")
    
    # 配置信息
    is_required = Column(Integer, default=0, comment="是否必需(0:否,1:是)")
    default_value = Column(Text, comment="默认值")
    validation_rule = Column(Text, comment="验证规则")
    
    # 分组和排序
    parameter_group = Column(String(50), comment="参数分组")
    sort_order = Column(Integer, default=0, comment="排序顺序")

    # 创建复合索引
    __table_args__ = (
        Index('idx_indicator_sequence', 'indicator_name', 'sequence_number'),
        Index('idx_parameter_group', 'parameter_group', 'sort_order'),
    )

    def validate(self) -> bool:
        """
        验证指标参数数据的有效性
        """
        if not self.indicator_name or len(self.indicator_name.strip()) == 0:
            return False
        if not self.parameter_name or len(self.parameter_name.strip()) == 0:
            return False
        if self.sequence_number is None or self.sequence_number < 0:
            return False
        if self.parameter_type not in ['string', 'number', 'boolean', 'json']:
            return False
        return True

    def before_save(self) -> None:
        """
        保存前的处理
        """
        super().before_save()
        # 清理空白字符
        if self.indicator_name:
            self.indicator_name = self.indicator_name.strip()
        if self.parameter_name:
            self.parameter_name = self.parameter_name.strip()
        if self.parameter_group:
            self.parameter_group = self.parameter_group.strip()

    def get_typed_value(self) -> Any:
        """
        根据参数类型返回正确类型的值
        """
        if not self.parameter_value:
            return self.get_typed_default_value()
            
        try:
            if self.parameter_type == 'number':
                # 尝试转换为整数，如果失败则转换为浮点数
                if '.' in str(self.parameter_value):
                    return float(self.parameter_value)
                else:
                    return int(self.parameter_value)
            elif self.parameter_type == 'boolean':
                return str(self.parameter_value).lower() in ['true', '1', 'yes', 'on']
            elif self.parameter_type == 'json':
                import json
                return json.loads(self.parameter_value)
            else:  # string
                return str(self.parameter_value)
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.parameter_value

    def get_typed_default_value(self) -> Any:
        """
        根据参数类型返回正确类型的默认值
        """
        if not self.default_value:
            return None
            
        try:
            if self.parameter_type == 'number':
                if '.' in str(self.default_value):
                    return float(self.default_value)
                else:
                    return int(self.default_value)
            elif self.parameter_type == 'boolean':
                return str(self.default_value).lower() in ['true', '1', 'yes', 'on']
            elif self.parameter_type == 'json':
                import json
                return json.loads(self.default_value)
            else:  # string
                return str(self.default_value)
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.default_value

    def set_typed_value(self, value: Any) -> None:
        """
        设置类型化的值
        """
        if value is None:
            self.parameter_value = None
            return
            
        if self.parameter_type == 'json':
            import json
            self.parameter_value = json.dumps(value, ensure_ascii=False)
        else:
            self.parameter_value = str(value)

    def is_required_parameter(self) -> bool:
        """
        检查是否为必需参数
        """
        return self.is_required == 1

    def get_indicator_key(self) -> str:
        """
        获取指标唯一标识
        """
        return f"{self.indicator_name}_{self.sequence_number}"

    def get_parameter_key(self) -> str:
        """
        获取参数唯一标识
        """
        return f"{self.get_indicator_key()}_{self.parameter_name}"

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'IndicatorParameter':
        """
        从字典创建指标参数对象
        """
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

    def to_config_dict(self) -> Dict[str, Any]:
        """
        转换为配置字典格式
        """
        return {
            'name': self.parameter_name,
            'value': self.get_typed_value(),
            'type': self.parameter_type,
            'description': self.parameter_description,
            'required': self.is_required_parameter(),
            'default': self.get_typed_default_value(),
            'group': self.parameter_group,
            'order': self.sort_order
        }

    def __repr__(self) -> str:
        return (f"<IndicatorParameter(id={self.id}, "
                f"indicator='{self.indicator_name}', "
                f"sequence={self.sequence_number}, "
                f"parameter='{self.parameter_name}')>")
