import copy, os, yaml
from apirun.core.globalContext import g_context
import pandas as pd
import json
import ast


# 获取以context开头 .xlsx结尾的内容，并放入到公共参数中去!
# 公共参数处理逻辑
# openpyxl是pandas用于读取.xlsx文件的引擎之一
# pip install pandas openpyxl

def load_context_from_excel(folder_path):
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
                # 如果Type是“变量”，则将Description作为键，Value作为值添加到result字典中
                data[row['变量描述']] = row['变量值']
            elif '数据库' in row['类型']:
                # 如果Type包含“数据库”，则解析Value列中的JSON字符串
                db_name = row['变量描述']  # 提取数据库名
                db_config = json.loads(row['变量值'])  # 将JSON字符串转换为字典
                #     # 将数据库配置添加到result字典的_database键下
                data['_database'][db_name] = db_config
            # 将结果字典转换为JSON字符串（如果需要的话）
        if data: g_context().set_by_dict(data)
    except Exception as e:
        print(f"装载excel文件错误: {str(e)}")
        return False


def load_excel_files(config_path):
    excel_caseInfos = []
    # 扫描 文件夹下的excel
    suite_folder = os.path.join(config_path)
    load_context_from_excel(suite_folder)
    file_names = [(int(f.split("_")[0]), f) for f in os.listdir(suite_folder) if
                  f.endswith(".xlsx") and f.split("_")[0].isdigit()]
    file_names.sort()
    file_names = [f[-1] for f in file_names]

    # 因为需要excel的参数一一对应起来关键字，所以需要结合：keywords.yaml中的参数描述变成字典格式。
    keywords_file_path = r"F:\ProjectHcEdu\api-engine\apirun\extend\keywords.yaml"
    keywords_info = {}
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
            # 遍历得到所有的参数，并且结合关键字描述变成字典加到对应的步骤中
            parameter = []
            for key, value in row.items():
                if "参数_" in key:
                    try:
                        # 尝试将字符串转换为Python对象
                        value = ast.literal_eval(value)
                    except:
                        print("当前即是一个普通的字符串格式")
                    parameter.append(value)

            # 变成字典格式
            dict_parameter = {k: v for k, v in zip(keywords_info[row['关键字']], parameter)}

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


def excel_case_parser(config_path):
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
