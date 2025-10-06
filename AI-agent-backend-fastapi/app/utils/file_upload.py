"""文件上传工具"""
import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path


# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword",
                          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

# 文件大小限制（字节）
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# upload_type 到文件类型的映射
TYPE_MAPPING = {
    "avatars": ALLOWED_IMAGE_TYPES,  # 头像只允许图片
    "image": ALLOWED_IMAGE_TYPES,  # 图片类型
    "files": ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES,  # 通用文件允许图片和文档
    "document": ALLOWED_DOCUMENT_TYPES  # 文档类型
}

# upload_type 到文件大小限制的映射
SIZE_MAPPING = {
    "avatars": MAX_IMAGE_SIZE,  # 头像限制5MB
    "image": MAX_IMAGE_SIZE,  # 图片限制5MB
    "files": MAX_DOCUMENT_SIZE,  # 通用文件限制10MB
    "document": MAX_DOCUMENT_SIZE  # 文档限制10MB
}

# 上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_upload_file(
    file: UploadFile,
    upload_type: str = "image",
    allowed_types: Optional[set] = None,
    max_size: Optional[int] = None
) -> str:
    """保存上传的文件
    
    Args:
        file: 上传的文件对象
        upload_type: 上传类型（image/document）
        allowed_types: 允许的文件类型
        max_size: 最大文件大小
        
    Returns:
        str: 文件保存路径
    """
    # 设置默认值（使用映射表）
    if allowed_types is None:
        allowed_types = TYPE_MAPPING.get(upload_type, ALLOWED_IMAGE_TYPES)

    if max_size is None:
        max_size = SIZE_MAPPING.get(upload_type, MAX_IMAGE_SIZE)
    
    # 验证文件类型
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}"
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 验证文件大小
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制: {max_size / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 创建类型目录
    type_dir = UPLOAD_DIR / upload_type
    type_dir.mkdir(exist_ok=True)
    
    # 保存文件
    file_path = type_dir / unique_filename
    with open(file_path, "wb") as f:
        f.write(contents)

    # 返回URL路径（以/开头，符合Web标准）
    return "/" + str(file_path).replace("\\", "/")


async def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False

