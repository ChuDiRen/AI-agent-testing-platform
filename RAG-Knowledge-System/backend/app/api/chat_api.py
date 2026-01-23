"""
智能问答API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from services.chat_service import ChatService
from rag.rag_engine import RAGEngine
from services.llm_service import LLMService
from db.session import get_db
from core.deps import get_current_user
from models.user import User
from core.resp_model import ResponseModel

router = APIRouter(prefix="/chat", tags=["智能问答"])


@router.post("", response_model=ResponseModel)
async def chat(
    message: str,
    session_id: Optional[str] = None,
    top_k: Optional[int] = None,
    score_threshold: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends()
):
    """
    智能问答

    需要认证
    """
    try:
        response = await chat_service.chat(
            query=message,
            session_id=session_id,
            user_id=current_user.id,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return ResponseModel.success(
            data=response.dict(),
            message="问答成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


@router.post("/with-history", response_model=ResponseModel)
async def chat_with_history(
    message: str,
    session_id: str,
    top_k: Optional[int] = None,
    score_threshold: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends()
):
    """
    带历史记录的智能问答

    需要认证
    """
    try:
        response = await chat_service.chat_with_history(
            query=message,
            session_id=session_id,
            user_id=current_user.id,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return ResponseModel.success(
            data=response.dict(),
            message="问答成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


@router.get("/history/{session_id}", response_model=ResponseModel)
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends()
):
    """
    获取聊天历史

    需要认证
    """
    try:
        history = chat_service.get_chat_history(session_id)

        return ResponseModel.success(
            data={
                "session_id": session_id,
                "messages": [msg.dict() for msg in history]
            },
            message="获取历史成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.delete("/history/{session_id}", response_model=ResponseModel)
async def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends()
):
    """
    清空聊天历史

    需要认证
    """
    try:
        success = chat_service.clear_chat_history(session_id)

        if success:
            return ResponseModel.success(
                data={"session_id": session_id},
                message="清空历史成功"
            )
        else:
            return ResponseModel.error(
                message="会话不存在"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史失败: {str(e)}")


@router.post("/search", response_model=ResponseModel)
async def search_documents(
    query: str,
    top_k: int = 5,
    score_threshold: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag_engine: RAGEngine = Depends()
):
    """
    文档检索（不生成回答）

    需要认证
    """
    try:
        results = await rag_engine.search(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return ResponseModel.success(
            data={
                "query": query,
                "results": results,
                "count": len(results)
            },
            message="检索成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")
