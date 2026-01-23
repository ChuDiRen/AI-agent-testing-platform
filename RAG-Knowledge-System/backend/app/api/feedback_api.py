"""
反馈API - 用户对AI回答的反馈
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.feedback_service import FeedbackService
from models.feedback import FeedbackType
from db.session import get_db
from core.deps import get_current_user
from models.user import User
from core.resp_model import ResponseModel

router = APIRouter(prefix="/feedback", tags=["用户反馈"])


class FeedbackRequest(BaseModel):
    """反馈请求"""
    message_id: str
    feedback_type: FeedbackType
    comment: Optional[str] = None
    reason: Optional[str] = None


@router.post("", response_model=ResponseModel)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交反馈

    需要认证
    """
    try:
        feedback_service = FeedbackService(db)
        feedback = await feedback_service.submit_feedback(
            message_id=request.message_id,
            user_id=current_user.id,
            feedback_type=request.feedback_type,
            comment=request.comment,
            reason=request.reason
        )

        return ResponseModel.success(
            data={
                "feedback_id": feedback.id,
                "message_id": feedback.message_id,
                "feedback_type": feedback.feedback_type.value
            },
            message="反馈提交成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")


@router.get("/message/{message_id}", response_model=ResponseModel)
async def get_message_feedback(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取消息的反馈

    需要认证
    """
    try:
        feedback_service = FeedbackService(db)
        feedback = feedback_service.get_message_feedback(message_id)

        if feedback:
            return ResponseModel.success(
                data=feedback.dict(),
                message="获取反馈成功"
            )
        else:
            return ResponseModel.success(
                data=None,
                message="暂无反馈"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取反馈失败: {str(e)}")


@router.get("/message/{message_id}/stats", response_model=ResponseModel)
async def get_message_feedback_stats(
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    获取消息的反馈统计

    需要认证
    """
    try:
        feedback_service = FeedbackService(db)
        stats = feedback_service.get_message_feedback_stats(message_id)

        return ResponseModel.success(
            data=stats,
            message="获取统计成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/my-feedbacks", response_model=ResponseModel)
async def get_my_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的反馈列表

    需要认证
    """
    try:
        feedback_service = FeedbackService(db)
        feedbacks = feedback_service.get_user_feedbacks(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )

        return ResponseModel.success(
            data={
                "items": [f.dict() for f in feedbacks],
                "count": len(feedbacks)
            },
            message="获取反馈列表成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取反馈列表失败: {str(e)}")


@router.get("/report", response_model=ResponseModel)
async def get_feedback_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取反馈报告

    需要认证
    """
    try:
        feedback_service = FeedbackService(db)

        # 转换日期字符串
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        report = feedback_service.get_feedback_report(start_dt, end_dt)

        return ResponseModel.success(
            data=report,
            message="获取报告成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")


@router.delete("/{feedback_id}", response_model=ResponseModel)
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除反馈

    需要认证
    """
    try:
        feedback_service = FeedbackService(db)
        success = await feedback_service.delete_feedback(feedback_id, current_user.id)

        if success:
            return ResponseModel.success(
                data={"feedback_id": feedback_id},
                message="删除反馈成功"
            )
        else:
            return ResponseModel.error(
                message="反馈不存在或无权删除"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除反馈失败: {str(e)}")
