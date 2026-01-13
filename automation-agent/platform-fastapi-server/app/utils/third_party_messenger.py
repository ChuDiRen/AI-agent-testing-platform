"""
第三方消息通知工具
从 Flask 迁移到 FastAPI - 支持企业微信、钉钉、飞书
"""
import logging
import base64
import hmac
import hashlib
import time
import urllib.parse
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

# 设置日志
logger = logging.getLogger(__name__)


class ThirdPartyMessenger:
    """第三方消息通知工具类"""
    
    def __init__(self, platform: str = None, webhook_url: str = None, keywords: str = None):
        """
        初始化消息通知工具
        
        Args:
            platform: 平台类型
            webhook_url: Webhook URL
            keywords: 关键词配置
        """
        self.platform = platform or settings.DEFAULT_PLATFORM if hasattr(settings, 'DEFAULT_PLATFORM') else None
        self.webhook_url = webhook_url
        self.keywords = keywords
    
    async def send_wechat_message(
        self,
        message: str,
        keywords: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送企业微信消息
        
        Args:
            message: 消息内容
            keywords: 关键词（可选）
        
        Returns:
            Dict: 响应结果
        """
        try:
            # 构造企业微信消息格式
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message,
                    "mentioned_list": keywords.split(",") if keywords else []
                }
            }
            
            # 使用 httpx 异步发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
            
            if response.status_code == 200:
                logger.info(f"企业微信消息发送成功: {response.json()}")
                return response.json()
            else:
                logger.error(f"企业微信消息发送失败: {response.text}")
                return {"success": False, "message": "发送失败"}
                
        except Exception as e:
            logger.error(f"发送企业微信消息异常: {e}")
            return {"success": False, "message": f"发送异常: {str(e)}"}
    
    async def send_dingtalk_message(
        self,
        message: str,
        keywords: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送钉钉消息
        
        Args:
            message: 消息内容
            keywords: 关键词配置（JSON 格式）
        
        Returns:
            Dict: 响应结果
        """
        try:
            # 判断 keywords 是否为空，如果为空，就不生成签名数据，直接发送
            if keywords:
                keywords = eval(keywords)
                secret = keywords.get("secret_key")
                timestamp = str(round(time.time() * 1000))
                secret_enc = secret.encode('utf-8')
                string_to_sign = f'{timestamp}\n{secret}'
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                webhook_url_with_sign = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            else:
                webhook_url_with_sign = self.webhook_url
            
            # 构造钉钉消息格式
            data = {
                "msgtype": "text",
                "text": {
                    "content": message,
                    "mentioned_list": ["@all"]  # 将关键词转换为列表
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            
            # 使用 httpx 异步发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url_with_sign,
                    headers=headers,
                    json=data
                )
            
            if response.status_code == 200:
                logger.info(f"钉钉消息发送成功: {response.json()}")
                return response.json()
            else:
                logger.error(f"钉钉消息发送失败: {response.text}")
                return {"success": False, "message": "发送失败"}
                
        except Exception as e:
            logger.error(f"发送钉钉消息异常: {e}")
            return {"success": False, "message": f"发送异常: {str(e)}"}
    
    async def send_feishu_message(
        self,
        message: str,
        keywords: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送飞书消息
        
        Args:
            message: 消息内容
            keywords: 关键词配置（JSON 格式，包含 sign）
        
        Returns:
            Dict: 响应结果
        """
        try:
            data = {}
            
            # 判断 keywords 是否为空，如果为空，就不生成签名数据，直接发送
            if keywords:
                # 如果不是空的，就获取 sign 的值，默认填写为 {"sign":"xxxx"}
                keywords = eval(keywords)
                secret = keywords.get("sign")
                # 获取当前时间戳
                timestamp = int(time.time())
                # 拼接时间戳与签名名
                string_to_sign = '{}\n{}'.format(timestamp, secret)
                # 获取这个 code
                hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
                # 对 code 进行 base64 处理
                sign = base64.b64encode(hmac_code).decode('utf-8')
                # 获取到内容后，将 sign 给到字典中
                data.update({"sign": sign})
            
            # 如果没有签名，这里就直接处理
            data.update({"msg_type": "text"})
            data.update({"content": {"text": message}})
            
            headers = {"Content-Type": "application/json"}
            
            # 使用 httpx 异步发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    headers=headers,
                    json=data
                )
            
            if response.status_code == 200:
                logger.info(f"飞书消息发送成功: {response.json()}")
                return response.json()
            else:
                logger.error(f"飞书消息发送失败: {response.text}")
                return {"success": False, "message": "发送失败"}
                
        except Exception as e:
            logger.error(f"发送飞书消息异常: {e}")
            return {"success": False, "message": f"发送异常: {str(e)}"}
    
    async def send_message(
        self,
        case_collection_info: Dict[str, Any],
        coll_type: str,
        test_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        查询测试结果并发送机器人通知
        
        Args:
            case_collection_info: 用例集合信息
            coll_type: 用例类型
            test_result: 测试结果对象
        
        Returns:
            Dict: 响应结果
        """
        try:
            # 替换消息模板中的变量
            message_template = test_result.get("message_template", "")
            message = message_template.replace("{{coll_name}}", case_collection_info.get("collection_name", ""))
            message = message.replace("{{status}}", test_result.get("status", ""))
            
            # 结合路径不一样，对应的地址不一样
            if coll_type == "web":
                report_url = f"{settings.REPORT_WEB_URL}/{test_result.get('detail', '')}/index.html"
            elif coll_type == "app":
                report_url = f"{settings.REPORT_APP_URL}/{test_result.get('detail', '')}/index.html"
            elif coll_type == "api":
                report_url = f"{settings.REPORT_API_URL}/{test_result.get('detail', '')}/index.html"
            else:
                return {"success": False, "message": "不支持的用例类型"}
            
            message = message.replace("{{report_url}}", report_url)
            
            # 6. 发送机器人通知
            robot_config = test_result.get("robot_config", {})
            robot_type = robot_config.get("robot_type", "")
            
            if robot_type == "1" or robot_type == 1:  # 企业微信
                logger.info("---发送企业微信消息---")
                return await self.send_wechat_message(
                    robot_config.get("webhook_url", ""),
                    message,
                    robot_config.get("keywords", "")
                )
            elif robot_type == "2" or robot_type == 2:  # 钉钉
                logger.info("---发送钉钉消息---")
                return await self.send_dingtalk_message(
                    robot_config.get("webhook_url", ""),
                    message,
                    robot_config.get("keywords", "")
                )
            elif robot_type == "3" or robot_type == 3:  # 飞书
                logger.info("---发送飞书消息---")
                return await self.send_feishu_message(
                    robot_config.get("webhook_url", ""),
                    message,
                    robot_config.get("keywords", "")
                )
            else:
                return {"success": False, "message": "未知的机器人类型"}
                
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return {"success": False, "message": f"服务器错误,请联系管理员:{str(e)}"}


# 创建全局实例（可以在后续导入使用）
ThirdPartyMessengerObj = None


def get_messenger(platform: str = None, webhook_url: str = None, keywords: str = None) -> ThirdPartyMessenger:
    """
    获取消息通知工具实例
    
    Args:
        platform: 平台类型
        webhook_url: Webhook URL
        keywords: 关键词配置
    
    Returns:
        ThirdPartyMessenger: 消息通知工具实例
    """
    global ThirdPartyMessengerObj
    if ThirdPartyMessengerObj is None:
        ThirdPartyMessengerObj = ThirdPartyMessenger(platform, webhook_url, keywords)
    return ThirdPartyMessengerObj
