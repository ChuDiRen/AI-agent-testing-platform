from datetime import datetime

from apitest.service.ApiMetaService import MetaService
from config.dev_settings import settings
from core.MinioUtils import MinioUtils
from core.database import get_session
from core.dependencies import check_permission
from core.dependencies import get_minio_client
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form
from sqlmodel import Session

from ..schemas.ApiMetaSchema import ApiMetaQuery, ApiMetaUpdate

module_name = "ApiMeta" # 模块名称
module_route = APIRouter(prefix=f"/{module_name}", tags=["API元数据管理"])
logger = get_logger(__name__)

@module_route.get("/queryAll", summary="查询所有元数据", dependencies=[Depends(check_permission("apitest:meta:query"))])
async def queryAll(session: Session = Depends(get_session)):
    """查询所有文件元数据"""
    try:
        service = MetaService(session)
        datas = service.query_all_file_meta()
        logger.info("查询所有文件元数据成功")
        return respModel.ok_resp_list(lst=datas, msg="查询成功")
    except Exception as e:
        logger.error(f"查询所有元数据失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/queryByPage", summary="分页查询元数据", dependencies=[Depends(check_permission("apitest:meta:query"))])
async def queryByPage(query: ApiMetaQuery, session: Session = Depends(get_session)):
    """分页查询文件元数据"""
    try:
        service = MetaService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            mate_name=query.mate_name,
            object_url=query.object_url,
            file_type=query.file_type,
            project_id=query.project_id
        )
        logger.info(f"分页查询文件元数据成功，共{total}条记录")
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询元数据失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询元数据", dependencies=[Depends(check_permission("apitest:meta:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询文件元数据"""
    try:
        service = MetaService(session)
        data = service.get_by_id(id)
        if data:
            logger.info(f"查询文件元数据成功: ID={id}")
            return respModel.ok_resp(obj=data)
        else:
            logger.warning(f"查询文件元数据不存在: ID={id}")
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"查询元数据失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="上传文件并新增元数据", dependencies=[Depends(check_permission("apitest:meta:add"))])
async def insert(
    file: UploadFile = File(...),
    project_id: int = Form(0),
    session: Session = Depends(get_session),
    minio_client: MinioUtils = Depends(get_minio_client)
):
    """上传文件并创建文件元数据"""
    try:
        if not file:
            logger.error("文件上传失败: 未接收到文件")
            return respModel.error_resp(msg="未接收到文件")

        file_name = file.filename
        file_data = await file.read()

        # 上传文件到MinIO
        minio_client.upload_file("apitest", file_name, file_data=file_data)
        logger.info(f"文件上传到MinIO成功: {file_name}")

        # 创建文件元数据
        service = MetaService(session)
        data = service.create_file_meta(
            project_id=project_id,
            mate_name=file_name,
            object_url=f"/apitest/{file_name}",
            file_type=file.content_type
        )
        logger.info(f"文件元数据创建成功: ID={data.id}, 文件名={file_name}")
        return respModel.ok_resp(msg="文件上传成功", dic_t={"id": data.id})
    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"文件上传失败:{e}")

@module_route.put("/update", summary="更新元数据", dependencies=[Depends(check_permission("apitest:meta:edit"))])
async def update(meta: ApiMetaUpdate, session: Session = Depends(get_session)):
    """更新文件元数据"""
    try:
        service = MetaService(session)
        update_data = meta.model_dump(exclude_unset=True, exclude={'id'})
        success = service.update_file_meta(meta.id, update_data)
        if success:
            logger.info(f"文件元数据更新成功: ID={meta.id}")
            return respModel.ok_resp(msg="修改成功")
        else:
            logger.warning(f"文件元数据不存在: ID={meta.id}")
            return respModel.error_resp(msg="元数据不存在")
    except Exception as e:
        logger.error(f"更新元数据失败: ID={meta.id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除元数据", dependencies=[Depends(check_permission("apitest:meta:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除文件元数据"""
    try:
        service = MetaService(session)
        success = service.delete(id)
        if success:
            logger.info(f"文件元数据删除成功: ID={id}")
            return respModel.ok_resp(msg="删除成功")
        else:
            logger.warning(f"文件元数据不存在: ID={id}")
            return respModel.error_resp(msg="元数据不存在")
    except Exception as e:
        logger.error(f"删除元数据失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.get("/downloadFile", summary="获取文件下载地址", dependencies=[Depends(check_permission("apitest:meta:download"))])
async def downloadFile(id: int = Query(...), session: Session = Depends(get_session)):
    """获取文件下载地址"""
    try:
        service = MetaService(session)
        data = service.get_by_id(id)
        if not data:
            logger.warning(f"文件不存在: ID={id}")
            return respModel.error_resp(msg="文件不存在")

        object_url = data.object_url
        if not object_url:
            logger.warning(f"文件URL为空: ID={id}")
            return respModel.error_resp(msg="获取下载地址失败，文件不存在")

        download_url = f"{settings.MINIO_CLIENT_URL}{object_url}"
        logger.info(f"获取文件下载地址成功: ID={id}, URL={download_url}")
        return respModel.ok_resp(msg="获取到下载地址", dic_t={"downloadUrl": download_url})
    except Exception as e:
        logger.error(f"获取下载地址失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,获取下载地址失败：{e}")
