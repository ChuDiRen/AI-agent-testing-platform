from app import database
import bcrypt

class User(database.Model):
    __tablename__ = "t_user" # 对应的表
    # 对应的表字段
    id = database.Column(database.Integer, primary_key=True, )
    username = database.Column(database.String(255), unique=True)
    password = database.Column(database.String(255), unique=True)
    create_time = database.Column(database.DateTime, unique=True)


    def set_password(self, password):
        """加密密码：使用bcrypt生成哈希值"""
        # 转换为字节类型，加盐哈希（salt自动生成）
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        """验证密码：比对输入密码的哈希值与存储的哈希值"""
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))