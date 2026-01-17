import jwt
import app
import datetime

class JwtUtils(object):
    @staticmethod
    def create_token(username, password):
        """
        创建访问 token (access token)
        有效期：30分钟
        """
        key = app.application.config["SECRET_KEY"]
        payload = {
            "username": username,
            "password": password,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),  # 30分钟过期
            "type": "access"  # 标记为访问令牌
        }
        token = jwt.encode(payload, key, algorithm="HS256")
        return token

    @staticmethod
    def create_refresh_token(username):
        """
        创建刷新 token (refresh token)
        有效期：7天
        """
        key = app.application.config["SECRET_KEY"]
        payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 7天过期
            "type": "refresh"  # 标记为刷新令牌
        }
        token = jwt.encode(payload, key, algorithm="HS256")
        return token

    @staticmethod
    def verify_token(token):
        """
        验证 token 是否有效
        """
        key = app.application.config["SECRET_KEY"]
        try:
            payload = jwt.decode(token, key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            # token 已过期
            return {"error": "token_expired"}
        except jwt.InvalidTokenError:
            # token 无效
            return None

    @staticmethod
    def refresh_access_token(refresh_token):
        """
        使用 refresh token 刷新 access token
        返回新的 access token 和 refresh token
        """
        key = app.application.config["SECRET_KEY"]
        try:
            # 验证 refresh token
            payload = jwt.decode(refresh_token, key, algorithms=['HS256'])
            
            # 检查是否为 refresh token
            if payload.get("type") != "refresh":
                return None, None
            
            username = payload.get("username")
            
            # 生成新的 access token 和 refresh token
            new_access_token = JwtUtils.create_token(username, "")  # password 不需要存储
            new_refresh_token = JwtUtils.create_refresh_token(username)
            
            return new_access_token, new_refresh_token
        except jwt.ExpiredSignatureError:
            # refresh token 已过期，需要重新登录
            return None, None
        except jwt.InvalidTokenError:
            return None, None

if __name__ == '__main__':
    # token = JwtUtils.create_token("admin","123456")

    # print(token)

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiIxMjM0NTYiLCJleHAiOjE3NTUwODI2NzZ9.kIKOy_QjWmLWtRXy2Dk_eTOiutmRZt78aZxXARPaa7k"
    data = JwtUtils.verify_token(token)
    print(data)
