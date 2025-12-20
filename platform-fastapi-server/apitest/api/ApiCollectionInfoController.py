from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..service.api_collection_info_service import ApiCollectionInfoService
from ..schemas.api_collection_schema import (
    ApiCollectionInfoQuery, ApiCollectionInfoCreate, ApiCollectionInfoUpdate,
    ApiCollectionDetailCreate, BatchAddCasesRequest, UpdateDdtDataRequest,
    PlanRobotCreate, PlanRobotUpdate
)

logger = get_logger(__name__)

module_name = "ApiCollectionInfo"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试计划管理"])

# ==================== 测试计划CRUD ====================

@module_route.post("/queryByPage", summary="分页查询测试计划", dependencies=[Depends(check_permission("apitest:collection:query"))])
async def queryByPage(query: ApiCollectionInfoQuery, session: Session = Depends(get_session)):
    """分页查询测试计划"""
    try:
        service = ApiCollectionInfoService(session)
        result_list, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            project_id=query.project_id,
            plan_name=query.plan_name
        )
        return respModel.ok_resp_list(lst=result_list, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询测试计划", dependencies=[Depends(check_permission("apitest:collection:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询测试计划（含关联用例）"""
    try:
        service = ApiCollectionInfoService(session)
        result = service.get_by_id(id)
        if not result:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增测试计划", dependencies=[Depends(check_permission("apitest:collection:add"))])
async def insert(data: ApiCollectionInfoCreate, session: Session = Depends(get_session)):
    """新增测试计划"""
    try:
        service = ApiCollectionInfoService(session)
        service.create(
            project_id=data.project_id,
            plan_name=data.plan_name,
            plan_desc=data.plan_desc
        )
        return respModel.ok_resp_text(msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update", summary="更新测试计划", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def update(data: ApiCollectionInfoUpdate, session: Session = Depends(get_session)):
    """更新测试计划"""
    try:
        service = ApiCollectionInfoService(session)
        update_data = data.model_dump(exclude_unset=True, exclude={'id'})
        updated = service.update(data.id, update_data)
        if not updated:
            return respModel.error_resp("测试计划不存在")
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除测试计划", dependencies=[Depends(check_permission("apitest:collection:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除测试计划"""
    try:
        service = ApiCollectionInfoService(session)
        if service.delete(id):
            return respModel.ok_resp_text(msg="删除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# ==================== 用例关联管理 ====================

@module_route.post("/addCase", summary="添加用例到测试计划", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def addCase(data: ApiCollectionDetailCreate, session: Session = Depends(get_session)):
    """添加用例到计划"""
    try:
        service = ApiCollectionInfoService(session)
        result = service.add_case(
            plan_id=data.collection_info_id,
            case_info_id=data.case_info_id,
            run_order=data.run_order,
            ddt_data=data.ddt_data
        )
        if not result:
            return respModel.error_resp("该用例已添加到计划中")
        return respModel.ok_resp_text(msg="添加成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/batchAddCases", summary="批量添加用例到测试计划", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def batchAddCases(data: BatchAddCasesRequest, session: Session = Depends(get_session)):
    """批量添加用例到计划，自动提取数据驱动配置"""
    try:
        service = ApiCollectionInfoService(session)
        added_count = service.batch_add_cases(plan_id=data.plan_id, case_ids=data.case_ids)
        return respModel.ok_resp_text(msg=f"成功添加{added_count}个用例")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.delete("/removeCase", summary="从测试计划移除用例", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def removeCase(plan_case_id: int = Query(...), session: Session = Depends(get_session)):
    """从计划中移除用例"""
    try:
        service = ApiCollectionInfoService(session)
        if service.remove_case(plan_case_id):
            return respModel.ok_resp_text(msg="移除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/updateDdtData", summary="更新测试计划的数据驱动信息", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def updateDdtData(data: UpdateDdtDataRequest, session: Session = Depends(get_session)):
    """更新用例的数据驱动数据"""
    try:
        service = ApiCollectionInfoService(session)
        updated = service.update_ddt_data(data.plan_case_id, data.ddt_data)
        if not updated:
            return respModel.error_resp("关联数据不存在")
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# ==================== 复制测试计划 ====================

@module_route.post("/copy", summary="复制测试计划", dependencies=[Depends(check_permission("apitest:collection:add"))])
async def copyPlan(id: int = Query(..., description="要复制的计划ID"), session: Session = Depends(get_session)):
    """
    复制测试计划及其关联的用例
    - 复制计划基本信息（名称添加“_副本”后缀）
    - 复制所有关联的用例配置（包括DDT数据）
    """
    try:
        service = ApiCollectionInfoService(session)
        result = service.copy_plan(id)
        if not result:
            return respModel.error_resp("测试计划不存在")
        return respModel.ok_resp(
            obj=result,
            msg=f"复制成功，新计划ID: {result['new_plan_id']}，复制了{result['copied_cases']}个用例"
        )
    except Exception as e:
        session.rollback()
        logger.error(f"复制测试计划失败: {e}", exc_info=True)
        return respModel.error_resp(f"复制失败: {e}")

# ==================== Jenkins配置接口 ====================

@module_route.get("/getJenkinsConfig", summary="获取Jenkins配置信息")
async def getJenkinsConfig(id: int = Query(..., description="测试计划ID"), session: Session = Depends(get_session)):
    """
    获取测试计划的Jenkins CI/CD集成配置信息
    返回可用于Jenkins Pipeline的配置
    """
    try:
        service = ApiCollectionInfoService(session)
        jenkins_config = service.get_jenkins_config(id)
        if not jenkins_config:
            return respModel.error_resp("测试计划不存在")
        return respModel.ok_resp(obj=jenkins_config, msg="获取成功")
    except Exception as e:
        logger.error(f"获取Jenkins配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")

# ==================== 批量执行测试计划（已废弃，请使用 /ApiInfoCase/executeCase 接口） ====================
# 注意：executePlan 接口已合并到 /ApiInfoCase/executeCase 接口
# 前端调用 executeCase 时传入 plan_id 即可实现批量执行

# ==================== 机器人关联管理 ====================

@module_route.get("/getRobots", summary="获取测试计划关联的机器人", dependencies=[Depends(check_permission("apitest:collection:query"))])
async def getRobots(plan_id: int = Query(..., description="测试计划ID"), session: Session = Depends(get_session)):
    """获取测试计划关联的所有机器人配置"""
    try:
        service = ApiCollectionInfoService(session)
        result = service.get_robots(plan_id)
        return respModel.ok_resp_list(lst=result, msg="查询成功")
    except Exception as e:
        logger.error(f"获取计划机器人失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/addRobot", summary="为测试计划添加机器人通知", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def addRobot(data: PlanRobotCreate, session: Session = Depends(get_session)):
    """为测试计划添加机器人通知配置"""
    try:
        service = ApiCollectionInfoService(session)
        result = service.add_robot(
            plan_id=data.plan_id,
            robot_id=data.robot_id,
            is_enabled=data.is_enabled,
            notify_on_success=data.notify_on_success,
            notify_on_failure=data.notify_on_failure
        )
        if not result:
            return respModel.error_resp("该机器人已关联到此计划")
        return respModel.ok_resp_text(msg="添加成功")
    except Exception as e:
        session.rollback()
        logger.error(f"添加计划机器人失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.put("/updateRobot", summary="更新测试计划机器人配置", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def updateRobot(data: PlanRobotUpdate, session: Session = Depends(get_session)):
    """更新测试计划机器人通知配置"""
    try:
        service = ApiCollectionInfoService(session)
        update_data = data.model_dump(exclude_unset=True, exclude={'id'})
        updated = service.update_robot(data.id, update_data)
        if not updated:
            return respModel.error_resp("关联配置不存在")
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"更新计划机器人失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.delete("/removeRobot", summary="移除测试计划机器人关联", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def removeRobot(id: int = Query(..., description="关联ID"), session: Session = Depends(get_session)):
    """移除测试计划的机器人关联"""
    try:
        service = ApiCollectionInfoService(session)
        if service.remove_robot(id):
            return respModel.ok_resp_text(msg="移除成功")
        return respModel.error_resp("关联配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"移除计划机器人失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")

