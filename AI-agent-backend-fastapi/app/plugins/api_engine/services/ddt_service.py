# Copyright (c) 2025 左岚. All rights reserved.
"""
数据驱动测试服务
"""
import json
import csv
import io
import os
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, desc
import pandas as pd

from ..models.ddt import ApiEngineDDT, ApiEngineDDTExecution
from ..models.case import ApiEngineCase
from ..engine.core.globalContext import g_context


class DDTService:
    """数据驱动测试服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ddt(
        self,
        case_id: int,
        name: str,
        description: str,
        data_source_type: str,
        data_content: Optional[List[Dict]] = None,
        file_path: Optional[str] = None,
        database_query: Optional[str] = None,
        database_config: Optional[Dict] = None,
        api_url: Optional[str] = None,
        api_headers: Optional[Dict] = None,
        api_params: Optional[Dict] = None,
        execution_mode: str = 'sequential',
        max_parallel: int = 5,
        failure_strategy: str = 'continue',
        max_retries: int = 0,
        created_by: int
    ) -> ApiEngineDDT:
        """创建数据驱动测试数据集"""
        ddt = ApiEngineDDT(
            case_id=case_id,
            name=name,
            description=description,
            data_source_type=data_source_type,
            data_content=data_content,
            file_path=file_path,
            database_query=database_query,
            database_config=database_config,
            api_url=api_url,
            api_headers=api_headers,
            api_params=api_params,
            execution_mode=execution_mode,
            max_parallel=max_parallel,
            failure_strategy=failure_strategy,
            max_retries=max_retries,
            created_by=created_by
        )

        self.db.add(ddt)
        await self.db.commit()
        await self.db.refresh(ddt)
        return ddt

    async def get_ddt(self, ddt_id: int) -> Optional[ApiEngineDDT]:
        """获取DDT数据集"""
        result = await self.db.execute(
            select(ApiEngineDDT).where(ApiEngineDDT.ddt_id == ddt_id)
        )
        return result.scalar_one_or_none()

    async def get_ddts_by_case(self, case_id: int) -> List[ApiEngineDDT]:
        """获取用例的所有DDT数据集"""
        result = await self.db.execute(
            select(ApiEngineDDT)
            .where(ApiEngineDDT.case_id == case_id)
            .where(ApiEngineDDT.is_active == 'yes')
            .order_by(ApiEngineDDT.sort_order, ApiEngineDDT.created_at)
        )
        return list(result.scalars().all())

    async def update_ddt(self, ddt_id: int, update_data: Dict) -> Optional[ApiEngineDDT]:
        """更新DDT数据集"""
        ddt = await self.get_ddt(ddt_id)
        if not ddt:
            return None

        for field, value in update_data.items():
            if hasattr(ddt, field):
                setattr(ddt, field, value)

        await self.db.commit()
        await self.db.refresh(ddt)
        return ddt

    async def delete_ddt(self, ddt_id: int) -> bool:
        """删除DDT数据集"""
        result = await self.db.execute(
            delete(ApiEngineDDT).where(ApiEngineDDT.ddt_id == ddt_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_test_data(self, ddt: ApiEngineDDT) -> List[Dict]:
        """获取测试数据"""
        if ddt.data_source_type == 'manual':
            return ddt.data_content or []

        elif ddt.data_source_type == 'file':
            return await self._load_data_from_file(ddt.file_path, ddt.file_type)

        elif ddt.data_source_type == 'database':
            return await self._load_data_from_database(ddt.database_query, ddt.database_config)

        elif ddt.data_source_type == 'api':
            return await self._load_data_from_api(ddt.api_url, ddt.api_headers, ddt.api_params)

        return []

    async def _load_data_from_file(self, file_path: str, file_type: str) -> List[Dict]:
        """从文件加载测试数据"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            if file_type.lower() == 'csv':
                df = pd.read_csv(file_path)
                return df.to_dict('records')

            elif file_type.lower() in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
                return df.to_dict('records')

            elif file_type.lower() == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data if isinstance(data, list) else [data]

            else:
                # 默认按CSV处理
                df = pd.read_csv(file_path)
                return df.to_dict('records')

        except Exception as e:
            raise ValueError(f"文件解析失败: {str(e)}")

    async def _load_data_from_database(self, query: str, config: Dict) -> List[Dict]:
        """从数据库加载测试数据"""
        try:
            import pymysql
            from pymysql.cursors import DictCursor

            if not config:
                raise ValueError("数据库配置不能为空")

            conn = pymysql.Connect(**config, cursorclass=DictCursor)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return results

        except Exception as e:
            raise ValueError(f"数据库查询失败: {str(e)}")

    async def _load_data_from_api(self, url: str, headers: Dict, params: Dict) -> List[Dict]:
        """从API接口加载测试数据"""
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                # 检查是否有常见的数据字段
                for key in ['data', 'results', 'items', 'list']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # 如果是单个对象，转换为列表
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("API返回的数据格式不支持")

        except Exception as e:
            raise ValueError(f"API请求失败: {str(e)}")

    async def execute_ddt(
        self,
        ddt_id: int,
        execution_context: Optional[Dict] = None,
        executed_by: int = 1
    ) -> Dict:
        """执行数据驱动测试"""
        ddt = await self.get_ddt(ddt_id)
        if not ddt:
            raise ValueError("DDT数据集不存在")

        # 获取测试数据
        test_data = await self.get_test_data(ddt)
        if not test_data:
            raise ValueError("没有可用的测试数据")

        # 生成批次ID
        batch_id = f"ddt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ddt_id}"

        # 创建执行记录
        executions = []
        for i, data_row in enumerate(test_data):
            execution = ApiEngineDDTExecution(
                ddt_id=ddt_id,
                case_id=ddt.case_id,
                batch_id=batch_id,
                data_index=i,
                data_row=data_row,
                status='pending',
                executed_by=executed_by
            )
            executions.append(execution)
            self.db.add(execution)

        await self.db.commit()

        # 执行测试
        if ddt.execution_mode == 'parallel':
            results = await self._execute_parallel(ddt, test_data, batch_id, execution_context)
        else:
            results = await self._execute_sequential(ddt, test_data, batch_id, execution_context)

        return {
            "batch_id": batch_id,
            "ddt_id": ddt_id,
            "total_cases": len(test_data),
            "execution_mode": ddt.execution_mode,
            "results": results
        }

    async def _execute_sequential(
        self,
        ddt: ApiEngineDDT,
        test_data: List[Dict],
        batch_id: str,
        execution_context: Optional[Dict]
    ) -> List[Dict]:
        """顺序执行"""
        results = []

        for i, data_row in enumerate(test_data):
            try:
                # 合并执行上下文和测试数据
                context = {**(execution_context or {}), **data_row}

                # 执行单个测试用例
                result = await self._execute_single_test(ddt.case_id, context, i, batch_id)
                results.append(result)

                # 检查失败策略
                if result['status'] == 'failed' and ddt.failure_strategy == 'stop':
                    break

            except Exception as e:
                error_result = {
                    "data_index": i,
                    "status": "error",
                    "error_message": str(e),
                    "execution_time": 0
                }
                results.append(error_result)

                if ddt.failure_strategy == 'stop':
                    break

        return results

    async def _execute_parallel(
        self,
        ddt: ApiEngineDDT,
        test_data: List[Dict],
        batch_id: str,
        execution_context: Optional[Dict]
    ) -> List[Dict]:
        """并行执行"""
        # 这里简化实现，实际应该使用异步任务队列
        # 为了演示，我们仍然顺序执行，但返回并行格式的结果
        return await self._execute_sequential(ddt, test_data, batch_id, execution_context)

    async def _execute_single_test(
        self,
        case_id: int,
        context: Dict,
        data_index: int,
        batch_id: str
    ) -> Dict:
        """执行单个测试"""
        start_time = datetime.now()

        try:
            # 这里应该调用实际的测试执行引擎
            # 为了演示，我们模拟执行过程
            from ..services.execution_service import ExecutionService
            from ..engine.extend.keywords import Keywords

            # 设置全局上下文
            for key, value in context.items():
                g_context().set_dict(key, value)

            # 模拟执行时间
            import time
            time.sleep(0.1)

            # 更新执行记录
            execution = await self.db.execute(
                select(ApiEngineDDTExecution)
                .where(ApiEngineDDTExecution.batch_id == batch_id)
                .where(ApiEngineDDTExecution.data_index == data_index)
            )
            execution_record = execution.scalar_one_or_none()

            if execution_record:
                execution_record.status = 'success'
                execution_record.execution_result = {
                    "context": context,
                    "message": "执行成功"
                }
                execution_record.started_at = start_time
                execution_record.finished_at = datetime.now()
                execution_record.execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                await self.db.commit()

            return {
                "data_index": data_index,
                "status": "success",
                "execution_time": execution_record.execution_time if execution_record else 0
            }

        except Exception as e:
            # 更新执行记录为失败状态
            execution = await self.db.execute(
                select(ApiEngineDDTExecution)
                .where(ApiEngineDDTExecution.batch_id == batch_id)
                .where(ApiEngineDDTExecution.data_index == data_index)
            )
            execution_record = execution.scalar_one_or_none()

            if execution_record:
                execution_record.status = 'failed'
                execution_record.error_message = str(e)
                execution_record.started_at = start_time
                execution_record.finished_at = datetime.now()
                execution_record.execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                await self.db.commit()

            return {
                "data_index": data_index,
                "status": "failed",
                "error_message": str(e),
                "execution_time": execution_record.execution_time if execution_record else 0
            }

    async def get_ddt_execution_results(self, batch_id: str) -> List[ApiEngineDDTExecution]:
        """获取DDT执行结果"""
        result = await self.db.execute(
            select(ApiEngineDDTExecution)
            .where(ApiEngineDDTExecution.batch_id == batch_id)
            .order_by(ApiEngineDDTExecution.data_index)
        )
        return list(result.scalars().all())

    async def get_ddt_statistics(self, ddt_id: int) -> Dict:
        """获取DDT统计信息"""
        # 统计执行记录
        result = await self.db.execute(
            select(
                func.count(ApiEngineDDTExecution.execution_id).label('total'),
                func.sum(func.case([(ApiEngineDDTExecution.status == 'success', 1)], else_=0)).label('success'),
                func.sum(func.case([(ApiEngineDDTExecution.status == 'failed', 1)], else_=0)).label('failed'),
                func.sum(func.case([(ApiEngineDDTExecution.status == 'error', 1)], else_=0)).label('error'),
                func.avg(ApiEngineDDTExecution.execution_time).label('avg_time')
            )
            .where(ApiEngineDDTExecution.ddt_id == ddt_id)
        )

        stats = result.first()

        return {
            "total_executions": stats.total or 0,
            "success_count": stats.success or 0,
            "failed_count": stats.failed or 0,
            "error_count": stats.error or 0,
            "success_rate": (stats.success / stats.total * 100) if stats.total else 0,
            "average_execution_time": stats.avg_time or 0
        }

    async def import_data_from_file(
        self,
        case_id: int,
        file_path: str,
        name: str,
        description: str,
        created_by: int
    ) -> ApiEngineDDT:
        """从文件导入测试数据"""
        # 确定文件类型
        file_ext = os.path.splitext(file_path)[1].lower()
        file_type_map = {
            '.csv': 'csv',
            '.xlsx': 'xlsx',
            '.xls': 'xls',
            '.json': 'json'
        }
        file_type = file_type_map.get(file_ext, 'csv')

        # 创建DDT数据集
        ddt = await self.create_ddt(
            case_id=case_id,
            name=name,
            description=description,
            data_source_type='file',
            file_path=file_path,
            file_type=file_type,
            created_by=created_by
        )

        # 预加载数据以验证
        try:
            await self.get_test_data(ddt)
        except Exception as e:
            # 如果数据加载失败，删除DDT记录
            await self.delete_ddt(ddt.ddt_id)
            raise ValueError(f"文件数据加载失败: {str(e)}")

        return ddt

    async def export_ddt_results(self, batch_id: str, format: str = 'json') -> bytes:
        """导出DDT执行结果"""
        executions = await self.get_ddt_execution_results(batch_id)

        if format.lower() == 'json':
            data = []
            for execution in executions:
                data.append({
                    "数据索引": execution.data_index,
                    "状态": execution.status,
                    "执行时间(ms)": execution.execution_time,
                    "开始时间": execution.started_at.isoformat() if execution.started_at else None,
                    "结束时间": execution.finished_at.isoformat() if execution.finished_at else None,
                    "错误信息": execution.error_message,
                    "测试数据": execution.data_row,
                    "执行结果": execution.execution_result
                })

            return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')

        elif format.lower() == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(['数据索引', '状态', '执行时间(ms)', '开始时间', '结束时间', '错误信息'])

            # 写入数据
            for execution in executions:
                writer.writerow([
                    execution.data_index,
                    execution.status,
                    execution.execution_time,
                    execution.started_at.isoformat() if execution.started_at else '',
                    execution.finished_at.isoformat() if execution.finished_at else '',
                    execution.error_message or ''
                ])

            return output.getvalue().encode('utf-8')

        else:
            raise ValueError(f"不支持的导出格式: {format}")