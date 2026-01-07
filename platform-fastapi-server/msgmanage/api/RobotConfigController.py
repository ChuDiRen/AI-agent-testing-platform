"""
机器人配置Controller
"""
import time
from datetime import datetime

import httpx
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.RobotConfigModel import RobotConfig
from ..schemas.robot_config_schema import (
    RobotConfigQuery, RobotConfigCreate, RobotConfigUpdate,
    RobotTestRequest
)
from ..service.RobotConfigService import RobotConfigService

module_name = "RobotConfig"
module_model = RobotConfig
module_route = APIRouter(prefix=f"/{module_name}", tags=["机器人配置管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询机器人配置", dependencies=[Depends(check_permission("msgmanage:robot:query"))])
async def queryByPage(query: RobotConfigQuery, session: Session = Depends(get_session)):
    """分页查询机器人配置"""
    try:
        service = RobotConfigService(session)
        robots, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            robot_type=query.robot_type,
            robot_name=query.robot_name,
            is_enabled=query.is_enabled
        )
        logger.info(f"分页查询机器人配置成功，共{total}条记录")
        return respModel.ok_resp_list(lst=robots, total=total)
    except Exception as e:
        logger.error(f"分页查询机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryById", summary="根据ID查询机器人配置", dependencies=[Depends(check_permission("msgmanage:robot:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询机器人配置"""
    try:
        service = RobotConfigService(session)
        robot = service.get_by_id(id)
        if robot:
            logger.info(f"查询机器人配置成功: ID={id}")
            return respModel.ok_resp(obj=robot)
        else:
            logger.warning(f"查询机器人配置不存在: ID={id}")
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryAll", summary="查询所有启用的机器人配置", dependencies=[Depends(check_permission("msgmanage:robot:query"))])
async def queryAll(session: Session = Depends(get_session)):
    """查询所有启用的机器人配置"""
    try:
        service = RobotConfigService(session)
        robots = service.query_all()
        logger.info(f"查询所有机器人配置成功，共{len(robots)}条记录")
        return respModel.ok_resp_list(lst=robots, msg="查询成功")
    except Exception as e:
        logger.error(f"查询所有机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增机器人配置", dependencies=[Depends(check_permission("msgmanage:robot:add"))])
async def insert(robot: RobotConfigCreate, session: Session = Depends(get_session)):
    """新增机器人配置"""
    try:
        service = RobotConfigService(session)
        data = service.create(**robot.model_dump())
        logger.info(f"新增机器人配置成功: ID={data.id}, 名称={data.robot_name}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新机器人配置", dependencies=[Depends(check_permission("msgmanage:robot:edit"))])
async def update(robot: RobotConfigUpdate, session: Session = Depends(get_session)):
    """更新机器人配置"""
    try:
        service = RobotConfigService(session)
        update_data = robot.model_dump(exclude_unset=True, exclude={'id'})
        success = service.update(robot.id, update_data)
        if success:
            logger.info(f"更新机器人配置成功: ID={robot.id}")
            return respModel.ok_resp(msg="修改成功")
        else:
            logger.warning(f"更新机器人配置失败，配置不存在: ID={robot.id}")
            return respModel.error_resp(msg="机器人配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", summary="删除机器人配置", dependencies=[Depends(check_permission("msgmanage:robot:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除机器人配置"""
    try:
        service = RobotConfigService(session)
        success = service.delete(id)
        if success:
            logger.info(f"删除机器人配置成功: ID={id}")
            return respModel.ok_resp(msg="删除成功")
        else:
            logger.warning(f"删除机器人配置失败，配置不存在: ID={id}")
            return respModel.error_resp(msg="机器人配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


@module_route.put("/toggleEnabled", summary="启用/禁用机器人", dependencies=[Depends(check_permission("msgmanage:robot:edit"))])
async def toggleEnabled(id: int = Query(...), is_enabled: bool = Query(...), session: Session = Depends(get_session)):
    """启用或禁用机器人配置"""
    try:
        statement = select(module_model).where(module_model.id == id)
        robot = session.exec(statement).first()
        if robot:
            robot.is_enabled = is_enabled
            robot.update_time = datetime.now()
            session.commit()
            status_text = "启用" if is_enabled else "禁用"
            return respModel.ok_resp(msg=f"已{status_text}该机器人")
        else:
            return respModel.error_resp(msg="机器人配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"操作失败: {e}")


@module_route.post("/testConnection", summary="测试机器人连接", dependencies=[Depends(check_permission("msgmanage:robot:test"))])
async def testConnection(request: RobotTestRequest, session: Session = Depends(get_session)):
    """测试机器人连接"""
    try:
        # 获取机器人配置
        statement = select(module_model).where(module_model.id == request.robot_id)
        robot = session.exec(statement).first()
        
        if not robot:
            return respModel.error_resp(msg="机器人配置不存在")
        
        # 构造测试消息
        test_message = {
            "msgtype": "text",
            "text": {
                "content": request.test_message
            }
        }
        
        # 发送测试请求
        start_time = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(robot.webhook_url, json=test_message)
            response_time = int((time.time() - start_time) * 1000)
        
        # 更新最后测试时间
        robot.last_test_time = datetime.now()
        session.commit()
        
        if response.status_code == 200:
            return respModel.ok_resp(
                msg="连接测试成功",
                dic_t={
                    "success": True,
                    "response_time": response_time,
                    "message": "机器人连接正常"
                }
            )
        else:
            return respModel.error_resp(
                msg=f"连接测试失败: HTTP {response.status_code}"
            )
    except Exception as e:
        logger.error(f"测试机器人连接失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"测试失败: {e}")
