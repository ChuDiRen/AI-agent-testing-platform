---
description: 
globs: 
alwaysApply: false
---
# 异常处理与错误管理规范

## 异常分类体系

### 业务异常 (BusinessException)
- **使用场景**: 业务逻辑验证失败、业务规则不满足
- **抛出位置**: Service层业务逻辑处理中
- **示例**: 用户名已存在、库存不足、订单状态不允许操作
- **处理方式**: `throw new BusinessException("业务错误信息")`

### 服务异常 (ServiceException) 
- **使用场景**: 服务层处理过程中的系统性错误
- **抛出位置**: Service层调用Manager层或外部服务时
- **示例**: 外部API调用失败、数据处理异常、配置错误
- **处理方式**: `throw new ServiceException("服务错误信息")`

### 数据访问异常 (DataAccessException)
- **使用场景**: 数据库操作相关错误
- **抛出位置**: Manager层和Mapper层
- **示例**: SQL执行失败、数据库连接异常、数据完整性约束违反
- **处理方式**: `throw new DataAccessException("数据访问错误信息")`

## 异常处理最佳实践

### 日志记录规范
```java
// 推荐的异常日志记录方式
try {
    // 业务逻辑
} catch (Exception e) {
    log.error("方法名执行失败，参数：{}，错误信息：{}", 
              JSON.toJSONString(参数对象), e.getMessage(), e);
    throw new ServiceException("操作失败：" + e.getMessage());
}
```

### 日志记录内容要求
- **必须包含**: 方法名、关键参数、完整堆栈信息
- **参数记录**: 使用JSON序列化关键参数，避免敏感信息泄露
- **错误信息**: 记录原始异常消息和自定义业务消息
- **日志级别**: 业务异常使用WARN，系统异常使用ERROR

### 异常传播策略
- **Service层**: 捕获Manager层异常，转换为业务友好的错误信息
- **Manager层**: 捕获Mapper层异常，记录详细日志，向上抛出包装后的异常
- **Controller层**: 不处理业务异常，由全局异常处理器统一处理

## 统一异常处理

### 全局异常处理器
- **位置**: `gyl-gateway` 模块中配置
- **职责**: 统一处理所有未捕获异常，返回标准错误响应
- **响应格式**: 使用 [Result](mdc:gyl-common/src/main/java/com/njgyl/common/result/Result.java) 结构封装错误信息

### 错误码管理
- **定义位置**: [ResultCode](mdc:gyl-common/src/main/java/com/njgyl/common/enums/ResultCode.java) 枚举
- **命名规范**: 功能模块_错误类型_具体错误
- **错误码分配**: 避免冲突，保持连续性
- **错误信息**: 用户友好的中文描述

## 异常处理示例

### Service层异常处理
```java
@Override
public Result<UserDTO> createUser(UserCreateDTO createDTO) {
    try {
        log.info("创建用户，参数：{}", JSON.toJSONString(createDTO));
        
        // 业务验证
        if (adminUserManager.isUserNameExists(createDTO.getUserName(), null)) {
            return Result.error(ResultCode.ACCOUNT_SAME.code(), "用户名已存在");
        }
        
        // 执行创建
        AdminUser user = convertToEntity(createDTO);
        boolean success = adminUserManager.createUser(user);
        
        if (!success) {
            return Result.error(ResultCode.ERROR.code(), "创建用户失败");
        }
        
        return Result.success();
    } catch (Exception e) {
        log.error("创建用户失败，参数：{}，错误：{}", 
                  JSON.toJSONString(createDTO), e.getMessage(), e);
        return Result.error(ResultCode.ERROR.code(), "创建用户失败：" + e.getMessage());
    }
}
```

### Manager层异常处理
```java
public boolean createUser(AdminUser user) {
    try {
        log.info("保存用户信息，用户名：{}", user.getUserName());
        
        // 数据库操作
        int result = adminUserMapper.insert(user);
        
        // 缓存操作
        clearUserCache(user.getId());
        
        return result > 0;
    } catch (Exception e) {
        log.error("保存用户信息失败，用户名：{}，错误：{}", 
                  user.getUserName(), e.getMessage(), e);
        throw new DataAccessException("保存用户信息失败：" + e.getMessage());
    }
}
```

## 特殊场景处理

### 事务回滚场景
```java
@Transactional(rollbackFor = Exception.class)
public Result<Void> registerUser(RegisterDTO registerDTO) {
    try {
        // 创建门店
        Shop shop = createShop(registerDTO);
        
        // 创建用户
        AdminUser user = createUser(registerDTO, shop.getId());
        
        // 创建钱包
        createWallet(shop.getId());
        
        return Result.success();
    } catch (Exception e) {
        log.error("用户注册失败，参数：{}，错误：{}", 
                  JSON.toJSONString(registerDTO), e.getMessage(), e);
        // 事务自动回滚
        throw new ServiceException("注册失败：" + e.getMessage());
    }
}
```

### 外部API调用异常
```java
public String sendSMS(String phone, String code) {
    try {
        // 调用短信服务
        SmsResponse response = smsClient.send(phone, code);
        
        if (!response.isSuccess()) {
            log.warn("短信发送失败，手机号：{}，响应：{}", phone, response);
            throw new ServiceException("短信发送失败：" + response.getMessage());
        }
        
        return response.getMessageId();
    } catch (Exception e) {
        log.error("短信发送异常，手机号：{}，错误：{}", phone, e.getMessage(), e);
        throw new ServiceException("短信服务异常：" + e.getMessage());
    }
}
```

## 监控与告警

### 错误监控
- **日志聚合**: 使用ELK等工具收集和分析错误日志
- **异常统计**: 统计各类异常的发生频率和趋势
- **性能监控**: 监控异常对系统性能的影响

### 告警机制
- **严重异常**: 系统异常立即告警
- **业务异常**: 超过阈值时告警
- **错误率**: 错误率超过预设值时告警
