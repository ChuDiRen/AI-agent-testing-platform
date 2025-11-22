"""
机器人配置Controller
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from ..model.RobotConfigModel import RobotConfig
from ..schemas.robot_config_schema import (
    RobotConfigQuery, RobotConfigCreate, RobotConfigUpdate,
    RobotConfigResponse, RobotTestRequest, RobotTestResponse
)
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from datetime import datetime
import httpx
import time


module_name = "RobotConfig"
module_model = RobotConfig
module_route = APIRouter(prefix=f"/{module_name}", tags=["机器人配置管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", dependencies=[Depends(check_permission("msgmanage:robot:query"))])
def queryByPage(query: RobotConfigQuery, session: Session = Depends(get_session)):
    """分页查询机器人配置"""
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model).limit(query.pageSize).offset(offset)
        
        # 添加过滤条件
        if query.robot_type:
            statement = statement.where(module_model.robot_type == query.robot_type)
        if query.robot_name:
            statement = statement.where(module_model.robot_name.contains(query.robot_name))
        if query.is_enabled is not None:
            statement = statement.where(module_model.is_enabled == query.is_enabled)
        
        robots = session.exec(statement).all()
        
        # 计算总数
        count_statement = select(module_model)
        if query.robot_type:
            count_statement = count_statement.where(module_model.robot_type == query.robot_type)
        if query.robot_name:
            count_statement = count_statement.where(module_model.robot_name.contains(query.robot_name))
        if query.is_enabled is not None:
            count_statement = count_statement.where(module_model.is_enabled == query.is_enabled)
        
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=robots, total=total)
    except Exception as e:
        logger.error(f"分页查询机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryById")
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询机器人配置"""
    try:
        statement = select(module_model).where(module_model.id == id)
        robot = session.exec(statement).first()
        if robot:
            return respModel.ok_resp(obj=robot)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryAll")
def queryAll(session: Session = Depends(get_session)):
    """查询所有启用的机器人配置"""
    try:
        statement = select(module_model).where(module_model.is_enabled == True)
        robots = session.exec(statement).all()
        return respModel.ok_resp_list(lst=robots, msg="查询成功")
    except Exception as e:
        logger.error(f"查询所有机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", dependencies=[Depends(check_permission("msgmanage:robot:add"))])
def insert(robot: RobotConfigCreate, session: Session = Depends(get_session)):
    """新增机器人配置"""
    try:
        data = module_model(**robot.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", dependencies=[Depends(check_permission("msgmanage:robot:edit"))])
def update(robot: RobotConfigUpdate, session: Session = Depends(get_session)):
    """更新机器人配置"""
    try:
        statement = select(module_model).where(module_model.id == robot.id)
        db_robot = session.exec(statement).first()
        if db_robot:
            update_data = robot.model_dump(exclude_unset=True, exclude={'id'})
            update_data['update_time'] = datetime.now()
            
            for key, value in update_data.items():
                setattr(db_robot, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="机器人配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", dependencies=[Depends(check_permission("msgmanage:robot:delete"))])
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除机器人配置"""
    try:
        statement = select(module_model).where(module_model.id == id)
        robot = session.exec(statement).first()
        if robot:
            session.delete(robot)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="机器人配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除机器人配置失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


@module_route.post("/testConnection", dependencies=[Depends(check_permission("msgmanage:robot:test"))])
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
