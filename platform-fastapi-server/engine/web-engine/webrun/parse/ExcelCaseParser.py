"""
Excel 格式测试用例解析器
支持从 Excel 文件中读取 Web 自动化测试用例
"""
import ast
import json
import os
from pathlib import Path

import pandas as pd
import yaml

from ..core.globalContext import g_context


def load_context_from_excel(folder_path):
    """
    从 context.xlsx 文件中加载全局配置
    
    :param folder_path: Excel 文件所在文件夹路径
    :return: 是否成功加载
    """
    try:
        excel_file_path = os.path.join(folder_path, 'context.xlsx')
        
        if not os.path.exists(excel_file_path):
            print(f"context.xlsx 文件不存在: {excel_file_path}")
            return False

        # 读取Excel文件
        df = pd.read_excel(excel_file_path)

        # 初始化一个空字典来存储结果
        data = {}

        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            if row['类型'] == '变量':
                # 如果Type是"变量"，则将Description作为键，Value作为值添加到result字典中
                data[row['变量描述']] = row['变量值']
            elif '数据库' in str(row['类型']):
                # 如果Type包含"数据库"，则解析Value列中的JSON字符串
                if '_database' not in data:
                    data['_database'] = {}
                db_name = row['变量描述']  # 提取数据库名
                try:
                    db_config = json.loads(row['变量值'])  # 将JSON字符串转换为字典
                    data['_database'][db_name] = db_config
                except json.JSONDecodeError as e:
                    print(f"数据库配置解析失败 {db_name}: {e}")
        
        # 将结果字典存储到全局上下文中
        if data:
            g_context().set_by_dict(data)
            print(f"已加载 context.xlsx: {list(data.keys())}")
        
        return True
    except Exception as e:
        print(f"装载 excel 文件错误: {str(e)}")
        return False


def load_excel_files(config_path):
    """
    加载指定文件夹下的所有 Excel 测试用例文件
    
    :param config_path: 测试用例文件夹路径
    :return: 测试用例信息列表
    """
    excel_caseInfos = []
    
    # 扫描文件夹下的 excel 文件
    suite_folder = str(config_path)
    
    # 加载 context.xlsx 配置文件
    load_context_from_excel(suite_folder)
    
    # 获取所有以数字开头的 .xlsx 文件（排除 context.xlsx）
    file_names = [
        (int(f.split("_")[0]), f) 
        for f in os.listdir(suite_folder) 
        if f.endswith(".xlsx") 
        and f.split("_")[0].isdigit()
        and not f.startswith("~$")  # 排除临时文件
    ]
    file_names.sort()
    file_names = [f[-1] for f in file_names]

    if not file_names:
        print(f"警告: 未找到任何 Excel 测试用例文件（格式: 数字_用例名.xlsx）")
        return excel_caseInfos

    # 加载 keywords.yaml 获取关键字参数描述
    keywords_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'extend', 
        'keywords.yaml'
    )
    
    keywords_info = {}
    if os.path.exists(keywords_file_path):
        with open(keywords_file_path, "r", encoding='utf-8') as rfile:
            keywords_info = yaml.full_load(rfile)
    else:
        print(f"警告: keywords.yaml 文件不存在: {keywords_file_path}")

    # 遍历所有 Excel 文件
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        print(f"正在解析 Excel 用例: {file_name}")
        
        try:
            # 读取 Excel 文件为字典格式
            data = pd.read_excel(file_path, sheet_name=0)
            data = data.where(data.notnull(), None)  # 将空数据用 None 替换
            data = data.to_dict(orient='records')

            # 初始化当前测试用例
            current_test_case = None

            # 遍历每一行数据
            for row in data:
                # 检查当前行是否包含有效的测试用例标题
                if pd.notna(row.get('测试用例标题')):
                    # 如果存在正在构建的测试用例，则将其添加到结果列表中
                    if current_test_case is not None:
                        excel_caseInfos.append(current_test_case)
                    
                    # 初始化一个新的测试用例字典
                    current_test_case = {
                        "desc": row['测试用例标题'],
                        "用例等级": "" if pd.isna(row.get('用例等级')) else str(row['用例等级']),
                        "steps": []
                    }

                # 构建步骤
                if pd.notna(row.get('步骤描述')) and pd.notna(row.get('关键字')):
                    step = {
                        row['步骤描述']: {
                            "关键字": str(row['关键字']),
                        }
                    }

                    # 收集所有参数列（以 "参数_" 开头的列）
                    parameters = []
                    for key, value in row.items():
                        if "参数_" in str(key) and pd.notna(value):
                            try:
                                # 尝试将字符串转换为 Python 对象
                                value = ast.literal_eval(str(value))
                            except (ValueError, SyntaxError):
                                # 如果转换失败，保持原字符串
                                pass
                            parameters.append(value)

                    # 将参数转换为字典格式
                    keyword = str(row['关键字'])
                    if keyword in keywords_info:
                        dict_parameter = {
                            k: v 
                            for k, v in zip(keywords_info[keyword], parameters)
                        }
                        step[row['步骤描述']].update(dict_parameter)
                    else:
                        # 如果关键字不在 keywords.yaml 中，使用参数索引
                        for idx, param in enumerate(parameters):
                            step[row['步骤描述']][f"param_{idx}"] = param

                    # 将步骤添加到当前测试用例中
                    if current_test_case is not None:
                        current_test_case['steps'].append(step)

            # 添加最后一个测试用例
            if current_test_case is not None:
                excel_caseInfos.append(current_test_case)

        except Exception as e:
            print(f"解析 Excel 文件失败 {file_name}: {str(e)}")
            continue

    print(f"成功加载 {len(excel_caseInfos)} 个 Excel 测试用例")
    return excel_caseInfos


def excel_case_parser(config_path: Path) -> dict:
    """
    Excel 测试用例解析器入口函数
    
    :param config_path: 测试用例文件夹路径（Path对象）
    :return: 包含用例信息的字典 {"case_infos": [...], "case_names": [...]}
    """
    case_infos = []
    case_names = []

    # 获取符合条件的 Excel 文件列表
    excel_caseInfos = load_excel_files(config_path)

    for caseinfo in excel_caseInfos:
        caseinfo.update({"_case_name": caseinfo["desc"]})
        case_infos.append(caseinfo)  # 用例信息
        case_names.append(caseinfo["desc"])  # 用例名称

    return {
        "case_infos": case_infos,
        "case_names": case_names
    }

