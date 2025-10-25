"""
数据模型定义
使用 dataclass 定义测试引擎中的数据结构
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseInfo:
    """测试用例信息"""
    desc: str
    steps: list[dict[str, Any]]
    context: dict[str, Any] = field(default_factory=dict)
    ddts: list[dict[str, Any]] = field(default_factory=list)
    pre_script: str | None = None
    post_script: str | None = None
    _case_name: str | None = None
    storyName: str | None = None
    featureName: str | None = None
    remark: str | None = None
    rank: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaseInfo":
        """从字典创建用例信息 - 使用字典推导式简化"""
        return cls(**{
            k: data.get(k, v)
            for k, v in {
                "desc": "",
                "steps": [],
                "context": {},
                "ddts": [],
                "pre_script": None,
                "post_script": None,
                "_case_name": None,
                "storyName": None,
                "featureName": None,
                "remark": None,
                "rank": None,
            }.items()
        })
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典 - 使用字典推导式过滤 None 和空值"""
        return {
            k: v for k, v in {
                "desc": self.desc,
                "steps": self.steps,
                "context": self.context,
                "ddts": self.ddts,
                "pre_script": self.pre_script,
                "post_script": self.post_script,
                "_case_name": self._case_name,
                "storyName": self.storyName,
                "featureName": self.featureName,
                "remark": self.remark,
                "rank": self.rank,
            }.items() if v not in (None, [], "")
        }


@dataclass
class ParseResult:
    """用例解析结果"""
    case_infos: list[dict[str, Any]]
    case_names: list[str]
    
    def __len__(self) -> int:
        return len(self.case_infos)


@dataclass
class RequestData:
    """请求数据结构"""
    url: str
    method: str
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None
    response: str = ""


__all__ = ["CaseInfo", "ParseResult", "RequestData"]

