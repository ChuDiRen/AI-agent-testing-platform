# 文件上传与 OSS 管理技能

## 触发条件
- 关键词：文件上传、OSS、对象存储、图片上传、文件管理、MinIO
- 场景：当用户需要处理文件上传和存储时

## 核心规范

### 规范1：本项目文件存储技术栈

- **对象存储**: MinIO
- **客户端**: `core/minio_client.py`
- **工具类**: `core/MinioUtils.py`
- **文件服务**: `core/FileService.py`

### 规范2：MinIO 客户端配置

```python
# core/minio_client.py
from minio import Minio
from config.dev_settings import settings

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)
```

### 规范3：MinIO 工具类

```python
# core/MinioUtils.py
from minio import Minio
from datetime import timedelta
import uuid
import os

class MinioUtils:
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """确保存储桶存在"""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
    
    def upload_file(self, file_data: bytes, file_name: str, content_type: str = None):
        """上传文件"""
        # 生成唯一文件名
        ext = os.path.splitext(file_name)[1]
        object_name = f"{uuid.uuid4().hex}{ext}"
        
        from io import BytesIO
        file_stream = BytesIO(file_data)
        
        self.client.put_object(
            self.bucket_name,
            object_name,
            file_stream,
            length=len(file_data),
            content_type=content_type
        )
        
        return object_name
    
    def get_presigned_url(self, object_name: str, expires: int = 3600):
        """获取预签名 URL"""
        return self.client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=timedelta(seconds=expires)
        )
    
    def delete_file(self, object_name: str):
        """删除文件"""
        self.client.remove_object(self.bucket_name, object_name)
    
    def list_files(self, prefix: str = ""):
        """列出文件"""
        objects = self.client.list_objects(self.bucket_name, prefix=prefix)
        return [obj.object_name for obj in objects]
```

### 规范4：文件上传 API

```python
# 文件上传接口
from fastapi import APIRouter, UploadFile, File, Depends
from core.MinioUtils import MinioUtils
from core.minio_client import minio_client

router = APIRouter(prefix="/file", tags=["文件管理"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 读取文件内容
        content = await file.read()
        
        # 上传到 MinIO
        minio_utils = MinioUtils(minio_client, "uploads")
        object_name = minio_utils.upload_file(
            content,
            file.filename,
            file.content_type
        )
        
        # 获取访问 URL
        url = minio_utils.get_presigned_url(object_name)
        
        return respModel.ok_resp(obj={
            "object_name": object_name,
            "url": url,
            "filename": file.filename,
            "size": len(content)
        })
    except Exception as e:
        return respModel.error_resp(f"上传失败: {e}")

@router.delete("/delete")
async def delete_file(object_name: str):
    """删除文件"""
    try:
        minio_utils = MinioUtils(minio_client, "uploads")
        minio_utils.delete_file(object_name)
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        return respModel.error_resp(f"删除失败: {e}")
```

### 规范5：前端文件上传

```vue
<template>
  <el-upload
    :action="uploadUrl"
    :headers="uploadHeaders"
    :on-success="handleSuccess"
    :on-error="handleError"
    :before-upload="beforeUpload"
    :limit="1"
  >
    <el-button type="primary">点击上传</el-button>
    <template #tip>
      <div class="el-upload__tip">只能上传 jpg/png 文件，且不超过 5MB</div>
    </template>
  </el-upload>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const uploadUrl = '/api/file/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const beforeUpload = (file) => {
  const isImage = ['image/jpeg', 'image/png'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG 格式的图片')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }
  return true
}

const handleSuccess = (response) => {
  if (response.code === 0) {
    ElMessage.success('上传成功')
    emit('success', response.data)
  } else {
    ElMessage.error(response.msg)
  }
}

const handleError = () => {
  ElMessage.error('上传失败')
}
</script>
```

### 规范6：文件类型限制

```python
# 允许的文件类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile):
    """验证文件"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(f"不支持的文件类型: {ext}")
    
    # 检查文件大小（需要先读取）
    content = file.file.read()
    file.file.seek(0)  # 重置文件指针
    
    if len(content) > MAX_FILE_SIZE:
        raise ValidationException(f"文件大小超过限制: {MAX_FILE_SIZE / 1024 / 1024}MB")
    
    return True
```

## 禁止事项
- ❌ 不验证文件类型和大小
- ❌ 使用原始文件名存储（安全风险）
- ❌ 不处理上传失败的情况
- ❌ 硬编码 MinIO 配置

## 检查清单
- [ ] 是否验证文件类型
- [ ] 是否限制文件大小
- [ ] 是否使用唯一文件名
- [ ] 是否有错误处理
