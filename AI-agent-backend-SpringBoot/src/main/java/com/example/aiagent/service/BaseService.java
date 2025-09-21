// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.service;

import com.baomidou.mybatisplus.extension.service.IService;

/**
 * Service基础接口
 * 继承MyBatis-Plus的IService，提供基础业务操作
 * 
 * @param <T> 实体类型
 * @author 左岚团队
 * @version 1.0.0
 */
public interface BaseService<T> extends IService<T> {
    // 继承IService的所有方法
    // 可以在这里添加自定义的通用业务方法
}
