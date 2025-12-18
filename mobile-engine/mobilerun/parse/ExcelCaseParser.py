import ast
import os
from pathlib import Path

import pandas as pd
import yaml

from ..core.globalContext import g_context


def load_context_from_excel(folder_path: str) -> bool:
    try:
        excel_file_path = os.path.join(folder_path, "context.xlsx")
        if not os.path.exists(excel_file_path):
            return False

        df = pd.read_excel(excel_file_path)
        data: dict = {}
        for _, row in df.iterrows():
            if row.get("类型") == "变量":
                data[row.get("变量描述")] = row.get("变量值")

        if data:
            g_context().set_by_dict(data)
        return True
    except Exception:
        return False


def load_excel_files(config_path: Path):
    excel_caseInfos = []

    suite_folder = str(config_path)
    load_context_from_excel(suite_folder)

    file_names = [
        (int(f.split("_")[0]), f)
        for f in os.listdir(suite_folder)
        if f.endswith(".xlsx") and f.split("_")[0].isdigit() and not f.startswith("~$")
    ]
    file_names.sort()
    file_names = [f[-1] for f in file_names]

    keywords_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extend", "keywords.yaml")
    keywords_info = {}
    if os.path.exists(keywords_file_path):
        with open(keywords_file_path, "r", encoding="utf-8") as rfile:
            keywords_info = yaml.full_load(rfile) or {}

    for file_name in file_names:
        file_path = os.path.join(suite_folder, file_name)
        try:
            data = pd.read_excel(file_path, sheet_name=0)
            data = data.where(data.notnull(), None)
            data = data.to_dict(orient="records")

            current_test_case = None

            for row in data:
                if pd.notna(row.get("测试用例标题")):
                    if current_test_case is not None:
                        excel_caseInfos.append(current_test_case)

                    current_test_case = {
                        "desc": row.get("测试用例标题"),
                        "steps": [],
                    }

                if pd.notna(row.get("步骤描述")) and pd.notna(row.get("关键字")):
                    step = {
                        row.get("步骤描述"): {
                            "关键字": str(row.get("关键字")),
                        }
                    }

                    parameters = []
                    for key, value in row.items():
                        if "参数_" in str(key) and pd.notna(value):
                            try:
                                value = ast.literal_eval(str(value))
                            except (ValueError, SyntaxError):
                                pass
                            parameters.append(value)

                    keyword = str(row.get("关键字"))
                    if keyword in keywords_info:
                        dict_parameter = {k: v for k, v in zip(keywords_info[keyword], parameters)}
                        step[row.get("步骤描述")].update(dict_parameter)
                    else:
                        for idx, param in enumerate(parameters):
                            step[row.get("步骤描述")][f"param_{idx}"] = param

                    if current_test_case is not None:
                        current_test_case["steps"].append(step)

            if current_test_case is not None:
                excel_caseInfos.append(current_test_case)
        except Exception:
            continue

    return excel_caseInfos


def excel_case_parser(config_path: Path) -> dict:
    case_infos = []
    case_names = []

    excel_caseInfos = load_excel_files(config_path)

    for caseinfo in excel_caseInfos:
        caseinfo.update({"_case_name": caseinfo["desc"]})
        case_infos.append(caseinfo)
        case_names.append(caseinfo["desc"])

    return {"case_infos": case_infos, "case_names": case_names}
