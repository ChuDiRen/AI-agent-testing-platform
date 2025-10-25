from typing import Dict, Any, Optional


class g_context:
    """
    全局上下文管理类
    
    用于存储和管理测试过程中的全局变量和配置信息。
    采用单例模式，所有实例共享同一个数据字典。
    """
    
    _dic: Dict[str, Any] = {}  # 类级别属性，所有实例共享

    def set_dict(self, key: str, value: Any) -> None:
        """
        给字典添加对应的键值对
        
        :param key: 键名
        :param value: 键值
        """
        self._dic[key] = value

    def get_dict(self, key: str) -> Optional[Any]:
        """
        获取字典中某个key的value
        
        :param key: 键名
        :return: 键值，如果不存在则返回 None
        """
        return self._dic.get(key)

    def set_by_dict(self, dic: Dict[str, Any]) -> None:
        """
        批量设置字典中的值
        
        :param dic: 要更新的字典
        """
        self._dic.update(dic)

    def show_dict(self) -> Dict[str, Any]:
        """
        显示当前字典的所有数据
        
        :return: 完整的数据字典
        """
        return self._dic



