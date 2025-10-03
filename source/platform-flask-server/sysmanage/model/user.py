from app import database


class User(database.Model):
    __tablename__ = "t_user"
    id = database.Column(database.Integer, primary_key=True, )
    username = database.Column(database.String(255), unique=True)
    password = database.Column(database.String(255), unique=True)
    create_time = database.Column(database.DateTime, unique=True)
