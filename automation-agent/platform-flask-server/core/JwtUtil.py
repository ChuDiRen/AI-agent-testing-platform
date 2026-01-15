import jwt
import app
import datetime

class JwtUtils(object):
    @staticmethod
    def create_token(username,password):
        key = app.application.config["SECRET_KEY"]
        # 要把什么东西转换成token
        payload ={
            "username":username,
            "password":password,
            "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=5) #设置过期时间为五分钟
        }
        token = jwt.encode(payload,key,algorithm="HS256")
        return token

    @staticmethod
    def verify_token(token):
        key = app.application.config["SECRET_KEY"]
        try:
            payload = jwt.decode(token,key,algorithms=['HS256'])
            return payload
        except jwt.InvalidTokenError:
            return None

if __name__ == '__main__':
    # token = JwtUtils.create_token("admin","123456")

    # print(token)

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiIxMjM0NTYiLCJleHAiOjE3NTUwODI2NzZ9.kIKOy_QjWmLWtRXy2Dk_eTOiutmRZt78aZxXARPaa7k"
    data = JwtUtils.verify_token(token)
    print(data)
