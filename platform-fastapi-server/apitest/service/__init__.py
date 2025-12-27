# API测试服务模块 - 严格按照Controller命名规范
# 每个Service类名与对应Controller完全匹配

# 核心业务 Service
from .ApiProjectService import ApiProjectService          # ApiProjectController
from .ApiDbbaseService import ApiDbbaseService            # ApiDbbaseController  
from .ApiCollectionDetailService import ApiCollectionDetailService  # ApiCollectionDetailController
from .ApiCollectionInfoService import ApiCollectionInfoService    # ApiCollectionInfoController
from .ApiFolderService import ApiFolderService                    # ApiFolderController
from .ApiInfoService import InfoService                           # ApiInfoController
from .ApiInfoCaseService import InfoCaseService                  # ApiInfoCaseController
from .ApiHistoryService import HistoryService                     # ApiHistoryController

# 关键字 Service
from .ApiKeywordService import ApiKeywordService                     # ApiKeywordController

# 任务和执行 Service
from .TestTaskService import TestTaskService                      # TestTaskController
from .execution_service import ExecutionService
from .result_collector import ResultCollector
from .case_yaml_builder import CaseYamlBuilder

# 统计和报告 Service
from .ApiStatisticsService import StatisticsService               # ApiStatisticsController
from .ApiRequestHistoryService import RequestHistoryService      # ApiRequestHistoryController
from .ApiReportViewerService import ReportViewerService          # ApiReportViewerController

# 元数据和配置 Service
from .ApiInfoCaseStepService import InfoCaseStepService         # ApiInfoCaseStepController
from .ApiMetaService import MetaService                           # ApiMetaController
from .ApiOperationTypeService import OperationTypeService        # ApiOperationTypeController

__all__ = [
    # 核心业务
    "ApiProjectService",
    "ApiDbbaseService",
    "ApiCollectionDetailService",
    "ApiCollectionInfoService",
    "ApiFolderService",
    "InfoService",
    "InfoCaseService",
    "HistoryService",
    # 关键字
    "ApiKeywordService",
    # 任务和执行
    "TestTaskService",
    "ExecutionService",
    "ResultCollector",
    "CaseYamlBuilder",
    # 统计和报告
    "StatisticsService",
    "RequestHistoryService",
    "ReportViewerService",
    # 元数据和配置
    "InfoCaseStepService",
    "MetaService",
    "OperationTypeService",
]
