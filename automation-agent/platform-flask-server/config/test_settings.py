# 测试环境配置

# 注意，这里的常量名是固定写法 -- 前缀://用户名:密码@数据库地址:端口号/数据库名?charset=utf8
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin123456@192.168.111.128:3306/testdb?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 打印sql语句
SQLALCHEMY_ECHO = True
# Token密钥
SECRET_KEY = "1234567812345678"

#自动化的路径
KEY_WORDS_DIR = r"/keyswords" # 关键字生成的文件夹
CASES_ROOT_DIR = r"/yamls" # 测试用例生成的文件夹
REPORT_ROOT_DIR = r"/report"   # 用例报告文件夹

# 测试报告存放的路径
REPORT_API_URL = r"http://127.0.0.1:5000/ApiReportViewer"   # 接口用例报告文件夹

# rabbitMQ 配置
RABBITMQ_HOST = "192.168.111.128"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "admin"
RABBITMQ_PASSWORD = "admin123456"
QUEUE_LIST = [("web_queue", 3), ("app_queue", 3), ("api_queue", 6)] # 用于配置不同的测试队列的数量

#redis配置
REDIS_HOST = "192.168.111.128"
REDIS_PORT = 6379
REDIS_DB = 1 # 主要项目做隔离，一个项目就好了，微服务拆分，一个项目一个数据库
REDIS_PASSWORD = "admin123456"