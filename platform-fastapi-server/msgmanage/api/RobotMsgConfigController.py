"""
机器人消息模板配置Controller
"""
import json
import re
from datetime import datetime

import httpx
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.RobotConfigModel import RobotConfig
from ..model.RobotMsgConfigModel import RobotMsgConfig
from ..schemas.robot_msg_config_schema import (
    RobotMsgConfigQuery, RobotMsgConfigCreate, RobotMsgConfigUpdate,
    MessageSendRequest
)

module_name = "RobotMsgConfig"
module_model = RobotMsgConfig
module_route = APIRouter(prefix=f"/{module_name}", tags=["机器人消息模板管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询消息模板", dependencies=[Depends(check_permission("msgmanage:template:query"))])
def queryByPage(query: RobotMsgConfigQuery, session: Session = Depends(get_session)):
    """分页查询消息模板"""
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model).limit(query.pageSize).offset(offset)
        
        # 添加过滤条件
        if query.robot_id:
            statement = statement.where(module_model.robot_id == query.robot_id)
        if query.msg_type:
            statement = statement.where(module_model.msg_type == query.msg_type)
        if query.template_name:
            statement = statement.where(module_model.template_name.contains(query.template_name))
        if query.is_enabled is not None:
            statement = statement.where(module_model.is_enabled == query.is_enabled)
        
        templates = session.exec(statement).all()
        
        # 计算总数
        count_statement = select(module_model)
        if query.robot_id:
            count_statement = count_statement.where(module_model.robot_id == query.robot_id)
        if query.msg_type:
            count_statement = count_statement.where(module_model.msg_type == query.msg_type)
        if query.template_name:
            count_statement = count_statement.where(module_model.template_name.contains(query.template_name))
        if query.is_enabled is not None:
            count_statement = count_statement.where(module_model.is_enabled == query.is_enabled)
        
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=templates, total=total)
    except Exception as e:
        logger.error(f"分页查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryById", summary="根据ID查询消息模板", dependencies=[Depends(check_permission("msgmanage:template:query"))])
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询消息模板"""
    try:
        statement = select(module_model).where(module_model.id == id)
        template = session.exec(statement).first()
        if template:
            return respModel.ok_resp(obj=template)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryByRobotId", summary="根据机器人ID查询消息模板", dependencies=[Depends(check_permission("msgmanage:template:query"))])
def queryByRobotId(robot_id: int = Query(...), session: Session = Depends(get_session)):
    """根据机器人ID查询所有模板"""
    try:
        statement = select(module_model).where(
            module_model.robot_id == robot_id,
            module_model.is_enabled == True
        )
        templates = session.exec(statement).all()
        return respModel.ok_resp_list(lst=templates, msg="查询成功")
    except Exception as e:
        logger.error(f"根据机器人ID查询模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增消息模板", dependencies=[Depends(check_permission("msgmanage:template:add"))])
def insert(template: RobotMsgConfigCreate, session: Session = Depends(get_session)):
    """新增消息模板"""
    try:
        data = module_model(**template.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新消息模板", dependencies=[Depends(check_permission("msgmanage:template:edit"))])
def update(template: RobotMsgConfigUpdate, session: Session = Depends(get_session)):
    """更新消息模板"""
    try:
        statement = select(module_model).where(module_model.id == template.id)
        db_template = session.exec(statement).first()
        if db_template:
            update_data = template.model_dump(exclude_unset=True, exclude={'id'})
            update_data['update_time'] = datetime.now()
            
            for key, value in update_data.items():
                setattr(db_template, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="消息模板不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", summary="删除消息模板", dependencies=[Depends(check_permission("msgmanage:template:delete"))])
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除消息模板"""
    try:
        statement = select(module_model).where(module_model.id == id)
        template = session.exec(statement).first()
        if template:
            session.delete(template)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="消息模板不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


def replace_variables(template_content: str, variables: dict) -> str:
    """替换模板中的变量"""
    if not variables:
        return template_content
    
    # 替换 {{variable}} 格式的变量
    for key, value in variables.items():
        pattern = r'\{\{' + re.escape(key) + r'\}\}'
        template_content = re.sub(pattern, str(value), template_content)
    
    return template_content


@module_route.post("/send", summary="发送消息", dependencies=[Depends(check_permission("msgmanage:template:send"))])
async def send(request: MessageSendRequest, session: Session = Depends(get_session)):
    """发送消息"""
    try:
        # 获取消息模板
        template_statement = select(module_model).where(module_model.id == request.template_id)
        template = session.exec(template_statement).first()
        
        if not template:
            return respModel.error_resp(msg="消息模板不存在")
        
        if not template.is_enabled:
            return respModel.error_resp(msg="消息模板未启用")
        
        # 获取机器人配置
        robot_statement = select(RobotConfig).where(RobotConfig.id == template.robot_id)
        robot = session.exec(robot_statement).first()
        
        if not robot:
            return respModel.error_resp(msg="机器人配置不存在")
        
        if not robot.is_enabled:
            return respModel.error_resp(msg="机器人未启用")
        
        # 替换变量
        message_content = replace_variables(template.template_content, request.variables or {})
        
        # 构造消息体
        if template.msg_type == "text":
            message_body = {
                "msgtype": "text",
                "text": {
                    "content": message_content
                }
            }
        elif template.msg_type == "markdown":
            message_body = {
                "msgtype": "markdown",
                "markdown": {
                    "title": template.template_name,
                    "text": message_content
                }
            }
        elif template.msg_type == "card":
            # 对于卡片消息，template_content应该是JSON格式
            try:
                message_body = json.loads(message_content)
            except:
                message_body = {
                    "msg_type": "interactive",
                    "card": json.loads(message_content)
                }
        else:
            return respModel.error_resp(msg=f"不支持的消息类型: {template.msg_type}")
        
        # 发送消息
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(robot.webhook_url, json=message_body)
        
        if response.status_code == 200:
            return respModel.ok_resp(
                msg="消息发送成功",
                dic_t={
                    "success": True,
                    "robot_name": robot.robot_name,
                    "sent_at": datetime.now().isoformat()
                }
            )
        else:
            return respModel.error_resp(
                msg=f"消息发送失败: HTTP {response.status_code}, {response.text}"
            )
    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"发送失败: {e}")


@module_route.post("/sendToRabbitMQ", summary="推送消息任务到RabbitMQ", dependencies=[Depends(check_permission("msgmanage:template:send"))])
async def sendToRabbitMQ(request: MessageSendRequest, session: Session = Depends(get_session)):
    """将消息发送任务推送到RabbitMQ队列（异步处理）"""
    try:
        from core.RabbitMQManager import rabbitmq_manager
        
        # 获取模板和机器人信息
        template_statement = select(module_model).where(module_model.id == request.template_id)
        template = session.exec(template_statement).first()
        
        if not template or not template.is_enabled:
            return respModel.error_resp(msg="消息模板不存在或未启用")
        
        # 构造消息任务
        message_task = {
            "template_id": request.template_id,
            "robot_id": template.robot_id,
            "variables": request.variables or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 发布到RabbitMQ
        rabbitmq_manager.publish_message_push(message_task)
        
        return respModel.ok_resp(
            msg="消息已加入发送队列",
            dic_t={"task_id": message_task["timestamp"]}
        )
    except Exception as e:
        logger.error(f"推送消息任务到队列失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"推送失败: {e}")
