from minio import Minio
import os

# MinIO 配置
MINIO_CLIENT_URL = "192.168.1.106:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
bucket_name = "apitest"

# 初始化客户端
client = Minio(
    MINIO_CLIENT_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# 构建文件路径（建议使用相对路径）
file_path = os.path.join(os.path.dirname(__file__), "示例文件.txt")

# 上传文件
client.fput_object(
    bucket_name=bucket_name,
    object_name="示例文件.txt",  # 可自定义上传后的文件名
    file_path=file_path
)

print("文件上传成功")
# 下载文件
#  直接访问：http://192.168.1.106:9000/apitest/%E7%A4%BA%E4%BE%8B%E6%96%87%E4%BB%B6.txt

