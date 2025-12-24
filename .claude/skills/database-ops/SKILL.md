# 数据库操作技能

## 触发条件
- 关键词：数据库、SQL、建表、MySQL、字典、DDL、索引、迁移、schema、SQLModel
- 场景：当用户需要进行数据库操作时

## 核心规范

### 规范1：本项目数据库技术栈

- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **数据库**: MySQL
- **驱动**: PyMySQL (同步) / aiomysql (异步)
- **连接管理**: `core/database.py`

### 规范2：Model 定义规范

```python
# {module}/model/{Module}Model.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class {Module}(SQLModel, table=True):
    """模块数据模型"""
    __tablename__ = "{module}"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="名称")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")
    status: int = Field(default=1, description="状态：1启用 0禁用")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=50, description="创建人")
```

### 规范3：数据库会话管理

```python
# core/database.py
from sqlmodel import Session, create_engine
from config.dev_settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    """获取数据库会话（依赖注入用）"""
    with Session(engine) as session:
        yield session
```

### 规范4：Service 层数据库操作

```python
from sqlmodel import Session, select, and_, or_
from datetime import datetime

class {Module}Service:
    def __init__(self, session: Session):
        self.session = session
    
    # 分页查询
    def query_by_page(self, page: int, page_size: int, **filters):
        statement = select({Module})
        
        # 条件筛选
        if filters.get('name'):
            statement = statement.where({Module}.name.contains(filters['name']))
        if filters.get('status') is not None:
            statement = statement.where({Module}.status == filters['status'])
        
        # 排序
        statement = statement.order_by({Module}.id.desc())
        
        # 统计总数
        total = len(self.session.exec(statement).all())
        
        # 分页
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    # 根据ID查询
    def get_by_id(self, id: int):
        return self.session.get({Module}, id)
    
    # 创建
    def create(self, **kwargs):
        data = {Module}(**kwargs, create_time=datetime.now())
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    # 更新
    def update(self, id: int, update_data: dict):
        data = self.get_by_id(id)
        if not data:
            return False
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        data.update_time = datetime.now()
        self.session.add(data)
        self.session.commit()
        return True
    
    # 删除
    def delete(self, id: int):
        data = self.get_by_id(id)
        if not data:
            return False
        self.session.delete(data)
        self.session.commit()
        return True
    
    # 批量删除
    def batch_delete(self, ids: list):
        statement = select({Module}).where({Module}.id.in_(ids))
        datas = self.session.exec(statement).all()
        for data in datas:
            self.session.delete(data)
        self.session.commit()
        return len(datas)
```

### 规范5：复杂查询示例

```python
from sqlmodel import select, and_, or_, func

# 多条件查询
statement = select({Module}).where(
    and_(
        {Module}.status == 1,
        or_(
            {Module}.name.contains(keyword),
            {Module}.description.contains(keyword)
        )
    )
)

# 关联查询
statement = select({Module}, RelatedModel).join(
    RelatedModel, {Module}.related_id == RelatedModel.id
)

# 聚合查询
statement = select(func.count({Module}.id)).where({Module}.status == 1)
count = self.session.exec(statement).one()

# 分组统计
statement = select(
    {Module}.status,
    func.count({Module}.id).label('count')
).group_by({Module}.status)
```

### 规范6：事务处理

```python
def batch_operation(self, items: list):
    try:
        for item in items:
            self.session.add(item)
        self.session.commit()
        return True
    except Exception as e:
        self.session.rollback()
        raise DatabaseException(f"批量操作失败: {e}")
```

## 禁止事项
- ❌ 在 Controller 中直接操作数据库
- ❌ 不使用参数化查询（SQL 注入风险）
- ❌ 忘记 commit 或 rollback
- ❌ 不处理数据库异常

## 检查清单
- [ ] 是否使用 SQLModel 定义模型
- [ ] 是否通过 Service 层操作数据库
- [ ] 是否有事务处理
- [ ] 是否有异常处理
