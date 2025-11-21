# -*- coding: utf-8 -*-
"""代码生成器API"""
from .GeneratorController import module_route as generator_route
from .GenTableController import module_route as gen_table_route

__all__ = ['generator_route', 'gen_table_route']
