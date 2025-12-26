# 后端重构命令

## 命令说明
使用 `/backend-refactor` 触发后端代码重构，优化代码结构和规范。

## 重构范围

### 1. Controller层重构（参考sysmanage模式）
```python
# 问题：直接在Controller中处理业务逻辑
@module_route.post("/queryByPage")
async def queryByPage(query: ApiInfoQuery, session: Session = Depends(get_session)):
    # 直接查询数据库
    result = session.query(ApiInfo).filter(...).all()
    return respModel.ok_resp_list(lst=result, total=len(result))

# 重构后：使用静态方法调用Service层（参考sysmanage标准）
@module_route.post("/queryByPage", summary="分页查询API接口信息", dependencies=[Depends(check_permission("apitest:api:query"))])
async def queryByPage(query: ApiInfoQuery, session: Session = Depends(get_session)):
    try:
        datas, total = InfoService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询API接口信息")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        data = InfoService.query_by_id(session, id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API接口信息", dependencies=[Depends(check_permission("apitest:api:add"))])
async def insert(api_info: ApiInfoCreate, session: Session = Depends(get_session)):
    try:
        data = InfoService.create(session, api_info)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新API接口信息", dependencies=[Depends(check_permission("apitest:api:edit"))])
async def update(api_info: ApiInfoUpdate, session: Session = Depends(get_session)):
    try:
        db_api = InfoService.update(session, api_info)
        if db_api:
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="接口不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API接口信息", dependencies=[Depends(check_permission("apitest:api:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        success = InfoService.delete(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="接口不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
```

### 2. Service层标准化（参考sysmanage模式）
```python
class InfoService:
    """接口信息Service层 - 使用静态方法模式"""
    
    @staticmethod
    def query_by_page(session: Session, query: ApiInfoQuery) -> Tuple[List[ApiInfo], int]:
        """标准分页查询方法"""
        offset = (query.page - 1) * query.pageSize
        statement = select(ApiInfo)
        
        # 应用过滤条件
        if query.project_id:
            statement = statement.where(ApiInfo.project_id == query.project_id)
        if query.api_name:
            statement = statement.where(ApiInfo.api_name.like(f"%{query.api_name}%"))
        if query.request_method:
            statement = statement.where(ApiInfo.request_method == query.request_method)
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(ApiInfo)
        if query.project_id:
            count_statement = count_statement.where(ApiInfo.project_id == query.project_id)
        if query.api_name:
            count_statement = count_statement.where(ApiInfo.api_name.like(f"%{query.api_name}%"))
        if query.request_method:
            count_statement = count_statement.where(ApiInfo.request_method == query.request_method)
        total = len(session.exec(count_statement).all())
        
        return datas, total
    
    @staticmethod
    def query_by_id(session: Session, id: int) -> Optional[ApiInfo]:
        """标准按ID查询方法"""
        statement = select(ApiInfo).where(ApiInfo.id == id)
        return session.exec(statement).first()
    
    @staticmethod
    def create(session: Session, api_info: ApiInfoCreate) -> ApiInfo:
        """标准创建方法"""
        data = ApiInfo(**api_info.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return data
    
    @staticmethod
    def update(session: Session, api_info: ApiInfoUpdate) -> Optional[ApiInfo]:
        """标准更新方法"""
        statement = select(ApiInfo).where(ApiInfo.id == api_info.id)
        db_api = session.exec(statement).first()
        if not db_api:
            return None
        
        update_data = api_info.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_api, key, value)
        session.commit()
        return db_api
    
    @staticmethod
    def delete(session: Session, id: int) -> bool:
        """标准删除方法"""
        statement = select(ApiInfo).where(ApiInfo.id == id)
        data = session.exec(statement).first()
        if not data:
            return False
        
        session.delete(data)
        session.commit()
        return True
```

### 3. 统一响应格式
```python
# 在 core/resp_model.py 中增强响应格式
class RespModel:
    @staticmethod
    def ok_resp_list(lst: list, total: int = None, msg: str = "操作成功"):
        return {
            "code": 200,
            "success": True,
            "message": msg,
            "data": {
                "list": lst,
                "total": total or len(lst),
                "page": getattr(lst, 'page', 1),
                "pageSize": getattr(lst, 'pageSize', len(lst))
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ok_resp(obj: Any = None, msg: str = "操作成功"):
        return {
            "code": 200,
            "success": True,
            "message": msg,
            "data": obj,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error_resp(msg: str, code: int = 500):
        return {
            "code": code,
            "success": False,
            "message": msg,
            "data": None,
            "timestamp": datetime.now().isoformat()
        }
```

### 4. 错误处理增强
```python
# 在 core/exceptions.py 中定义统一异常
class BusinessException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ValidationException(BusinessException):
    def __init__(self, message: str):
        super().__init__(message, 422)

class NotFoundException(BusinessException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)
```

### 5. 权限控制增强
```python
# 在 core/dependencies.py 中增强权限检查
def check_permission(permission: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        # 检查用户权限
        if not await check_user_permission(current_user.id, permission, session):
            raise PermissionException("权限不足")
        return current_user
    return dependency

## 使用示例

```
/backend-refactor --module apitest --target Controller --action refactor
/backend-refactor --module apitest --target Service --action optimize  
/backend-refactor --module apitest --target All --action full-refactor
```

## 注意事项

1. 备份原始代码
2. 逐步重构，避免影响现有功能
3. 更新相关测试用例
4. 验证API接口兼容性
