"""
Deep Agents Simple Core System

简化版多智能体系统，避免LangChain导入问题
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import uuid

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class WorkflowRequest(BaseModel):
    """工作流请求"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_input: str = Field(description="用户输入")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WorkflowResult(BaseModel):
    """工作流结果"""
    request_id: str = Field(description="请求ID")
    status: str = Field(description="执行状态")
    results: Dict[str, Any] = Field(default_factory=dict, description="结果数据")
    agent_outputs: Dict[str, str] = Field(default_factory=dict, description="智能体输出")
    workspace_files: List[str] = Field(default_factory=list, description="工作空间文件")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SimpleDeepAgentsSystem:
    """简化版Deep Agents多智能体系统"""
    
    def __init__(self):
        # 初始化LLM - 使用硅基流动
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            base_url="https://api.siliconflow.cn/v1",
            api_key="YOUR_SILICONFLOW_API_KEY"
        )
        
        # 创建工作空间目录
        self.workspace_dir = Path("./simple_agents_workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 智能体定义
        self.agents = {
            "planner": "负责API测试工作流规划和任务分解",
            "generator": "负责生成API测试代码和配置",
            "executor": "负责执行API测试和验证结果",
            "analyzer": "负责分析测试结果并生成报告"
        }
    
    async def run_workflow(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行完整的多智能体工作流"""
        request = WorkflowRequest(
            user_input=user_input,
            context=context or {}
        )
        
        workflow_result = WorkflowResult(
            request_id=request.request_id,
            status="running"
        )
        
        try:
            # 阶段1: Planning
            print("🧠 阶段1: Planning - API Planner Agent")
            planning_result = await self._run_planning_phase(request)
            workflow_result.agent_outputs["planner"] = planning_result
            
            # 阶段2: Generation
            print("⚡ 阶段2: Generation - API Generator Agent")
            generation_result = await self._run_generation_phase(planning_result)
            workflow_result.agent_outputs["generator"] = generation_result
            
            # 阶段3: Execution
            print("🚀 阶段3: Execution - API Executor Agent")
            execution_result = await self._run_execution_phase(generation_result)
            workflow_result.agent_outputs["executor"] = execution_result
            
            # 阶段4: Analysis
            print("📊 阶段4: Analysis - API Analyzer Agent")
            analysis_result = await self._run_analysis_phase(execution_result)
            workflow_result.agent_outputs["analyzer"] = analysis_result
            
            # 整合结果
            workflow_result.results = {
                "planning": planning_result,
                "generation": generation_result,
                "execution": execution_result,
                "analysis": analysis_result
            }
            
            # 保存工作空间文件
            workspace_files = await self._save_workspace_files(workflow_result)
            workflow_result.workspace_files = workspace_files
            
            workflow_result.status = "completed"
            
        except Exception as e:
            workflow_result.status = "failed"
            workflow_result.results["error"] = str(e)
        
        return workflow_result.dict()
    
    async def run_complete_workflow(self, user_input: str, context: Dict[str, Any] = None) -> WorkflowResult:
        """运行完整的多智能体工作流"""
        request = WorkflowRequest(
            user_input=user_input,
            context=context or {}
        )
        
        workflow_result = WorkflowResult(
            request_id=request.request_id,
            status="running"
        )
        
        try:
            # 阶段1: Planning
            print("🧠 阶段1: Planning - API Planner Agent")
            planning_result = await self._run_planning_phase(request)
            workflow_result.agent_outputs["planner"] = planning_result
            
            # 阶段2: Generation
            print("⚡ 阶段2: Generation - API Generator Agent")
            generation_result = await self._run_generation_phase(planning_result)
            workflow_result.agent_outputs["generator"] = generation_result
            
            # 阶段3: Execution
            print("🚀 阶段3: Execution - API Executor Agent")
            execution_result = await self._run_execution_phase(generation_result)
            workflow_result.agent_outputs["executor"] = execution_result
            
            # 阶段4: Analysis
            print("📊 阶段4: Analysis - API Analyzer Agent")
            analysis_result = await self._run_analysis_phase(execution_result)
            workflow_result.agent_outputs["analyzer"] = analysis_result
            
            # 整合结果
            workflow_result.results = {
                "planning": planning_result,
                "generation": generation_result,
                "execution": execution_result,
                "analysis": analysis_result
            }
            
            # 保存工作空间文件
            workspace_files = await self._save_workspace_files(workflow_result)
            workflow_result.workspace_files = workspace_files
            
            workflow_result.status = "completed"
            
        except Exception as e:
            workflow_result.status = "failed"
            workflow_result.results["error"] = str(e)
        
        return workflow_result
    
    async def _run_planning_phase(self, request: WorkflowRequest) -> Dict[str, Any]:
        """运行规划阶段"""
        prompt = f"""
        作为API测试规划专家，请分析以下需求并生成comprehensive的测试计划：
        
        用户需求：{request.user_input}
        
        请提供：
        1. API接口分析
        2. 测试场景规划
        3. 测试策略制定
        4. 任务分解步骤
        
        返回详细的规划结果。
        """
        
        response = await self.llm.ainvoke(prompt)
        
        planning_output = {
            "phase": "planning",
            "input": request.user_input,
            "output": response.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return planning_output
    
    async def _run_generation_phase(self, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """运行生成阶段"""
        prompt = f"""
        作为API测试代码生成专家，请基于以下测试计划生成可执行的测试代码：
        
        测试计划：{planning_result['output']}
        
        请提供：
        1. 测试代码生成
        2. 配置文件创建
        3. 测试数据准备
        4. 环境设置指南
        
        返回完整的生成结果。
        """
        
        response = await self.llm.ainvoke(prompt)
        
        generation_output = {
            "phase": "generation", 
            "input": planning_result["output"],
            "output": response.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return generation_output
    
    async def _run_execution_phase(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """运行执行阶段"""
        prompt = f"""
        作为API测试执行专家，请基于以下测试代码执行测试并收集结果：
        
        测试代码：{generation_result['output']}
        
        请提供：
        1. 测试执行结果
        2. 性能指标收集
        3. 错误日志分析
        4. 执行状态报告
        
        返回详细的执行结果。
        """
        
        response = await self.llm.ainvoke(prompt)
        
        execution_output = {
            "phase": "execution",
            "input": generation_result["output"],
            "output": response.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return execution_output
    
    async def _run_analysis_phase(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """运行分析阶段"""
        prompt = f"""
        作为API测试结果分析专家，请基于以下测试执行结果进行深度分析：
        
        执行结果：{execution_result['output']}
        
        请提供：
        1. 测试结果分析
        2. 性能趋势识别
        3. 问题根因分析
        4. 改进建议生成
        5. 综合报告创建
        
        返回comprehensive的分析结果。
        """
        
        response = await self.llm.ainvoke(prompt)
        
        analysis_output = {
            "phase": "analysis",
            "input": execution_result["output"],
            "output": response.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return analysis_output
    
    async def _save_workspace_files(self, workflow_result: WorkflowResult) -> List[str]:
        """保存工作空间文件"""
        workspace_files = []
        
        # 保存工作流结果
        result_file = self.workspace_dir / f"workflow_{workflow_result.request_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_result.dict(), f, indent=2, ensure_ascii=False)
        workspace_files.append(str(result_file))
        
        # 保存各个智能体的输出
        for agent_name, output in workflow_result.agent_outputs.items():
            agent_file = self.workspace_dir / f"{agent_name}_{workflow_result.request_id}.json"
            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            workspace_files.append(str(agent_file))
        
        return workspace_files
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """获取智能体状态"""
        status = {}
        
        for agent_name, description in self.agents.items():
            status[agent_name] = {
                "name": f"{agent_name.title()} Agent",
                "description": description,
                "tools": self._get_agent_tools(agent_name),
                "status": "active",
                "last_updated": datetime.utcnow().isoformat()
            }
        
        return status
    
    def _get_agent_tools(self, agent_name: str) -> List[str]:
        """获取智能体工具"""
        tools_mapping = {
            "planner": ["analyze_api_requirements", "decompose_test_tasks", "create_test_strategy"],
            "generator": ["generate_test_code", "create_test_config", "generate_test_data"],
            "executor": ["execute_api_tests", "validate_test_results", "monitor_test_execution"],
            "analyzer": ["analyze_test_results", "generate_insights", "create_recommendations"]
        }
        return tools_mapping.get(agent_name, [])
