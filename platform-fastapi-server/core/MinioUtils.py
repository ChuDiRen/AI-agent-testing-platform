import os
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from .logger import get_logger

logger = get_logger(__name__)

class MinioUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式：确保Minio客户端只有一个实例"""
        if not cls._instance:
            cls._instance = super(MinioUtils, cls).__new__(cls)
        return cls._instance

    def __init__(self, endpoint=None, access_key=None, secret_key=None, secure=True):
        """
        初始化Minio客户端
        :param endpoint: Minio服务地址
        :param access_key: 访问密钥
        :param secret_key: 秘密密钥
        :param secure: 是否使用HTTPS
        """
        if not hasattr(self, 'client'):
            self.endpoint = endpoint or os.getenv('MINIO_ENDPOINT')
            self.access_key = access_key or os.getenv('MINIO_ACCESS_KEY')
            self.secret_key = secret_key or os.getenv('MINIO_SECRET_KEY')
            self.secure = secure
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )

    def upload_file(self, bucket_name, object_name, file_path=None, file_data=None, content_type='application/octet-stream'):
        """
        上传文件到 MinIO，支持文件路径或字节流
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称
        :param file_path: 本地文件路径（可选）
        :param file_data: 文件字节流（可选）
        :param content_type: MIME 类型
        """
        if file_path:
            self.client.fput_object(bucket_name, object_name, file_path, content_type=content_type)
        elif file_data:
            from io import BytesIO
            data_stream = BytesIO(file_data)
            self.client.put_object(bucket_name, object_name, data_stream, len(file_data), content_type=content_type)
        else:
            raise ValueError("必须提供 file_path 或 file_data")

    def download_file(self, bucket_name, object_name, file_path):
        """
        从Minio下载文件
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称（文件名）
        :param file_path: 下载后的本地文件路径
        :return: 成功返回True，失败抛出异常
        """
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            return True
        except S3Error as e:
            raise Exception(f"下载失败: {e}")

    # 通过文件名获得文件访问的url
    def getUrl(self,bucket_name,file_name):
        # 设置文件有效期 1天时间
        expires = timedelta(days=1)
        try:
            url = self.client.presigned_get_object(bucket_name, file_name, expires=expires)
            return url
        except Exception as err:
            logger.error(f"获取文件URL失败: {err}", exc_info=True)
            return None

# 测试当前工具类
# 注意：MinIO 通常有两个端口：
# 9000：用于 S3 API 操作（上传、下载、创建 bucket 等）
# 9001：MinIO 控制台（管理界面）
def MinioUtils_upload():
    endpoint='192.168.163.128:9000'
    access_key='admin'
    secret_key='12345678'
    secure=False

    file_path = os.path.join(os.path.dirname(__file__), "示例文件.txt")
    test_MinioUtils = MinioUtils(endpoint,access_key,secret_key,secure)
    test_MinioUtils.upload_file("aitest",'示例文件.txt',file_path)

    # 也可以用文件对象进行上传。
def MinioUtils_download():
    endpoint='192.168.163.128:9000'
    access_key='admin'
    secret_key='12345678'
    secure=False

    file_path = os.path.join(os.path.dirname(__file__), "示例文件_back.txt")
    test_MinioUtils = MinioUtils(endpoint,access_key,secret_key,secure)
    test_MinioUtils.download_file("aitest",'示例文件.txt',file_path)


# MinioUtils_upload()
# MinioUtils_download()