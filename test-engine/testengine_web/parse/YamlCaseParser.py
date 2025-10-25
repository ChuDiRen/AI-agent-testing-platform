import copy
import os
import uuid
from typing import List, Dict, Any

import yaml

from ..core.globalContext import g_context  # 相对导入: webrun内部模块


def load_context_from_yaml(folder_path: str) -> bool:
    """
    从 context.yaml 加载全局配置
    
    :param folder_path: 配置文件所在文件夹路径
    :return: 加载成功返回 True，失败返回 False
    """
    try:
        yaml_file_path = os.path.join(folder_path, 'context.yaml')
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            print("加载context.yaml内容:", data)
            if data:
                g_context().set_by_dict(data)
        return True
    except Exception as e:
        print(f"装载yaml文件错误: {str(e)}")
        return False


def load_yaml_files(config_path: str) -> List[Dict[str, Any]]:
    """
    加载指定目录下的所有 YAML 测试用例文件
    
    :param config_path: 用例目录路径
    :return: YAML 用例信息列表
    """
    # 扫描文件夹下的yaml
    suite_folder = os.path.join(config_path)
    load_context_from_yaml(suite_folder)
    
    # 使用列表推导式获取并排序文件名
    file_names = sorted(
        [(int(f.split("_")[0]), f) for f in os.listdir(suite_folder) 
         if f.endswith(".yaml") and f.split("_")[0].isdigit()]
    )
    file_names = [f[-1] for f in file_names]
    
    # 加载所有YAML文件
    yaml_caseInfos = []
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        with open(file_path, "r", encoding='utf-8') as rfile:
            if caseinfo := yaml.full_load(rfile):
                yaml_caseInfos.append(caseinfo)
    
    return yaml_caseInfos


def yaml_case_parser(config_path: str) -> Dict[str, List]:
    """
    YAML 用例解析器
    
    :param config_path: 用例目录路径
    :return: 解析后的用例信息 {"case_infos": [], "case_names": []}
    """
    case_infos = []
    case_names = []
    
    # 获取符合条件的 YAML 文件列表
    yaml_caseInfos = load_yaml_files(config_path)
    
    for caseinfo in yaml_caseInfos:
        # 读取 DDTS 节点 --- 生成多组测试用例
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
                
                # 用例名称由名称及ddt数据组说明组成
                case_name = f'{caseinfo.get("desc", str(uuid.uuid4()))}-{ddt.get("desc", str(uuid.uuid4()))}'
                new_case["_case_name"] = case_name
                case_infos.append(new_case)
                case_names.append(case_name)
    
    return {
        "case_infos": case_infos,
        "case_names": case_names
    }

