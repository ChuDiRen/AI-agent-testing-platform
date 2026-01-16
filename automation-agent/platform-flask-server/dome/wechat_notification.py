import requests
import json

def send_wechat_message(webhook_url,  message, keywords =None):
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

# 使用示例
if __name__ == '__main__':
    # 你的机器人Webhook地址
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ee875643-a984-40cb-9dd1-366fa016bf9e"
    message = "这是一条来自Python脚本的消息"
    result = send_wechat_message(webhook_url, message)
