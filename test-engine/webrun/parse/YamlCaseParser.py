import copy
import os
import yaml
import uuid
from webrun.core.globalContext import g_context


def load_context_from_yaml(folder_path):
    """
    从 context.yaml 加载全局配置
    """
    try:
        yaml_file_path = os.path.join(folder_path, 'context.yaml')
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            print("加载context.yaml内容:", data)
            if data:
                g_context().set_by_dict(data)
    except Exception as e:
        print(f"装载yaml文件错误: {str(e)}")
        return False


def load_yaml_files(config_path):
    """
    加载指定目录下的所有 YAML 测试用例文件
    """
    yaml_caseInfos = []
    # 扫描文件夹下的yaml
    suite_folder = os.path.join(config_path)
    load_context_from_yaml(suite_folder)
    file_names = [(int(f.split("_")[0]), f) for f in os.listdir(suite_folder) if
                  f.endswith(".yaml") and f.split("_")[0].isdigit()]
    file_names.sort()
    file_names = [f[-1] for f in file_names]
    # 获取 suite 文件夹下的所有 YAML 文件，并按文件名排序
    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        with open(file_path, "r", encoding='utf-8') as rfile:
            caseinfo = yaml.full_load(rfile)
            yaml_caseInfos.append(caseinfo)
    
    return yaml_caseInfos


def yaml_case_parser(config_path):
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
        if len(ddts) > 0:
            caseinfo.pop("ddts")
        
        if len(ddts) == 0:
            case_name = caseinfo.get("desc", uuid.uuid4().__str__())  # 用例名称
            caseinfo.update({"_case_name": case_name})  # 把生成的用例名称保存到用例对象中
            case_infos.append(caseinfo)  # 用例信息
            case_names.append(case_name)
        else:
            # 循环生成多个用例执行对象，保存起来。
            for ddt in ddts:
                new_case = copy.deepcopy(caseinfo)
                # 将数据读取后更新到 context 里面
                context = new_case.get("context", {})
                ddt.update(context)
                new_case.update({"context": ddt})
                case_name = f'{caseinfo.get("desc", uuid.uuid4().__str__())}-{ddt.get("desc", uuid.uuid4().__str__())}'  # 用例名称
                new_case.update({"_case_name": case_name})  # 把生成的用例名称保存到用例对象中
                case_infos.append(new_case)
                # 用例名称由 名称及ddt数据组说明组成
                case_names.append(case_name)
    
    return {
        "case_infos": case_infos,
        "case_names": case_names
    }

