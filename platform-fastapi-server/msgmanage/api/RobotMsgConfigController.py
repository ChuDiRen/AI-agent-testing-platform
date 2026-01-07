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
from ..service.RobotMsgConfigService import RobotMsgConfigService

module_name = "RobotMsgConfig"
module_model = RobotMsgConfig
module_route = APIRouter(prefix=f"/{module_name}", tags=["机器人消息模板管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询消息模板", dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def queryByPage(query: RobotMsgConfigQuery, session: Session = Depends(get_session)):
    """分页查询消息模板"""
    try:
        service = RobotMsgConfigService(session)
        templates, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            robot_id=query.robot_id,
            msg_type=query.msg_type,
            template_name=query.template_name,
            is_enabled=query.is_enabled
        )
        logger.info(f"分页查询消息模板成功，共{total}条记录")
        return respModel.ok_resp_list(lst=templates, total=total)
    except Exception as e:
        logger.error(f"分页查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryById", summary="根据ID查询消息模板", dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询消息模板"""
    try:
        service = RobotMsgConfigService(session)
        template = service.get_by_id(id)
        if template:
            logger.info(f"查询消息模板成功: ID={id}")
            return respModel.ok_resp(obj=template)
        else:
            logger.warning(f"查询消息模板不存在: ID={id}")
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryByRobotId", summary="根据机器人ID查询消息模板", dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def queryByRobotId(robot_id: int = Query(...), session: Session = Depends(get_session)):
    """根据机器人ID查询所有模板"""
    try:
        service = RobotMsgConfigService(session)
        templates = service.get_by_robot_id(robot_id)
        logger.info(f"根据机器人ID查询模板成功: robot_id={robot_id}, 共{len(templates)}条")
        return respModel.ok_resp_list(lst=templates, msg="查询成功")
    except Exception as e:
        logger.error(f"根据机器人ID查询模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增消息模板", dependencies=[Depends(check_permission("msgmanage:template:add"))])
async def insert(template: RobotMsgConfigCreate, session: Session = Depends(get_session)):
    """新增消息模板"""
    try:
        service = RobotMsgConfigService(session)
        data = service.create(**template.model_dump())
        logger.info(f"新增消息模板成功: ID={data.id}, 名称={data.template_name}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新消息模板", dependencies=[Depends(check_permission("msgmanage:template:edit"))])
async def update(template: RobotMsgConfigUpdate, session: Session = Depends(get_session)):
    """更新消息模板"""
    try:
        service = RobotMsgConfigService(session)
        update_data = template.model_dump(exclude_unset=True, exclude={'id'})
        success = service.update(template.id, update_data)
        if success:
            logger.info(f"更新消息模板成功: ID={template.id}")
            return respModel.ok_resp(msg="修改成功")
        else:
            logger.warning(f"更新消息模板失败，模板不存在: ID={template.id}")
            return respModel.error_resp(msg="消息模板不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", summary="删除消息模板", dependencies=[Depends(check_permission("msgmanage:template:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除消息模板"""
    try:
        service = RobotMsgConfigService(session)
        success = service.delete(id)
        if success:
            logger.info(f"删除消息模板成功: ID={id}")
            return respModel.ok_resp(msg="删除成功")
        else:
            logger.warning(f"删除消息模板失败，模板不存在: ID={id}")
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
        service = RobotMsgConfigService(session)
        # 获取消息模板
        template = service.get_by_id(request.template_id)

        if not template:
            logger.warning(f"发送消息失败：消息模板不存在: template_id={request.template_id}")
            return respModel.error_resp(msg="消息模板不存在")

        if not template.is_enabled:
            logger.warning(f"发送消息失败：消息模板未启用: template_id={request.template_id}")
            return respModel.error_resp(msg="消息模板未启用")

        # 获取机器人配置
        robot_statement = select(RobotConfig).where(RobotConfig.id == template.robot_id)
        robot = session.exec(robot_statement).first()

        if not robot:
            logger.warning(f"发送消息失败：机器人配置不存在: robot_id={template.robot_id}")
            return respModel.error_resp(msg="机器人配置不存在")

        if not robot.is_enabled:
            logger.warning(f"发送消息失败：机器人未启用: robot_id={template.robot_id}")
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
            logger.info(f"消息发送成功: template_id={request.template_id}, robot={robot.robot_name}")
            return respModel.ok_resp(
                msg="消息发送成功",
                dic_t={
                    "success": True,
                    "robot_name": robot.robot_name,
                    "sent_at": datetime.now().isoformat()
                }
            )
        else:
            logger.error(f"消息发送失败: HTTP {response.status_code}, {response.text}")
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

        service = RobotMsgConfigService(session)
        # 获取模板信息
        template = service.get_by_id(request.template_id)

        if not template or not template.is_enabled:
            logger.warning(f"推送消息任务失败：模板不存在或未启用: template_id={request.template_id}")
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
        logger.info(f"推送消息任务到队列成功: template_id={request.template_id}")

        return respModel.ok_resp(
            msg="消息已加入发送队列",
            dic_t={"task_id": message_task["timestamp"]}
        )
    except Exception as e:
        logger.error(f"推送消息任务到队列失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"推送失败: {e}")
