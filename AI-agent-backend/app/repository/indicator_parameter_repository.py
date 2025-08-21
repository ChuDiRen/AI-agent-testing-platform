"""
指标参数Repository
处理指标参数相关的数据库操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.entity.indicator_parameter import IndicatorParameter
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class IndicatorParameterRepository(BaseRepository[IndicatorParameter]):
    """
    指标参数Repository类
    提供指标参数特定的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化指标参数Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(IndicatorParameter, db)

    def get_by_indicator(self, indicator_name: str, sequence_number: int) -> List[IndicatorParameter]:
        """
        根据指标名称和序列号获取所有参数
        
        Args:
            indicator_name: 指标名称
            sequence_number: 序列号
            
        Returns:
            指标参数列表
        """
        try:
            parameters = self.db.query(IndicatorParameter).filter(
                and_(
                    IndicatorParameter.indicator_name == indicator_name,
                    IndicatorParameter.sequence_number == sequence_number,
                    IndicatorParameter.is_deleted == 0
                )
            ).order_by(IndicatorParameter.sort_order, IndicatorParameter.parameter_name).all()
            
            logger.debug(f"Found {len(parameters)} parameters for indicator {indicator_name}_{sequence_number}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting parameters for indicator {indicator_name}_{sequence_number}: {str(e)}")
            raise

    def get_by_parameter_name(self, indicator_name: str, sequence_number: int, 
                             parameter_name: str) -> Optional[IndicatorParameter]:
        """
        根据指标和参数名获取特定参数
        
        Args:
            indicator_name: 指标名称
            sequence_number: 序列号
            parameter_name: 参数名称
            
        Returns:
            指标参数对象或None
        """
        try:
            parameter = self.db.query(IndicatorParameter).filter(
                and_(
                    IndicatorParameter.indicator_name == indicator_name,
                    IndicatorParameter.sequence_number == sequence_number,
                    IndicatorParameter.parameter_name == parameter_name,
                    IndicatorParameter.is_deleted == 0
                )
            ).first()
            
            if parameter:
                logger.debug(f"Found parameter {parameter_name} for indicator {indicator_name}_{sequence_number}")
            else:
                logger.debug(f"No parameter {parameter_name} found for indicator {indicator_name}_{sequence_number}")
                
            return parameter
            
        except Exception as e:
            logger.error(f"Error getting parameter {parameter_name} for indicator {indicator_name}_{sequence_number}: {str(e)}")
            raise

    def get_by_group(self, parameter_group: str) -> List[IndicatorParameter]:
        """
        根据参数分组获取参数列表
        
        Args:
            parameter_group: 参数分组
            
        Returns:
            指标参数列表
        """
        try:
            parameters = self.db.query(IndicatorParameter).filter(
                and_(
                    IndicatorParameter.parameter_group == parameter_group,
                    IndicatorParameter.is_deleted == 0
                )
            ).order_by(IndicatorParameter.sort_order, IndicatorParameter.parameter_name).all()
            
            logger.debug(f"Found {len(parameters)} parameters in group {parameter_group}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting parameters by group {parameter_group}: {str(e)}")
            raise

    def get_required_parameters(self, indicator_name: str, sequence_number: int) -> List[IndicatorParameter]:
        """
        获取指标的必需参数
        
        Args:
            indicator_name: 指标名称
            sequence_number: 序列号
            
        Returns:
            必需参数列表
        """
        try:
            parameters = self.db.query(IndicatorParameter).filter(
                and_(
                    IndicatorParameter.indicator_name == indicator_name,
                    IndicatorParameter.sequence_number == sequence_number,
                    IndicatorParameter.is_required == 1,
                    IndicatorParameter.is_deleted == 0
                )
            ).order_by(IndicatorParameter.sort_order, IndicatorParameter.parameter_name).all()
            
            logger.debug(f"Found {len(parameters)} required parameters for indicator {indicator_name}_{sequence_number}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting required parameters for indicator {indicator_name}_{sequence_number}: {str(e)}")
            raise

    def get_parameters_by_type(self, parameter_type: str) -> List[IndicatorParameter]:
        """
        根据参数类型获取参数列表
        
        Args:
            parameter_type: 参数类型
            
        Returns:
            指标参数列表
        """
        try:
            parameters = self.db.query(IndicatorParameter).filter(
                and_(
                    IndicatorParameter.parameter_type == parameter_type,
                    IndicatorParameter.is_deleted == 0
                )
            ).order_by(IndicatorParameter.indicator_name, IndicatorParameter.sequence_number, 
                      IndicatorParameter.sort_order).all()
            
            logger.debug(f"Found {len(parameters)} parameters of type {parameter_type}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting parameters by type {parameter_type}: {str(e)}")
            raise

    def delete_by_indicator(self, indicator_name: str, sequence_number: int, 
                           soft_delete: bool = True) -> int:
        """
        删除指标的所有参数
        
        Args:
            indicator_name: 指标名称
            sequence_number: 序列号
            soft_delete: 是否软删除
            
        Returns:
            删除的参数数量
        """
        try:
            parameters = self.get_by_indicator(indicator_name, sequence_number)
            deleted_count = 0
            
            for parameter in parameters:
                if self.delete(parameter.id, soft_delete):
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} parameters for indicator {indicator_name}_{sequence_number}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting parameters for indicator {indicator_name}_{sequence_number}: {str(e)}")
            raise

    def batch_save_parameters(self, indicator_name: str, sequence_number: int, 
                             parameters_data: List[Dict[str, Any]]) -> List[IndicatorParameter]:
        """
        批量保存指标参数
        
        Args:
            indicator_name: 指标名称
            sequence_number: 序列号
            parameters_data: 参数数据列表
            
        Returns:
            保存后的参数列表
        """
        try:
            # 先删除现有参数
            self.delete_by_indicator(indicator_name, sequence_number, soft_delete=True)
            
            # 创建新参数
            new_parameters = []
            for param_data in parameters_data:
                param_data['indicator_name'] = indicator_name
                param_data['sequence_number'] = sequence_number
                
                parameter = IndicatorParameter.create_from_dict(param_data)
                new_parameters.append(parameter)
            
            # 批量保存
            saved_parameters = self.batch_create(new_parameters)
            
            logger.info(f"Batch saved {len(saved_parameters)} parameters for indicator {indicator_name}_{sequence_number}")
            return saved_parameters
            
        except Exception as e:
            logger.error(f"Error batch saving parameters for indicator {indicator_name}_{sequence_number}: {str(e)}")
            raise

    def get_indicator_config(self, indicator_name: str, sequence_number: int) -> Dict[str, Any]:
        """
        获取指标的完整配置
        
        Args:
            indicator_name: 指标名称
            sequence_number: 序列号
            
        Returns:
            指标配置字典
        """
        try:
            parameters = self.get_by_indicator(indicator_name, sequence_number)
            
            config = {
                'indicator_name': indicator_name,
                'sequence_number': sequence_number,
                'parameters': {},
                'groups': {},
                'required_parameters': [],
                'parameter_count': len(parameters)
            }
            
            for param in parameters:
                # 添加到参数字典
                config['parameters'][param.parameter_name] = param.to_config_dict()
                
                # 按组分类
                group = param.parameter_group or 'default'
                if group not in config['groups']:
                    config['groups'][group] = []
                config['groups'][group].append(param.parameter_name)
                
                # 记录必需参数
                if param.is_required_parameter():
                    config['required_parameters'].append(param.parameter_name)
            
            logger.debug(f"Generated config for indicator {indicator_name}_{sequence_number}")
            return config
            
        except Exception as e:
            logger.error(f"Error getting config for indicator {indicator_name}_{sequence_number}: {str(e)}")
            raise

    def search_parameters(self, keyword: str, skip: int = 0, limit: int = 100) -> List[IndicatorParameter]:
        """
        搜索参数
        
        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            匹配的参数列表
        """
        try:
            keyword = f"%{keyword}%"
            parameters = self.db.query(IndicatorParameter).filter(
                and_(
                    or_(
                        IndicatorParameter.indicator_name.like(keyword),
                        IndicatorParameter.parameter_name.like(keyword),
                        IndicatorParameter.parameter_description.like(keyword),
                        IndicatorParameter.parameter_group.like(keyword)
                    ),
                    IndicatorParameter.is_deleted == 0
                )
            ).order_by(IndicatorParameter.indicator_name, IndicatorParameter.sequence_number, 
                      IndicatorParameter.sort_order).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(parameters)} parameters matching keyword: {keyword}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error searching parameters with keyword {keyword}: {str(e)}")
            raise

    def get_all_indicators(self) -> List[Dict[str, Any]]:
        """
        获取所有指标的基本信息
        
        Returns:
            指标信息列表
        """
        try:
            # 查询所有不重复的指标名称和序列号
            indicators = self.db.query(
                IndicatorParameter.indicator_name,
                IndicatorParameter.sequence_number
            ).filter(
                IndicatorParameter.is_deleted == 0
            ).distinct().all()
            
            result = []
            for indicator_name, sequence_number in indicators:
                # 获取每个指标的参数数量
                param_count = self.db.query(IndicatorParameter).filter(
                    and_(
                        IndicatorParameter.indicator_name == indicator_name,
                        IndicatorParameter.sequence_number == sequence_number,
                        IndicatorParameter.is_deleted == 0
                    )
                ).count()
                
                result.append({
                    'indicator_name': indicator_name,
                    'sequence_number': sequence_number,
                    'parameter_count': param_count,
                    'indicator_key': f"{indicator_name}_{sequence_number}"
                })
            
            logger.debug(f"Found {len(result)} indicators")
            return result
            
        except Exception as e:
            logger.error(f"Error getting all indicators: {str(e)}")
            raise
