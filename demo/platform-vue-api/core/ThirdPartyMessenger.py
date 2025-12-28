from app import database, application
from core.resp_model import respModel
from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
from msgmanage.model.RobotConfigModel import RobotConfig

import logging
import base64
import hmac
import time
import urllib.parse
import requests
import hashlib, json


# 设置日志
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

class ThirdPartyMessenger:
    def __init__(self, platform=None, webhook_url=None, keywords=None):
        self.platform = platform
        self.webhook_url = webhook_url
        self.keywords = keywords

    # 辅助函数：发送企业微信消息
    def send_wechat_message(self,webhook_url, message, keywords=None):
        import requests
        import json

        # 构造企业微信消息格式
        payload = {
            "msgtype": "text",
            "text": {
                "content": message,
                "mentioned_list": keywords.split(",") if keywords else [],  # 将关键词转换为列表
                "mentioned_mobile_list": []  # 如果需要手机号提及，可以在这里添加
            }
        }

        response = requests.post(webhook_url, headers={"Content-Type": "application/json"},
                                 data=json.dumps(payload))

        if response.status_code == 200:
            print("消息发送成功:", response.json())
        else:
            print("消息发送失败:", response.json())

        return response.json()
    # 辅助函数：发送钉钉消息
    def send_dingtalk_message(self,webhook_url, message, keywords=None):
        # 判断keywords是不是空的，如果是空的，就不生成签名数据，直接发送
        if keywords:
            keywords = eval(keywords)
            secret = keywords["secret_key"]
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode('utf-8')
            string_to_sign = f'{timestamp}\n{secret}'
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            webhook_url += f"&timestamp={timestamp}&sign={sign}"

        headers = {'Content-Type': 'application/json'}
        payload = {
            "msgtype": "text",
            "text": {
                "content": message,
                "mentioned_list": ["@all"]  # 将关键词转换为列表
            }
        }
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            print("消息发送成功:", response.json())
        else:
            print("消息发送失败:", response.json())

        return response.json()
    # 辅助函数：发送飞书消息
    def send_feishu_message(self,webhook_url, message, keywords=None):
        # 实现飞书消息发送逻辑
        # 飞书发送 不需要管关键词，只需要处理sign 签名即可
        data = {}
        # 判断keywords是不是空的，如果是空的，就不生成签名数据，直接发送
        if keywords:
            # 如果不是空的，就获取sign的值 默认填写为 {"sign":"xxxx"}
            keywords = eval(keywords)
            secret = keywords["sign"]
            # 获取当前时间戳
            timestamp = int(time.time())
            # 拼接时间戳与 签名
            string_to_sign = '{}\n{}'.format(timestamp, secret)
            # 获取这个code
            hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
            # 对code进行base64处理
            sign = base64.b64encode(hmac_code).decode('utf-8')
            # 获取到内容后，将sign给到字典中
            data.update({"sign": sign})

        # 如果没有签名，这里就直接处理
        data.update({"msg_type": "text"})
        data.update({"content": {"text": message}})
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            webhook_url,
            headers=headers,
            data=json.dumps(data)
        )
        if response.status_code == 200:
            print("消息发送成功:", response.json())
        else:
            print("消息发送失败:", response.json())

        return response.json()

    def send_message(self, case_collection_info, coll_type, HistoryModelObj):
        """
        查询测试结果并发送机器人通知
        结合不同case_collection_info 和 HistoryModel进行操作
        """
        try:
            with application.app_context():
                # 1. 查询测试结果
                test_result = HistoryModelObj.query.filter_by(collection_info_id=case_collection_info["id"]).order_by(
                    HistoryModelObj.create_time.desc()).first()
                if not test_result:
                    return respModel.ok_resp(msg="没有找到对应的测试结果")

                # 2. 获取机器人配置
                robot_configs = RobotMsgConfig.query.filter_by(coll_id=case_collection_info["id"], is_enabled=1,
                                                               coll_type=coll_type).all()
                if not robot_configs:
                    return respModel.ok_resp(msg="没有找到启用的机器人配置")

                # 4. 获取机器人详细配置
                for config in robot_configs:
                    robot_config = RobotConfig.query.filter_by(id=config.robot_id).first()
                    if not robot_config:
                        continue

                    # 5. 替换消息模板中的变量
                    message_template = robot_config.message_template
                    message = message_template.replace("{{coll_name}}", case_collection_info.get("collection_name"))
                    message = message.replace("{{status}}", test_result.history_desc)

                    # 结合路径不一样，对应的地址不一样：
                    if coll_type == "web":
                        report_url = f"{application.config['REPORT_WEB_URL']}/{test_result.history_detail}/index.html"
                    elif coll_type == "app":
                        report_url = f"{application.config['REPORT_APP_URL']}/{test_result.history_detail}/index.html"
                    elif coll_type == "api":
                        report_url = f"{application.config['REPORT_API_URL']}/{test_result.history_detail}/index.html"
                    else:
                        raise Exception("不支持的用例类型")

                    message = message.replace("{{report_url}}", report_url)

                    # 6. 发送机器人通知
                    if robot_config.robot_type == "1" or robot_config.robot_type == 1:  # 企业微信
                        print("---发送企业微信消息---")
                        self.send_wechat_message(robot_config.webhook_url, message,robot_config.keywords)
                    elif robot_config.robot_type == "2" or robot_config.robot_type == 2:  # 钉钉
                        print("---发送钉钉消息---")
                        self.send_dingtalk_message(robot_config.webhook_url, message,robot_config.keywords)
                    elif robot_config.robot_type == "3" or robot_config.robot_type == 3:  # 飞书
                        print("---发送飞书消息---")
                        self.send_feishu_message(robot_config.webhook_url,  message,robot_config.keywords)
                    else:
                        return respModel.error_resp(msg="未知的机器人类型")

        except Exception as e:
            print(e)
            return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

ThirdPartyMessengerObj = ThirdPartyMessenger()


# 测试用例：验证企业微信消息发送功能

if __name__ == '__main__':
    # 你的机器人Webhook地址
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ee875643-a984-40cb-9dd1-366fa016bf9e"
    message = "这是一条来自Python脚本的消息"
    result = ThirdPartyMessengerObj.send_wechat_message(webhook_url, message)

    # 你的机器人Webhook地址
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=857e5a8cb8a950f99a52bdc932050a78f2fe8a7f186fc9ebce121c4244a5cc5e"
    secret = '{"secret_key":"SEC280c3f6ba96f49aa1e11f662205eb1cc25a43dafa991d2fdeb8d94ad583495dc"}'
    message = "这是一条来自Python脚本的钉钉消息"
    result = ThirdPartyMessengerObj.send_dingtalk_message(webhook_url, message,secret)


    # 你的机器人Webhook地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/f53b1f37-754f-4074-bb20-df8420a3eb8b"
    message = "这是一条来自Python脚本的钉钉消息"
    result = ThirdPartyMessengerObj.send_feishu_message(webhook_url,message)


