#  用来存在测试计划信息细节的方法

import os,json
from datetime import datetime
from app import application
from app import database
from sysmanage.model.HistoryInfoModel import HistoryInfo

class CaseCollection:
    @staticmethod
    def generateHistoryInfo(coll_type,case_collection_info,report_data_path,execute_uuid):
        # 返回当前路径的所有列表
        file_list = os.listdir(report_data_path)
        for file in file_list:
            #  确定当前列表的解为以：result.json
            if file.endswith("result.json"):
                with open(os.path.join(report_data_path, file), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if data:
                        print("当前的数据：", data)
                        # 获取到第一层名字为name，status,start，stop的值
                        name = data["name"]
                        status = data["status"]
                        start = data["start"]
                        stop = data["stop"]
                # 2. 读取到数据后，把数据写入到数据库，对应类名为CaseType
                with application.app_context():
                    # 3.保存前计算出此用例执行的毫秒数，用stop-start
                    duration = stop - start
                    # project_id 就是 project_id coll_id就是 data_id 然后本次的type为web  存入数据库 参考 copyData函数 id不用生成
                    case_types = {
                        "name": name,
                        "status": status,
                        "type": coll_type,  # 使用常量代替硬编码
                        "project_id": case_collection_info["project_id"],
                        "coll_id": case_collection_info["id"],
                        "duration": duration,
                        # 添加一个创建时间，为当前时间
                        "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'),
                        # 添加一个detail字段 为 execute_uuid
                        "detail": execute_uuid
                    }
                    database.session.add(HistoryInfo(**case_types))
                    database.session.commit()
