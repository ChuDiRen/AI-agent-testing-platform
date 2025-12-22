"""
YAML 用例解析器
提供 YAML 测试用例文件的加载和解析功能
"""
import copy
import os
import uuid
from typing import Any, Callable, Dict, List

import yaml

try:
    # pyyaml-include 2.x
    from yaml_include import Constructor as YamlIncludeConstructor
except ImportError:
    try:
        # pyyaml-include 1.x
        from yamlinclude import YamlIncludeConstructor
    except ImportError:
        YamlIncludeConstructor = None


def load_context_from_yaml(folder_path: str, context_setter: Callable[[Dict], None] = None) -> bool:
    """
    从 context.yaml 加载全局配置
    
    :param folder_path: 配置文件所在文件夹路径
    :param context_setter: 上下文设置函数（接收字典参数）
    :return: 加载成功返回 True，失败返回 False
    """
    try:
        yaml_file_path = os.path.join(folder_path, 'context.yaml')
        if not os.path.exists(yaml_file_path):
            return False
            
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            print(f"加载 context.yaml 内容: {data}")
            if data and context_setter:
                context_setter(data)
        return True
    except Exception as e:
        print(f"装载 yaml 文件错误: {str(e)}")
        return False


def load_yaml_files(config_path: str, context_setter: Callable[[Dict], None] = None) -> List[Dict[str, Any]]:
    """
    加载指定目录下的所有 YAML 测试用例文件
    
    :param config_path: 用例目录路径
    :param context_setter: 上下文设置函数
    :return: YAML 用例信息列表
    """
    suite_folder = os.path.join(config_path)
    load_context_from_yaml(suite_folder, context_setter)
    
    # 获取并排序以数字开头的 yaml 文件
    file_names = sorted(
        [(int(f.split("_")[0]), f) for f in os.listdir(suite_folder) 
         if f.endswith(".yaml") and f.split("_")[0].isdigit()]
    )
    file_names = [f[-1] for f in file_names]
    
    # 加载所有 YAML 文件
    yaml_case_infos = []
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        with open(file_path, "r", encoding='utf-8') as rfile:
            if caseinfo := yaml.full_load(rfile):
                yaml_case_infos.append(caseinfo)
    
    return yaml_case_infos


def yaml_case_parser(config_path: str, context_setter: Callable[[Dict], None] = None) -> Dict[str, List]:
    """
    YAML 用例解析器
    
    :param config_path: 用例目录路径
    :param context_setter: 上下文设置函数
    :return: 解析后的用例信息 {"case_infos": [], "case_names": []}
    """
    case_infos = []
    case_names = []
    
    yaml_case_infos = load_yaml_files(config_path, context_setter)
    
    for caseinfo in yaml_case_infos:
        # 读取 DDTS 节点 - 数据驱动测试
        ddts = caseinfo.get("ddts", [])
        if ddts:
            caseinfo.pop("ddts")
        
        if not ddts:
            # 单个用例
            case_name = caseinfo.get("desc", str(uuid.uuid4()))
            caseinfo["_case_name"] = case_name
            case_infos.append(caseinfo)
            case_names.append(case_name)
        else:
            # 数据驱动：循环生成多个用例执行对象
            for ddt in ddts:
                new_case = copy.deepcopy(caseinfo)
                # 将数据读取后更新到 context 里面
                context = new_case.get("context", {})
                ddt.update(context)
                new_case["context"] = ddt
                
                # 用例名称由名称及 ddt 数据组说明组成
                case_name = f'{caseinfo.get("desc", str(uuid.uuid4()))}-{ddt.get("desc", str(uuid.uuid4()))}'
                new_case["_case_name"] = case_name
                case_infos.append(new_case)
                case_names.append(case_name)
    
    return {
        "case_infos": case_infos,
        "case_names": case_names
    }
