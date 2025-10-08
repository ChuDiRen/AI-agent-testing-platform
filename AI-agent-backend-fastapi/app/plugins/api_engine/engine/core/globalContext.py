class g_context(object): # 类继承
    _dic = {}  # 内置属性，外部不可修改


    def set_dict(self, key, value): 
        # 给字典添加对应的值
        self._dic[key] = value

    def get_dict(self, key):
        # 获取字典当中某个key的value，如果没有值则返回None
        return self._dic.get(key, None)

    def set_by_dict(self, dic):
        # 设置字典中的值，以键值对的方式更新
        self._dic.update(dic)

    def show_dict(self):
        # 显示当前字典的所有的数据
        return self._dic



