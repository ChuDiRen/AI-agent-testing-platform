from app import database

class ApiMeta(database.Model):
    __tablename__ = "t_api_meta"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_id = database.Column(database.Integer, comment='项目ID')
    mate_name = database.Column(database.String(255), nullable=True)
    object_url = database.Column(database.String(255), nullable=True)
    file_type = database.Column(database.String(255), nullable=True)
    create_time = database.Column(database.DateTime, nullable=True)