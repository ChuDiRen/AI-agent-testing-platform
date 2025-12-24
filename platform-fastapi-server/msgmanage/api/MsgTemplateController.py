"""
消息模板 Controller
"""
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..schemas.msg_template_schema import (
    MsgTemplateInsert,
    MsgTemplateUpdate,
    MsgTemplateQuery,
    TemplatePreviewRequest
)
from ..service.msg_template_service import MsgTemplateService, get_template_service

module_name = "msgmanage"
template_route = APIRouter(prefix="/template", tags=["消息模板管理"])
logger = get_logger(__name__)


@template_route.post("/queryByPage", summary="分页查询消息模板",
                    dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def query_by_page(query: MsgTemplateQuery, session: Session = Depends(get_session)):
    """分页查询消息模板"""
    try:
        service = get_template_service(session)
        result = service.query_by_page(query)
        return respModel.ok_resp_list(lst=result["list"], total=result["total"])
    except ValueError as e:
        logger.warning(f"查询模板参数错误: {e}")
        return respModel.error_resp(f"参数错误: {e}")
    except Exception as e:
        logger.error(f"分页查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.get("/queryById", summary="根据ID查询消息模板",
                   dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def query_by_id(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询消息模板"""
    try:
        service = get_template_service(session)
        result = service.get_by_id(id)
        if result:
            return respModel.ok_resp(obj=result)
        return respModel.error_resp("模板不存在")
    except Exception as e:
        logger.error(f"查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.get("/queryByCode", summary="根据模板编码查询消息模板",
                    dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def query_by_code(template_code: str = Query(...), session: Session = Depends(get_session)):
    """根据模板编码查询消息模板"""
    try:
        service = get_template_service(session)
        template = service.get_by_code(template_code)
        if template:
            return respModel.ok_resp(obj=service._to_dict(template))
        return respModel.error_resp("模板不存在或已禁用")
    except Exception as e:
        logger.error(f"根据编码查询消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.post("/insert", summary="新增消息模板",
                    dependencies=[Depends(check_permission("msgmanage:template:add"))])
async def insert(template: MsgTemplateInsert, session: Session = Depends(get_session)):
    """新增消息模板"""
    try:
        service = get_template_service(session)
        result = service.create(template)
        return respModel.ok_resp(msg="新增成功", dic_t={"id": result["id"]})
    except ValueError as e:
        logger.warning(f"新增消息模板失败: {e}")
        return respModel.error_resp(str(e))
    except Exception as e:
        logger.error(f"新增消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.put("/update", summary="更新消息模板",
                   dependencies=[Depends(check_permission("msgmanage:template:edit"))])
async def update(template: MsgTemplateUpdate, session: Session = Depends(get_session)):
    """更新消息模板"""
    try:
        service = get_template_service(session)
        result = service.update(template)
        return respModel.ok_resp(msg="更新成功", obj=result)
    except ValueError as e:
        logger.warning(f"更新消息模板失败: {e}")
        return respModel.error_resp(str(e))
    except Exception as e:
        logger.error(f"更新消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.delete("/delete", summary="删除消息模板",
                      dependencies=[Depends(check_permission("msgmanage:template:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除消息模板"""
    try:
        service = get_template_service(session)
        service.delete(id)
        return respModel.ok_resp(msg="删除成功")
    except ValueError as e:
        logger.warning(f"删除消息模板失败: {e}")
        return respModel.error_resp(str(e))
    except Exception as e:
        logger.error(f"删除消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.post("/preview", summary="预览消息模板",
                    dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def preview(request: TemplatePreviewRequest, session: Session = Depends(get_session)):
    """预览消息模板（变量替换）"""
    try:
        service = get_template_service(session)
        result = service.preview_template(request.template_code, request.params)
        return respModel.ok_resp(obj=result, msg="预览成功")
    except ValueError as e:
        logger.warning(f"预览消息模板失败: {e}")
        return respModel.error_resp(str(e))
    except Exception as e:
        logger.error(f"预览消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.post("/render", summary="渲染消息模板",
                    dependencies=[Depends(check_permission("msgmanage:template:render"))])
async def render(request: TemplatePreviewRequest, session: Session = Depends(get_session)):
    """渲染消息模板（用于实际发送）"""
    try:
        service = get_template_service(session)
        result = service.render_template(request.template_code, request.params)
        return respModel.ok_resp(obj=result, msg="渲染成功")
    except ValueError as e:
        logger.warning(f"渲染消息模板失败: {e}")
        return respModel.error_resp(str(e))
    except Exception as e:
        logger.error(f"渲染消息模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@template_route.get("/types", summary="获取模板类型列表",
                   dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def get_template_types():
    """获取模板类型列表"""
    types = [
        {"value": "verify", "label": "验证码"},
        {"value": "notify", "label": "通知消息"},
        {"value": "marketing", "label": "营销消息"},
        {"value": "warning", "label": "告警消息"},
        {"value": "system", "label": "系统消息"}
    ]
    return respModel.ok_resp_list(lst=types)


@template_route.get("/channels", summary="获取渠道类型列表",
                   dependencies=[Depends(check_permission("msgmanage:template:query"))])
async def get_channel_types():
    """获取渠道类型列表"""
    channels = [
        {"value": "system", "label": "站内消息"},
        {"value": "email", "label": "邮件"},
        {"value": "sms", "label": "短信"},
        {"value": "wechat", "label": "微信"},
        {"value": "dingtalk", "label": "钉钉"}
    ]
    return respModel.ok_resp_list(lst=channels)
