# API测试服务模块 - 严格按照Controller命名规范
# 每个Service类名与对应Controller完全匹配

# 核心业务 Service
from .api_project_service import ApiProjectService          # ApiProjectController
from .api_dbbase_service import ApiDbBaseService            # ApiDbBaseController  
from .api_collection_detail_service import ApiCollectionDetailService  # ApiCollectionDetailController
from .api_collection_info_service import ApiCollectionInfoService    # ApiCollectionInfoController
from .api_environment_service import ApiEnvironmentService          # ApiEnvironmentController
from .api_folder_service import ApiFolderService                    # ApiFolderController
from .api_info_service import InfoService                           # ApiInfoController
from .api_info_case_service import InfoCaseService                  # ApiInfoCaseController
from .api_history_service import HistoryService                     # ApiHistoryController

# 关键字和文档 Service
from .api_keyword_service import KeyWordService                     # ApiKeyWordController
from .api_doc_service import DocService                             # ApiDocController
from .api_mock_service import ApiMockService                        # ApiMockController

# 任务和执行 Service
from .test_task_service import TestTaskService                      # TestTaskController
from .execution_service import ExecutionService
from .result_collector import ResultCollector
from .case_yaml_builder import CaseYamlBuilder

# 统计和报告 Service
from .api_statistics_service import StatisticsService               # ApiStatisticsController
from .api_request_history_service import RequestHistoryService      # ApiRequestHistoryController
from .api_report_viewer_service import ReportViewerService          # ApiReportViewerController

# 元数据和配置 Service
from .api_info_case_step_service import InfoCaseStepService         # ApiInfoCaseStepController
from .api_meta_service import MetaService                           # ApiMetaController
from .api_operation_type_service import OperationTypeService        # ApiOperationTypeController

__all__ = [
    # 核心业务
    "ApiProjectService",
    "ApiDbBaseService",
    "ApiCollectionDetailService",
    "ApiCollectionInfoService",
    "ApiEnvironmentService",
    "ApiFolderService",
    "InfoService",
    "InfoCaseService",
    "HistoryService",
    # 关键字和文档
    "KeyWordService",
    "DocService",
    "ApiMockService",
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
