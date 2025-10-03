"""文件上传路由"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.file_upload import save_upload_file, delete_file

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post("/avatar", response_model=APIResponse[dict])
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[dict]:
    """上传用户头像"""
    # 保存文件
    file_path = await save_upload_file(file, upload_type="avatars")
    
    # 删除旧头像
    if current_user.avatar:
        await delete_file(current_user.avatar)
    
    # 更新用户头像
    current_user.avatar = file_path
    await db.commit()
    await db.refresh(current_user)
    
    return APIResponse(
        message="头像上传成功",
        data={
            "avatar_url": file_path,
            "filename": file.filename
        }
    )


@router.post("/file", response_model=APIResponse[dict])
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """上传通用文件"""
    file_path = await save_upload_file(file, upload_type="files")
    
    return APIResponse(
        message="文件上传成功",
        data={
            "file_url": file_path,
            "filename": file.filename,
            "content_type": file.content_type
        }
    )


@router.delete("/file", response_model=APIResponse[None])
async def delete_uploaded_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除上传的文件"""
    success = await delete_file(file_path)
    
    if not success:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return APIResponse(message="文件删除成功")

