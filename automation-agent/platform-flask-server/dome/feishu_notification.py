import base64
import hmac
import time
import requests
import hashlib, json
# 辅助函数：发送飞书消息
def send_feishu_message(webhook_url, message, keywords=None):
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


if __name__ == '__main__':
    # 使用示例
    # 你的机器人Webhook地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/f53b1f37-754f-4074-bb20-df8420a3eb8b"
    message = "这是一条来自Python脚本的钉钉消息"
    result = send_feishu_message(webhook_url,message)
