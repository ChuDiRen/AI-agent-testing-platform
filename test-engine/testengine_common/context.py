"""
全局上下文管理器
用于在测试执行过程中共享数据
"""
from typing import Any, Dict, Optional


class g_context:
    """
    全局上下文类 - 使用单例模式
    
    用于存储和管理测试过程中的全局变量和配置信息。
    采用类级别属性，所有实例共享同一个数据字典。
    """
    _dic: Dict[str, Any] = {}

    def set_dict(self, key: str, value: Any) -> None:
        """
        设置上下文中的值
        
        :param key: 键名
        :param value: 值
        """
        self._dic[key] = value

    def get_dict(self, key: str) -> Optional[Any]:
        """
        获取上下文中的值
        
        :param key: 键名
        :return: 对应的值，如果不存在则返回 None
        """
        return self._dic.get(key)

    def set_by_dict(self, dic: Dict[str, Any]) -> None:
        """
        批量设置上下文值
        
        :param dic: 要更新的字典
        """
        self._dic.update(dic)

    def show_dict(self) -> Dict[str, Any]:
        """
        获取所有上下文数据
        
        :return: 上下文数据字典
        """
        return self._dic

    def clear(self) -> None:
        """
        清空上下文数据
        """
        self._dic.clear()
