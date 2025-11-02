import ast
import json
import os
from typing import List, Dict, Any

import pandas as pd
import yaml

from ..core.globalContext import g_context  # 相对导入: webrun内部模块


# 获取以context开头 .xlsx结尾的内容，并放入到公共参数中去!
# 公共参数处理逻辑
# openpyxl是pandas用于读取.xlsx文件的引擎之一
# pip install pandas openpyxl

def load_context_from_excel(folder_path: str, excel_files: List[str] = None) -> bool:
    """
    从 Excel 文件加载上下文配置
    
    优先级：
    1. 独立的 context.xlsx 文件
    2. 测试用例 Excel 文件中的 context sheet
    
    :param folder_path: 用例目录路径
    :param excel_files: 测试用例 Excel 文件列表
    :return: 是否加载成功
    """
    try:
        # 方式1：尝试读取独立的 context.xlsx 文件
        context_file = os.path.join(folder_path, 'context.xlsx')
        if os.path.exists(context_file):
            df = pd.read_excel(context_file)
        # 方式2：从测试用例 Excel 文件中读取 context sheet
        elif excel_files:
            # 从第一个找到包含 context sheet 的 Excel 文件读取配置
            df = None
            for excel_file in excel_files:
                try:
                    file_path = os.path.join(folder_path, excel_file)
                    # 检查是否包含 context sheet
                    xl_file = pd.ExcelFile(file_path)
                    if 'context' in xl_file.sheet_names:
                        df = pd.read_excel(file_path, sheet_name='context')
                        print(f"从 {excel_file} 的 context sheet 加载配置")
                        break
                except Exception as e:
                    continue
            
            if df is None:
                print("警告: 未找到 context.xlsx 文件或包含 context sheet 的 Excel 文件")
                return False
        else:
            print("警告: 未找到 context.xlsx 文件")
            return False

        # 初始化一个空字典来存储结果
        data = {}

        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            if row['类型'] == '变量':
                # 如果Type是"变量"，则将Description作为键，Value作为值添加到result字典中
                data[row['变量描述']] = row['变量值']
        
        # 将结果字典转换为JSON字符串（如果需要的话）
        if data:
            g_context().set_by_dict(data)
        return True
    except Exception as e:
        print(f"装载excel文件错误: {str(e)}")
        return False


def load_excel_files(config_path: str) -> List[Dict[str, Any]]:
    """
    加载并解析 Excel 测试用例文件
    
    :param config_path: 用例目录路径
    :return: 解析后的用例信息列表
    """
    excel_caseInfos = []
    suite_folder = os.path.join(config_path)
    
    # 获取所有 Excel 文件（排除 context.xlsx）
    all_excel_files = [f for f in os.listdir(suite_folder) if f.endswith(".xlsx")]
    
    # 方式1：优先获取数字开头的文件（旧格式）
    numbered_files = sorted(
        [(int(f.split("_")[0]), f) for f in all_excel_files 
         if f.split("_")[0].isdigit()]
    )
    file_names = [f[-1] for f in numbered_files]
    
    # 方式2：如果没有数字开头的文件，获取所有非 context 的 xlsx 文件
    if not file_names:
        file_names = [f for f in all_excel_files if f != 'context.xlsx']
    
    # 加载上下文配置（优先从 context.xlsx，否则从测试用例 Excel 文件）
    load_context_from_excel(suite_folder, file_names)

    # 修复硬编码路径：使用相对路径获取 keywords.yaml
    keywords_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'extend', 'keywords.yaml'
    )
    with open(keywords_file_path, "r", encoding='utf-8') as rfile:
        keywords_info = yaml.full_load(rfile)

    # 解析每个 Excel 文件
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        
        # 检查文件是否包含多个 sheets
        xl_file = pd.ExcelFile(file_path)
        
        # 确定要解析的 sheet
        # 如果有 "测试用例" sheet，使用它；否则使用第一个 sheet
        if '测试用例' in xl_file.sheet_names:
            sheet_name = '测试用例'
        else:
            sheet_name = 0  # 使用第一个 sheet
        
        print(f"解析文件: {file_name}, Sheet: {sheet_name}")
        
        # 读取测试用例数据
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        data = data.where(data.notnull(), None)  # 将非空数据保留，空数据用None替换
        data = data.to_dict(orient='records')

        # 清理 NaN 值：将字符串 'nan' 转换为 None
        for row in data:
            for key, value in row.items():
                if isinstance(value, float) and pd.isna(value):
                    row[key] = None
                elif isinstance(value, str) and value.lower() == 'nan':
                    row[key] = None

        # 初始化当前正在构建的测试用例
        current_test_case = None

        # 循环解析每一行
        for row in data:
            # 检查当前行是否包含有效的测试用例标题
            if pd.notna(row.get('测试用例标题')):
                # 如果存在正在构建的测试用例，则将其添加到结果列表中
                if current_test_case is not None:
                    excel_caseInfos.append(current_test_case)
                
                # 初始化一个新的测试用例字典
                current_test_case = {
                    "desc": row['测试用例标题'],
                    "用例等级": "" if pd.isna(row.get('用例等级')) else str(row.get('用例等级')),
                    "steps": []
                }

            # 确保有当前测试用例（避免步骤在测试用例之前）
            if current_test_case is None:
                continue

            # 构建步骤
            step = {
                row['步骤描述']: {
                    "关键字": str(row['关键字']),
                }
            }
            
            # 提取参数并按编号排序
            parameter_dict = {}
            for key, value in row.items():
                if "参数_" in key:
                    # 提取参数编号
                    try:
                        param_num = int(key.split("_")[1])
                        if value is not None:
                            try:
                                # 尝试将字符串转换为Python对象
                                value = ast.literal_eval(str(value))
                            except (ValueError, SyntaxError):
                                # 如果转换失败，保持原字符串
                                pass
                        parameter_dict[param_num] = value
                    except (ValueError, IndexError):
                        pass

            # 按参数编号排序并转换为列表
            parameter = [parameter_dict[i] for i in sorted(parameter_dict.keys())]

            # 获取关键字的参数列表（处理两种格式：列表和逗号分隔字符串）
            keyword_params = keywords_info.get(row['关键字'], [])
            if isinstance(keyword_params, str):
                # 如果是字符串格式（如 "URL,PARAMS,HEADERS,DATA"），转换为列表
                keyword_params = [p.strip() for p in keyword_params.split(',')]
            
            # 使用字典推导式生成参数字典
            dict_parameter = {k: v for k, v in zip(keyword_params, parameter)}

            # 把对应的数据加到对应的步骤中
            step[row['步骤描述']].update(dict_parameter)

            # 将步骤添加到当前测试用例中
            current_test_case['steps'].append(step)

        # 不要忘记添加最后一个测试用例（如果有的话）
        if current_test_case is not None:
            excel_caseInfos.append(current_test_case)

    return excel_caseInfos


def excel_case_parser(config_path: str) -> Dict[str, List]:
    """
    Excel 用例解析器
    
    :param config_path: 用例目录路径
    :return: 解析后的用例信息 {"case_infos": [], "case_names": []}
    """
    # 获取符合条件的 Excel 文件列表
    excel_caseInfos = load_excel_files(config_path)

    # 使用列表推导式生成用例信息和名称
    case_infos = []
    case_names = []
    
    for caseinfo in excel_caseInfos:
        caseinfo["_case_name"] = caseinfo["desc"]
        case_infos.append(caseinfo)
        case_names.append(caseinfo["desc"])

    return {
        "case_infos": case_infos,
        "case_names": case_names
    }

