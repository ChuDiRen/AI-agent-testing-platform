from datetime import datetime

from config.dev_settings import settings
from core.MinioUtils import MinioUtils
from core.database import get_session
from core.dependencies import check_permission
from core.dependencies import get_minio_client
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form
from sqlmodel import Session, select

from ..model.ApiMetaModel import ApiMeta
from ..schemas.api_meta_schema import ApiMetaQuery, ApiMetaUpdate

module_name = "ApiMeta" # 模块名称
module_model = ApiMeta
module_route = APIRouter(prefix=f"/{module_name}", tags=["API元数据管理"])
logger = get_logger(__name__)

@module_route.get("/queryAll", summary="查询所有元数据", dependencies=[Depends(check_permission("apitest:meta:query"))]) # 查询所有元数据
async def queryAll(session: Session = Depends(get_session)):
    statement = select(module_model)
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")

@module_route.post("/queryByPage", summary="分页查询元数据", dependencies=[Depends(check_permission("apitest:meta:query"))]) # 分页查询元数据
async def queryByPage(query: ApiMetaQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        # 添加元数据名称模糊搜索条件
        if query.mate_name:
            statement = statement.where(module_model.mate_name.like(f'%{query.mate_name}%'))
        # 添加对象URL模糊搜索条件
        if query.object_url:
            statement = statement.where(module_model.object_url.like(f'%{query.object_url}%'))
        # 添加文件类型模糊搜索条件
        if query.file_type:
            statement = statement.where(module_model.file_type.like(f'%{query.file_type}%'))
        # 添加项目筛选条件
        if query.project_id and query.project_id > 0:
            statement = statement.where(module_model.project_id == query.project_id)
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        count_statement = select(module_model)
        if query.mate_name:
            count_statement = count_statement.where(module_model.mate_name.like(f'%{query.mate_name}%'))
        if query.object_url:
            count_statement = count_statement.where(module_model.object_url.like(f'%{query.object_url}%'))
        if query.file_type:
            count_statement = count_statement.where(module_model.file_type.like(f'%{query.file_type}%'))
        if query.project_id and query.project_id > 0:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询元数据", dependencies=[Depends(check_permission("apitest:meta:query"))]) # 根据ID查询元数据
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="上传文件并新增元数据", dependencies=[Depends(check_permission("apitest:meta:add"))]) # 上传文件并新增元数据
async def insert(
    file: UploadFile = File(...),
    project_id: int = Form(0),
    session: Session = Depends(get_session),
    minio_client: MinioUtils = Depends(get_minio_client)
):
    try:
        if not file:
            return respModel.error_resp(msg="未接收到文件")
        file_name = file.filename
        file_data = await file.read()
        # 上传文件到MinIO
        minio_client.upload_file("apitest", file_name, file_data=file_data)
        # 构造文件元数据
        file_metadata = {
            "project_id": project_id,
            "mate_name": file_name,
            "object_url": f"/apitest/{file_name}",
            "file_type": file.content_type,
            "create_time": datetime.now()
        }
        data = module_model(**file_metadata)
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="文件上传成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"文件上传失败:{e}")

@module_route.put("/update", summary="更新元数据", dependencies=[Depends(check_permission("apitest:meta:edit"))]) # 更新元数据
async def update(meta: ApiMetaUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == meta.id)
        db_data = session.exec(statement).first()
        if db_data:
            update_data = meta.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_data, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="元数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除元数据", dependencies=[Depends(check_permission("apitest:meta:delete"))]) # 删除元数据
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="元数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.get("/downloadFile", summary="获取文件下载地址", dependencies=[Depends(check_permission("apitest:meta:download"))]) # 获取文件下载地址
async def downloadFile(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if not data:
            return respModel.error_resp(msg="文件不存在")
        object_url = data.object_url
        if not object_url:
            return respModel.error_resp(msg="获取下载地址失败，文件不存在")
        download_url = f"{settings.MINIO_CLIENT_URL}{object_url}"
        return respModel.ok_resp(msg="获取到下载地址", dic_t={"downloadUrl": download_url})
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
