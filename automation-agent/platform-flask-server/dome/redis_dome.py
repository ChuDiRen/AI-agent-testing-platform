import redis

# redis配置
REDIS_HOST = "192.168.1.120"
REDIS_PORT = 6379
REDIS_DB = 1  # 主要项目做隔离，一个项目就好了，微服务拆分，一个项目一个数据库
REDIS_PASSWORD = None

with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD) as r:
    coll_type = "api"
    data_id = 2
    collection_name = "登录测试用例"
    key = f"task:{coll_type}_{data_id}"

    # 方法一：以列表的方式进行存储
    # r.lpush(key, "执行成功")

    # 方法二：以哈希存储的方式
    r.hset(key, "name", collection_name)
    r.hset(key, "type", coll_type)
    r.hset(key, "status", "执行成功")
