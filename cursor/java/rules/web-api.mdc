---
description: 
globs: 
alwaysApply: false
---
# Web API 设计与开发规范

## RESTful 接口设计规范

### URL 路径设计
- **后台管理模块**: 默认使用 `/api/admin/` 路径前缀
- **商城应用模块**: 默认使用 `/api/app/` 路径前缀  
- **仓配系统模块**: 默认使用 `/api/wms/` 路径前缀

### 资源命名规范
- **资源名词**: 使用复数形式，如 `/users`、`/orders`、`/products`
- **层级关系**: 体现资源间的层级关系，如 `/users/{id}/orders`
- **避免动词**: URL中避免使用动词，动作通过HTTP方法表达
- **小写字母**: 统一使用小写字母，单词间用连字符分隔

### HTTP 方法规范
- **GET**: 获取资源数据，支持查询参数
- **POST**: 创建新资源或执行复杂查询（分页、筛选）
- **PUT**: 完整更新资源
- **DELETE**: 删除资源
- **⚠️ 限制**: 项目中仅允许使用 GET 和 POST 方法

## 请求与响应规范

### 请求参数规范
- **简单查询**: 2个以下参数可以直接使用 `@RequestParam`
- **复杂参数**: 超过2个参数必须定义专门的DTO实体
- **DTO命名**: 清晰表达用途，如 `UserQueryDTO`、`OrderCreateDTO`
- **参数验证**: 使用Bean Validation注解进行参数校验

### 响应格式规范
- **统一封装**: 必须使用 [Result](mdc:gyl-common/src/main/java/com/njgyl/common/result/Result.java) 结构封装所有响应
- **时间格式**: 所有时间字段必须转换为字符串格式返回
- **空值处理**: 明确空值返回策略，避免null值直接返回
- **分页数据**: 使用 [ListWithPageDTO](mdc:gyl-common/src/main/java/com/njgyl/common/dto/ListWithPageDTO.java) 封装分页结果

### 响应结构示例
```json
{
  "error": 0,
  "body": {
    "data": [],
    "total": 100,
    "pageNum": 1,
    "pageSize": 20
  },
  "message": "操作成功",
  "success": true
}
```

## Controller 层开发规范

### 类级别注解
```java
@RestController
@RequestMapping("/api/admin/users")
@Api(tags = "用户管理")
@Validated
@Slf4j
public class AdminUserController {
    // 控制器实现
}
```

### 方法级别规范
```java
@PostMapping("/list")
@ApiOperation("分页查询用户列表")
public Result<ListWithPageDTO<AdminUserListDTO>> getUserPage(
    @RequestBody @Valid AdminUserQueryDTO queryDTO) {
    
    return adminUserService.getAdminUserPage(queryDTO);
}
```

### 参数校验注解
- **@Valid**: 用于DTO参数校验
- **@Validated**: 用于类级别校验
- **@NotNull**: 非空校验
- **@NotBlank**: 非空字符串校验
- **@Size**: 长度限制
- **@Pattern**: 正则表达式校验

## 安全与认证规范

### 认证机制
- **Token认证**: 使用JWT或自定义token进行身份认证
- **Token存储**: Redis缓存token，设置合理过期时间
- **Token刷新**: 提供token刷新机制，避免频繁登录

### 权限控制
- **角色权限**: 基于角色的访问控制(RBAC)
- **接口权限**: 细粒度的接口级别权限控制
- **数据权限**: 根据用户角色过滤数据范围

### 安全头设置
```java
// 设置安全相关的HTTP头
response.setHeader("X-Content-Type-Options", "nosniff");
response.setHeader("X-Frame-Options", "DENY");
response.setHeader("X-XSS-Protection", "1; mode=block");
```

## 错误处理与状态码

### 业务错误码
- **成功**: 0
- **参数错误**: 1000-1999
- **业务错误**: 2000-2999
- **认证错误**: 3000-3999
- **系统错误**: 9000-9999

### 错误响应格式
```json
{
  "error": 3002,
  "body": null,
  "message": "该账号已经注册",
  "success": false
}
```

### HTTP状态码使用
- **200**: 请求成功（包括业务失败的情况）
- **400**: 请求参数错误
- **401**: 未认证
- **403**: 无权限
- **500**: 服务器内部错误

## API文档规范

### Swagger注解
```java
@Api(tags = "用户管理")
public class UserController {
    
    @ApiOperation("创建用户")
    @ApiImplicitParams({
        @ApiImplicitParam(name = "createDTO", value = "用户创建信息", required = true)
    })
    @PostMapping("/create")
    public Result<Void> createUser(@RequestBody @Valid UserCreateDTO createDTO) {
        return userService.createUser(createDTO);
    }
}
```

### 文档维护
- **及时更新**: 接口变更时同步更新API文档
- **示例完整**: 提供完整的请求和响应示例
- **错误说明**: 说明可能的错误情况和处理方式

## 性能优化规范

### 分页查询优化
- **默认分页**: 列表查询默认分页，避免大量数据查询
- **分页参数**: 提供合理的默认页大小，限制最大页大小
- **索引优化**: 确保分页查询字段有合适的数据库索引

### 缓存策略
- **查询缓存**: 对频繁查询的数据进行Redis缓存
- **缓存更新**: 数据变更时及时更新或清除相关缓存
- **缓存穿透**: 防止缓存穿透和缓存雪崩

### 接口性能监控
- **响应时间**: 监控接口平均响应时间
- **并发能力**: 监控接口并发处理能力
- **错误率**: 监控接口错误率和异常情况

## 版本管理规范

### API版本策略
- **URL版本**: `/api/v1/users`、`/api/v2/users`
- **向后兼容**: 新版本要考虑向后兼容性
- **废弃通知**: 老版本废弃要提前通知

### 版本发布流程
- **测试环境**: 新版本先在测试环境验证
- **灰度发布**: 生产环境采用灰度发布策略
- **回滚方案**: 准备版本回滚方案

## 监控与日志

### 访问日志
- **请求记录**: 记录所有API请求的关键信息
- **响应时间**: 记录接口响应时间
- **用户标识**: 记录请求用户身份信息

### 业务日志
- **关键操作**: 记录用户的关键业务操作
- **数据变更**: 记录重要数据的变更历史
- **异常情况**: 详细记录异常情况和错误信息

### 日志格式规范
```java
// 请求开始日志
log.info("API请求开始 - 接口：{}，用户：{}，参数：{}", 
         request.getRequestURI(), userId, JSON.toJSONString(params));

// 请求结束日志
log.info("API请求结束 - 接口：{}，耗时：{}ms，结果：{}", 
         request.getRequestURI(), duration, success ? "成功" : "失败");
```
