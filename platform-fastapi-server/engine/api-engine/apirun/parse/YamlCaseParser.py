"""
YAML 用例解析器
负责加载和解析 YAML 格式的测试用例
"""
import copy
import uuid
from pathlib import Path
from typing import Any, TypeAlias

import yaml

from ..core.globalContext import g_context

# 类型别名
CaseDict: TypeAlias = dict[str, Any]
CaseList: TypeAlias = list[CaseDict]


def load_context_from_yaml(folder_path: Path) -> bool:
    """
    从文件夹中加载 context.yaml 配置文件
    
    :param folder_path: 文件夹路径（Path对象）
    :return: 加载是否成功
    """
    try:
        yaml_file_path = folder_path / 'context.yaml'
        
        if not yaml_file_path.exists():
            print(f"context.yaml 文件不存在: {yaml_file_path}")
            return False
            
        with yaml_file_path.open('r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            print("加载context.yaml内容:", data)
            if data: 
                g_context().set_by_dict(data)
        return True
    except Exception as e:
        print(f"装载yaml文件错误: {str(e)}")
        return False


def load_yaml_files(config_path: Path) -> CaseList:
    """
    加载指定目录下的所有 YAML 测试用例文件
    
    :param config_path: 用例目录路径（Path对象）
    :return: 用例信息列表
    """
    load_context_from_yaml(config_path)
    
    # 保存用例目录路径到全局上下文，供文件上传等功能使用
    g_context().set_dict("_cases_dir", str(config_path.resolve()))
    
    # 一步完成：筛选、排序 YAML 文件
    sorted_files = sorted(
        [f for f in config_path.iterdir() 
         if f.suffix == ".yaml" and f.stem.split("_")[0].isdigit()],
        key=lambda f: int(f.stem.split("_")[0])
    )
    
    # 加载并过滤文件（确保文件句柄正确关闭）
    case_list = []
    for file_path in sorted_files:
        with file_path.open("r", encoding='utf-8') as f:
            caseinfo = yaml.full_load(f)
            if caseinfo:
                case_list.append(caseinfo)
    
    return case_list


def yaml_case_parser(config_path: Path) -> dict[str, list[Any]]:
    """
    解析 YAML 格式的测试用例
    
    :param config_path: 用例目录路径（Path对象）
    :return: 包含用例信息和用例名称的字典 {"case_infos": [...], "case_names": [...]}
    """
    case_infos: CaseList = []
    case_names: list[str] = []

    # 获取符合条件的 YAML 文件列表
    yaml_caseInfos = load_yaml_files(config_path)

    for caseinfo in yaml_caseInfos:
        # 使用海象操作符 - 读取 DDTS 节点并生成多组测试用例
        if (ddts := caseinfo.get("ddts")) and len(ddts) > 0:
            caseinfo.pop("ddts")
            # 数据驱动测试 - 生成多个用例
            for ddt in ddts:
                new_case = copy.deepcopy(caseinfo)
                # 合并上下文 - 使用 | 操作符
                new_case["context"] = new_case.get("context", {}) | ddt
                # 生成用例名称
                case_name = f'{caseinfo.get("desc", uuid.uuid4().__str__())}-{ddt.get("desc", uuid.uuid4().__str__())}'
                new_case["_case_name"] = case_name
                case_infos.append(new_case)
                case_names.append(case_name)
        else:
            # 单个用例 - 使用match解构获取desc
            match caseinfo:
                case {"desc": desc}:
                    case_name = desc
                case _:
                    case_name = uuid.uuid4().__str__()
            
            caseinfo["_case_name"] = case_name
            case_infos.append(caseinfo)
            case_names.append(case_name)

    return {"case_infos": case_infos, "case_names": case_names}
