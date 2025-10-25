import copy
import os
import yaml
import json
import ast
from typing import List, Dict, Any
import pandas as pd
from ..core.globalContext import g_context  # 相对导入: apirun内部模块


# 获取以context开头 .xlsx结尾的内容，并放入到公共参数中去!
# 公共参数处理逻辑
# openpyxl是pandas用于读取.xlsx文件的引擎之一
# pip install pandas openpyxl

def load_context_from_excel(folder_path: str) -> bool:
    try:
        excel_file_path = os.path.join(folder_path, 'context.xlsx')

        # 读取Excel文件
        df = pd.read_excel(excel_file_path)

        # 初始化一个空字典来存储结果
        data = {
            "_database": {}
        }

        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            if row['类型'] == '变量':
                # 如果Type是"变量"，则将Description作为键，Value作为值添加到result字典中
                data[row['变量描述']] = row['变量值']
            elif '数据库' in row['类型']:
                # 如果Type包含"数据库"，则解析Value列中的JSON字符串
                db_name = row['变量描述']  # 提取数据库名
                db_config = json.loads(row['变量值'])  # 将JSON字符串转换为字典
                # 将数据库配置添加到result字典的_database键下
                data['_database'][db_name] = db_config
        
        # 将结果字典转换为JSON字符串（如果需要的话）
        if data:
            g_context().set_by_dict(data)
        return True
    except Exception as e:
        print(f"装载excel文件错误: {str(e)}")
        return False


def load_excel_files(config_path: str) -> List[Dict[str, Any]]:
    excel_caseInfos = []
    # 扫描 文件夹下的excel
    suite_folder = os.path.join(config_path)
    load_context_from_excel(suite_folder)
    
    # 使用列表推导式获取并排序文件名
    file_names = sorted(
        [(int(f.split("_")[0]), f) for f in os.listdir(suite_folder) 
         if f.endswith(".xlsx") and f.split("_")[0].isdigit()]
    )
    file_names = [f[-1] for f in file_names]

    # 修复硬编码路径：使用相对路径获取 keywords.yaml
    keywords_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'extend', 'keywords.yaml'
    )
    with open(keywords_file_path, "r", encoding='utf-8') as rfile:
        keywords_info = yaml.full_load(rfile)

    # 获取 suite 文件夹下的所有 Excel 文件，并按文件名排序
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        #  以字典的格式读出
        data = pd.read_excel(file_path, sheet_name=0)
        data = data.where(data.notnull(), None)  # 将非空数据保留，空数据用None替换
        data = data.to_dict(orient='records')

        # 初始化一个空列表来存储转换后的数据
        result = []
        # 初始化一个空字典来存储当前正在构建的测试用例
        current_test_case = None

        # 循环结束代表一个Excel用例结束
        for row in data:
            # 检查当前行是否包含有效的测试用例标题
            if pd.notna(row['测试用例标题']):
                # 如果存在正在构建的测试用例，则将其添加到结果列表中
                if current_test_case is not None:
                    excel_caseInfos.append(current_test_case)
                    # 初始化一个新的测试用例字典
                current_test_case = {
                    # "编号": int(row['编号']),
                    "desc": row['测试用例标题'],
                    "用例等级": "" if pd.isna(row['用例等级']) else str(row['用例等级']),
                    "steps": []
                }
                # 总是添加步骤（假设步骤编号是连续的，并且不跳过）

            step = {
                row['步骤描述']: {
                    "关键字": str(row['关键字']),
                }

            }
            
            # 使用列表推导式提取参数
            parameter = []
            for key, value in row.items():
                if "参数_" in key and value is not None:
                    try:
                        # 尝试将字符串转换为Python对象
                        value = ast.literal_eval(str(value))
                    except (ValueError, SyntaxError):
                        # 如果转换失败，保持原字符串
                        pass
                    parameter.append(value)

            # 使用字典推导式生成参数字典
            dict_parameter = {k: v for k, v in zip(keywords_info.get(row['关键字'], []), parameter)}

            # 把对应的数据加到对应的步骤中
            step[row['步骤描述']].update(dict_parameter)

            # 将步骤添加到当前测试用例中
            current_test_case['steps'].append(step)

            # 不要忘记添加最后一个测试用例（如果有的话）
        if current_test_case is not None:
            excel_caseInfos.append(current_test_case)

        # 把当前的excel的数据加到所有的数据当中去
        # excel_caseInfos.append(result)
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
