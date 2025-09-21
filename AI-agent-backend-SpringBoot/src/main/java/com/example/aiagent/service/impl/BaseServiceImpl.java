// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.service.impl;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.aiagent.service.BaseService;

/**
 * Service基础实现类
 * 继承MyBatis-Plus的ServiceImpl，提供基础业务操作实现
 * 
 * @param <M> Mapper类型
 * @param <T> 实体类型
 * @author 左岚团队
 * @version 1.0.0
 */
public class BaseServiceImpl<M extends BaseMapper<T>, T> extends ServiceImpl<M, T> implements BaseService<T> {
    // 继承ServiceImpl的所有方法实现
    // 可以在这里添加自定义的通用业务方法实现
}
