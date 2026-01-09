# -*- coding: utf-8 -*-
"""系统统计控制器"""
from sqlmodel import Session, select, func
from fastapi import APIRouter, Depends

from app.database.database import get_session
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from app.models.UserModel import User
from app.models.RoleModel import Role
from app.models.MenuModel import Menu
from app.models.DeptModel import Dept
from app.models.GenTable import GenTable
from app.models.GenHistory import GenHistory

router = APIRouter(prefix="/ApiStatistics", tags=["系统统计"])
logger = get_logger(__name__)

@router.get("/overview", summary="获取系统总览统计")
async def get_overview(session: Session = Depends(get_session)):
    """获取系统总览统计数据"""
    try:
        user_count = len(session.exec(select(User)).all())
        role_count = len(session.exec(select(Role)).all())
        menu_count = len(session.exec(select(Menu)).all())
        dept_count = len(session.exec(select(Dept)).all())
        table_count = len(session.exec(select(GenTable)).all())
        gen_count = len(session.exec(select(GenHistory)).all())
        
        data = {
            "userCount": user_count,
            "roleCount": role_count,
            "menuCount": menu_count,
            "deptCount": dept_count,
            "tableCount": table_count,
            "genCount": gen_count,
            "onlineUsers": 0,
            "totalProjects": 0,
            "totalTests": 0,
            "successRate": 0,
            "avgTime": 0
        }
        
        return respModel.ok_resp(obj=data, msg="获取统计数据成功")
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取统计数据失败: {e}")
