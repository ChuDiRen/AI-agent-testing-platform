"""
测试用例集合工具
从 Flask 迁移到 FastAPI
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List


class CaseCollection:
    """测试用例集合工具类"""
    
    @staticmethod
    def generate_history_info(
        coll_type: str,
        case_collection_info: Dict[str, Any],
        report_data_path: str,
        execute_uuid: str
    ) -> List[Dict[str, Any]]:
        """
        生成历史记录信息
        
        Args:
            coll_type: 用例类型
            case_collection_info: 用例集合信息
            report_data_path: 报告数据路径
            execute_uuid: 执行 UUID
        
        Returns:
            List[Dict]: 历史记录列表
        """
        # 获取报告数据路径的所有文件列表
        file_list = os.listdir(report_data_path)
        history_list = []
        
        for file in file_list:
            # 确定是 result.json 文件
            if file.endswith("result.json"):
                with open(os.path.join(report_data_path, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if data:
                        # 获取第一层数据
                        name = data.get("name", "")
                        status = data.get("status", "")
                        start = data.get("start", 0)
                        stop = data.get("stop", 0)
                        
                        # 计算执行时长（毫秒）
                        duration = stop - start
                        
                        # 构建历史记录字典
                        history_record = {
                            "name": name,
                            "status": status,
                            "type": coll_type,  # 使用常量代替硬编码
                            "project_id": case_collection_info.get("project_id"),
                            "coll_id": case_collection_info.get("id"),
                            "duration": duration,
                            # 添加创建时间，为当前时间
                            "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'),
                            # 添加 detail 字段为 execute_uuid
                            "detail": execute_uuid
                        }
                        
                        history_list.append(history_record)
        
        return history_list
    
    @staticmethod
    def parse_result_file(result_file_path: str) -> Dict[str, Any]:
        """
        解析 result.json 文件
        
        Args:
            result_file_path: result.json 文件路径
        
        Returns:
            Dict: 解析后的数据
        """
        try:
            with open(result_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"解析结果文件失败: {e}")
            return {}
    
    @staticmethod
    def list_report_files(report_dir: str) -> List[str]:
        """
        列出报告目录中的所有文件
        
        Args:
            report_dir: 报告目录路径
        
        Returns:
            List[str]: 文件列表
        """
        try:
            return os.listdir(report_dir)
        except Exception as e:
            print(f"列出报告文件失败: {e}")
            return []
    
    @staticmethod
    def create_history_records(
        coll_type: str,
        case_collection_info: Dict[str, Any],
        execution_data: Dict[str, Any]
        report_dir: str
    ) -> Dict[str, Any]:
        """
        创建历史记录
        
        Args:
            coll_type: 用例类型
            case_collection_info: 用例集合信息
            execution_data: 执行数据
            report_dir: 报告目录
        
        Returns:
            Dict: 创建的历史记录
        """
        return {
            "name": case_collection_info.get("collection_name", ""),
            "status": execution_data.get("status", "completed"),
            "type": coll_type,
            "project_id": case_collection_info.get("project_id"),
            "coll_id": case_collection_info.get("id"),
            "duration": execution_data.get("duration", 0),
            "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'),
            "detail": execution_data.get("execute_uuid", "")
        }
