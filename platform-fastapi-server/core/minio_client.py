from minio import Minio
from typing import BinaryIO

from config.dev_settings import settings


class MinioClientWrapper:
    """简单封装 MinIO 客户端,用于插件 ZIP 上传等操作"""

    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        # 默认桶名,可根据需要调整
        self.bucket = "ai-agent-plugins"
        # 确保桶存在
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_plugin_zip(self, data: BinaryIO, object_name: str, length: int) -> str:
        """上传插件 ZIP 到 MinIO,返回对象路径"""
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=data,
            length=length,
            content_type="application/zip",
        )
        return f"{self.bucket}/{object_name}"


minio_client = MinioClientWrapper()
