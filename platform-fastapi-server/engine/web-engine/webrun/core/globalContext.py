"""
全局上下文管理器
用于在测试用例执行过程中共享数据
"""
from typing import Any


class g_context:
    """全局上下文类 - 使用单例模式"""
    _dic: dict[str, Any] = {}  # 内置属性，外部不可修改

    def set_dict(self, key: str, value: Any) -> None:
        """
        设置上下文中的值
        
        :param key: 键名
        :param value: 值
        """
        self._dic[key] = value

    def get_dict(self, key: str) -> Any | None:
        """
        获取上下文中的值
        
        :param key: 键名
        :return: 对应的值，如果不存在则返回 None
        """
        return self._dic.get(key, None)

    def set_by_dict(self, dic: dict[str, Any]) -> None:
        """
        批量设置上下文值
        
        :param dic: 要更新的字典
        """
        self._dic.update(dic)

    def show_dict(self) -> dict[str, Any]:
        """
        获取所有上下文数据
        
        :return: 上下文数据字典
        """
        return self._dic

