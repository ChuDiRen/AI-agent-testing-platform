import copy
import uuid
from pathlib import Path
from typing import Any, TypeAlias

import yaml

from ..core.globalContext import g_context

CaseDict: TypeAlias = dict[str, Any]
CaseList: TypeAlias = list[CaseDict]


def load_context_from_yaml(folder_path: Path) -> bool:
    try:
        yaml_file_path = folder_path / "context.yaml"
        if not yaml_file_path.exists():
            return False
        with yaml_file_path.open("r", encoding="utf-8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            if data:
                g_context().set_by_dict(data)
        return True
    except Exception:
        return False


def load_yaml_files(config_path: Path) -> CaseList:
    load_context_from_yaml(config_path)

    sorted_files = sorted(
        [f for f in config_path.iterdir() if f.suffix == ".yaml" and f.stem.split("_")[0].isdigit()],
        key=lambda f: int(f.stem.split("_")[0]),
    )

    case_list: CaseList = []
    for file_path in sorted_files:
        with file_path.open("r", encoding="utf-8") as f:
            caseinfo = yaml.full_load(f)
            if caseinfo:
                case_list.append(caseinfo)

    return case_list


def yaml_case_parser(config_path: Path) -> dict[str, list[Any]]:
    case_infos: CaseList = []
    case_names: list[str] = []

    yaml_caseInfos = load_yaml_files(config_path)

    for caseinfo in yaml_caseInfos:
        if (ddts := caseinfo.get("ddts")) and len(ddts) > 0:
            caseinfo.pop("ddts")
            for ddt in ddts:
                new_case = copy.deepcopy(caseinfo)
                new_case["context"] = new_case.get("context", {}) | ddt
                case_name = f"{caseinfo.get('desc', uuid.uuid4().__str__())}-{ddt.get('desc', uuid.uuid4().__str__())}"
                new_case["_case_name"] = case_name
                case_infos.append(new_case)
                case_names.append(case_name)
        else:
            match caseinfo:
                case {"desc": desc}:
                    case_name = desc
                case _:
                    case_name = uuid.uuid4().__str__()

            caseinfo["_case_name"] = case_name
            case_infos.append(caseinfo)
            case_names.append(case_name)

    return {"case_infos": case_infos, "case_names": case_names}
