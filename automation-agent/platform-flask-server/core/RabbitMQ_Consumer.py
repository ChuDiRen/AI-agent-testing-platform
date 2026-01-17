# 生成rabbitMQ的连接信息
import pika
from config.dev_settings import RABBITMQ_HOST, RABBITMQ_PORT, QUEUE_LIST, RABBITMQ_USER, RABBITMQ_PASSWORD
import threading, time

# 消费者
class RabbitMQManager:
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        # 打印当前线程信息
        print(f"当前线程: {threading.current_thread().name}")
        if not cls._instance:
            with cls._instance_lock:
                print(f"线程: {threading.current_thread().name} 拿到锁")
                if not cls._instance:
                    cls._instance = super(RabbitMQManager, cls).__new__(cls)
                    cls._instance._initialized = False
        print(f"线程: {threading.current_thread().name} 获得对象{cls._instance}")
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def start_workers(self):
        print("MQ初始化完成，准备启动消费者线程...")
        """ 根据 QUEUE_LIST 启动多个消费者线程 """
        for queue_name, thread_count in QUEUE_LIST:
            # print(f"\n正在启动 {thread_count} 个线程监听队列: {queue_name}")
            for i in range(thread_count):
                threading.Thread(
                    target=self.start_consumer,
                    args=(queue_name,),  # 可以传入 exchange 和 routing_key
                    daemon=True
                ).start()

    def start_consumer(self, routing_key):
        """
        启动一个消费者线程，监听指定的队列
        :param routing_key: 队列名
        """
        max_retries = 3  # 最大重试次数
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST,
                        port=RABBITMQ_PORT,
                        credentials=credentials,
                        connection_attempts=3,
                        retry_delay=2
                    )
                )
                channel = connection.channel()

                # 交换机的命名：{队列名}_exchange
                exchange = f"{routing_key}_exchange"

                # 第一行：声明交换机
                channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)
                # 第二行：声明队列
                channel.queue_declare(queue=routing_key)
                # 第三行：绑定队列到交换机-这样我们才知道消息投递到哪个队列
                channel.queue_bind(exchange=exchange, queue=routing_key, routing_key=routing_key)

                def on_message(ch, method, properties, body):
                    print(f"[x] 收到消息 来自于 {routing_key}: {body.decode()}")
                    # TODO 1 : 真正触发回调,拿到用例数据我们就可以就可以进行测试用例执行
                    self.excuteReport(body)  # 真正触发回调

                # 绑定回调函数
                channel.basic_consume(queue=routing_key, on_message_callback=on_message, auto_ack=True)

                # print(f"[x] Worker {threading.get_ident()} 开始监听队列: {routing_key}")
                channel.start_consuming()  # 取消注释并放在这里
                
            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f" RabbitMQ 连接失败，已达到最大重试次数 ({max_retries})，队列 {routing_key} 停止监听")
                    return  # 停止重试
                print(f" RabbitMQ 连接失败，5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            except Exception as e:
                print(f" 消费者线程异常: {e}")
                return  # 其他异常直接退出

    def excuteReport(self,body):
        """
        执行用例生成历史记录 写入到rds当中
        """
        # TODO 0: 导入对应的包
        import json, os, subprocess
        from app import database, application
        from datetime import datetime

        from apitest.model.ApiHistoryModel import ApiHistoryModel

        # TODO 1: 获取用例数据
        dict_data = json.loads(body.decode('utf-8'))
        coll_type = dict_data.get("coll_type") # 用例类型
        execute_uuid = dict_data.get("execute_uuid") # 用例存放的文件夹
        case_collection_info = json.loads(dict_data.get("case_collection_info")) # 用例集合信息

        # TODO 2: 获取对应的路径
        key_words_dir = application.config['KEY_WORDS_DIR']  # 关键字目录
        run_tmp_dir = dict_data.get("run_tmp_dir")
        report_data_path = dict_data.get("report_data_path")
        report_html_path = dict_data.get("report_html_path")

        # TODO 3: 扩展: 将本次任务加入redis中 ，进入MQ后，表示本任务正在等待
        import redis
        from config.dev_settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

        data_id = case_collection_info["id"]
        key = f"task:{coll_type}_{data_id}_{execute_uuid}"
        with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD) as r:
            r.hset(key, "name", case_collection_info["collection_name"])
            r.hset(key, "execute_uuid", execute_uuid)
            r.hset(key, "type", coll_type)
            r.hset(key, "status", "执行中")

        # TODO 4: 结合用例类型不一样执行的命令不一样
        if coll_type == "web":
           pass
        elif coll_type == "app":
            pass
        elif coll_type == "api":
            cmd = "huace-apirun"
            HistoryModelObj = ApiHistoryModel  # 报告历史记录对象
        else:
            raise Exception("不支持的用例类型")

        # TODO 5:  执行命令
        # 1. 执行测试
        remote_command = f"{cmd} --cases={run_tmp_dir} --keyDir={key_words_dir} -sv --capture=tee-sys --alluredir={report_data_path} "
        command_output = subprocess.check_output(remote_command, shell=True, universal_newlines=True,
                                                 encoding='utf-8')
        history_desc = command_output.split("\n")[-2].replace("=", "")  # 截取最后一段
        # 2. 生成html测试报告
        os.system(f"allure generate {report_data_path} -c -o {report_html_path}")  # 等于你在命令行里面执行 allure
        print("当前的报告路径", report_html_path + "/index.html")
        # 3. 删除一些临时文件，保留html测试报告即可
        # shutil.rmtree(run_tmp_dir)  # 测试套件临时yaml文件 collection_dir
        # shutil.rmtree(report_data_path)  # 测试工具执行后的测试结果数据

        # 4.把对应的记录存放到历史记录表当中
        # 保存测试报告
        with application.app_context():
            report = HistoryModelObj(id=0,
                                     collection_info_id=case_collection_info["id"],
                                     history_desc=history_desc,
                                     history_detail=execute_uuid,
                                     create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
            database.session.add(report)
            database.session.commit()

       #  扩展- 把对应的计划的记录写入到用例的记录当中去
        from  core.CaseCollection import CaseCollection
        CaseCollection.generateHistoryInfo(coll_type, case_collection_info, report_data_path, execute_uuid)

       #  5.redis 执行完成
        with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD) as r:
            r.hset(key, "name", case_collection_info["collection_name"])
            r.hset(key, "execute_uuid", execute_uuid)
            r.hset(key, "type", coll_type)
            r.hset(key, "status", "执行完成")

            # 设置过期时间（单位：秒）
            r.expire(key, 60)  # 1分钟后过期

      #  6. 发送机器人消息
        from core.ThirdPartyMessenger import ThirdPartyMessengerObj
        ThirdPartyMessengerObj.send_message(case_collection_info, coll_type, HistoryModelObj)




if __name__ == '__main__':
    RabbitMQManager().start_workers()
    time.sleep(1000000)