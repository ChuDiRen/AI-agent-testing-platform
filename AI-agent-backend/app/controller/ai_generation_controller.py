# Copyright (c) 2025 左岚. All rights reserved.
"""
AI测试用例生成Controller
处理AI智能测试用例生成相关的HTTP请求
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.service.multi_agent_service import MultiAgentTestCaseGenerator
from app.service.test_case_service import TestCaseService
from app.dto.test_case_dto import (
    TestCaseGenerationRequest, TestCaseGenerationResponse
)
from app.dto.base import Success, Fail
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai-generation", tags=["AI测试用例生成"])


@router.post("/generate-test-cases", response_model=TestCaseGenerationResponse, summary="AI生成测试用例")
async def generate_test_cases(
    request: TestCaseGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """使用AI智能生成测试用例"""
    try:
        # 初始化多智能体生成器
        generator = MultiAgentTestCaseGenerator()
        
        # 生成配置
        generation_config = request.generation_config or {}
        generation_config.update({
            "target_module": request.target_module,
            "test_types": [t.value for t in request.test_types] if request.test_types else None,
            "priority_levels": [p.value for p in request.priority_levels] if request.priority_levels else None,
            "max_cases": request.max_cases,
            "include_edge_cases": request.include_edge_cases,
            "include_negative_cases": request.include_negative_cases
        })
        
        # 开始生成测试用例
        result = await generator.generate_test_cases(
            requirements_document=request.requirements_document,
            generation_config=generation_config
        )
        
        # 如果生成成功，可以选择自动保存到数据库
        if result["status"] == "completed" and result["generated_cases"]:
            background_tasks.add_task(
                save_generated_test_cases,
                db,
                result["generated_cases"],
                request.agent_id,
                current_user.get("user_id")
            )
        
        response = TestCaseGenerationResponse(**result)
        
        return Success(data=response, msg=f"AI生成完成，共生成 {result['total_generated']} 个测试用例")
        
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        return Fail(msg=f"AI生成测试用例失败: {str(e)}")


def save_generated_test_cases(db: Session, generated_cases: list, 
                            agent_id: int, created_by_id: int):
    """后台任务：保存生成的测试用例到数据库"""
    try:
        test_case_service = TestCaseService(db)
        saved_count = 0
        
        for case_data in generated_cases:
            try:
                # 将AI生成的格式转换为CreateRequest格式
                from app.dto.test_case_dto import TestCaseCreateRequest
                
                request = TestCaseCreateRequest(
                    name=case_data.get("用例名称", ""),
                    module=case_data.get("所属模块", ""),
                    description=case_data.get("备注", ""),
                    preconditions=case_data.get("前置条件", ""),
                    test_steps=case_data.get("步骤描述", ""),
                    expected_result=case_data.get("预期结果", ""),
                    tags=case_data.get("标签", "AI生成"),
                    agent_id=agent_id,
                    metadata={"generated_by": "ai", "case_id": case_data.get("ID", "")}
                )
                
                test_case_service.create_test_case(request, created_by_id)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving test case {case_data.get('ID', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Saved {saved_count}/{len(generated_cases)} generated test cases to database")
        
    except Exception as e:
        logger.error(f"Error in background task save_generated_test_cases: {str(e)}")


@router.get("/generation-status/{generation_id}", summary="获取生成状态")
def get_generation_status(
    generation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试用例生成状态"""
    try:
        # 这里应该实现获取生成状态的逻辑
        # 可以从缓存或数据库中查询生成任务的状态
        
        # 模拟返回状态
        status = {
            "generation_id": generation_id,
            "status": "completed",  # 或 "generating", "failed"
            "progress": 100,
            "message": "测试用例生成完成"
        }
        
        return Success(data=status)
        
    except Exception as e:
        logger.error(f"Error getting generation status: {str(e)}")
        return Fail(msg=f"获取生成状态失败: {str(e)}")
