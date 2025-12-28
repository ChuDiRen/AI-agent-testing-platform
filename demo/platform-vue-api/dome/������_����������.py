import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse


# 辅助函数：发送钉钉消息
def send_dingtalk_message(webhook_url, message, keywords=None):
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


if __name__ == '__main__':
    # 使用示例
    # 你的机器人Webhook地址
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=857e5a8cb8a950f99a52bdc932050a78f2fe8a7f186fc9ebce121c4244a5cc5e"
    secret = '{"secret_key":"SEC280c3f6ba96f49aa1e11f662205eb1cc25a43dafa991d2fdeb8d94ad583495dc"}'
    message = "这是一条来自Python脚本的钉钉消息"
    result = send_dingtalk_message(webhook_url, message,secret)
