"""
数据模型定义
使用 dataclass 定义测试引擎中的数据结构
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrowserConfig:
    """浏览器配置"""
    browser_type: str = "chrome"
    headless: bool = False
    implicit_wait: int = 10
    window_size: str = "maximize"
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BrowserConfig":
        """从字典创建配置 - 使用字典推导式简化"""
        defaults = {
            "browser_type": "chrome",
            "headless": False,
            "implicit_wait": 10,
            "window_size": "maximize"
        }
        return cls(**{k: data.get(k, v) for k, v in defaults.items()})


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


__all__ = ["BrowserConfig", "CaseInfo", "ParseResult"]

