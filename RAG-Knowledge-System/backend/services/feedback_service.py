"""
反馈服务 - 处理用户对AI回答的反馈
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select

from models.feedback import Feedback, FeedbackType
from core.logger import setup_logger

logger = setup_logger(__name__)


class FeedbackService:
    """反馈服务"""

    def __init__(self, db: Session):
        self.db = db

    async def submit_feedback(
        self,
        message_id: str,
        user_id: int,
        feedback_type: FeedbackType,
        comment: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Feedback:
        """
        提交反馈

        Args:
            message_id: 消息ID
            user_id: 用户ID
            feedback_type: 反馈类型（positive/negative）
            comment: 用户评论
            reason: 否定反馈的原因

        Returns:
            反馈记录
        """
        logger.info(f"收到用户反馈: user_id={user_id}, message_id={message_id}, type={feedback_type}")

        # 检查是否已有反馈
        existing = self.db.exec(
            select(Feedback).where(
                Feedback.message_id == message_id,
                Feedback.user_id == user_id
            )
        ).first()

        if existing:
            # 更新现有反馈
            existing.feedback_type = feedback_type
            existing.comment = comment
            existing.reason = reason
            existing.update_time = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            logger.info(f"更新已有反馈: feedback_id={existing.id}")
            return existing

        # 创建新反馈
        feedback = Feedback(
            message_id=message_id,
            user_id=user_id,
            feedback_type=feedback_type,
            comment=comment,
            reason=reason
        )

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        logger.info(f"创建新反馈: feedback_id={feedback.id}")
        return feedback

    def get_message_feedback(
        self,
        message_id: str
    ) -> Optional[Feedback]:
        """
        获取消息的反馈

        Args:
            message_id: 消息ID

        Returns:
            反馈记录或None
        """
        return self.db.exec(
            select(Feedback).where(Feedback.message_id == message_id)
        ).first()

    def get_message_feedback_stats(
        self,
        message_id: str
    ) -> dict:
        """
        获取消息的反馈统计

        Args:
            message_id: 消息ID

        Returns:
            统计字典
        """
        positive_count = len(self.db.exec(
            select(Feedback).where(
                Feedback.message_id == message_id,
                Feedback.feedback_type == FeedbackType.POSITIVE
            )
        ).all())

        negative_count = len(self.db.exec(
            select(Feedback).where(
                Feedback.message_id == message_id,
                Feedback.feedback_type == FeedbackType.NEGATIVE
            )
        ).all())

        total = positive_count + negative_count

        return {
            "message_id": message_id,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "total_count": total,
            "positive_rate": positive_count / total if total > 0 else 0.0,
            "negative_rate": negative_count / total if total > 0 else 0.0
        }

    def get_user_feedbacks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """
        获取用户的反馈列表

        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量

        Returns:
            反馈列表
        """
        return self.db.exec(
            select(Feedback)
            .where(Feedback.user_id == user_id)
            .order_by(Feedback.create_time.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_feedback_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        获取反馈报告

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            报告字典
        """
        query = select(Feedback)

        if start_date:
            query = query.where(Feedback.create_time >= start_date)
        if end_date:
            query = query.where(Feedback.create_time <= end_date)

        all_feedbacks = self.db.exec(query).all()

        # 统计
        positive_count = sum(1 for f in all_feedbacks if f.feedback_type == FeedbackType.POSITIVE)
        negative_count = sum(1 for f in all_feedbacks if f.feedback_type == FeedbackType.NEGATIVE)

        # 否定反馈原因统计
        negative_reasons = {}
        for f in all_feedbacks:
            if f.feedback_type == FeedbackType.NEGATIVE and f.reason:
                negative_reasons[f.reason] = negative_reasons.get(f.reason, 0) + 1

        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total_count": len(all_feedbacks),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "positive_rate": positive_count / len(all_feedbacks) if all_feedbacks else 0.0,
                "negative_rate": negative_count / len(all_feedbacks) if all_feedbacks else 0.0
            },
            "negative_reasons": negative_reasons
        }

    async def delete_feedback(self, feedback_id: int, user_id: int) -> bool:
        """
        删除反馈

        Args:
            feedback_id: 反馈ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        feedback = self.db.exec(
            select(Feedback).where(
                Feedback.id == feedback_id,
                Feedback.user_id == user_id
            )
        ).first()

        if not feedback:
            return False

        self.db.delete(feedback)
        self.db.commit()

        logger.info(f"删除反馈: feedback_id={feedback_id}, user_id={user_id}")
        return True
