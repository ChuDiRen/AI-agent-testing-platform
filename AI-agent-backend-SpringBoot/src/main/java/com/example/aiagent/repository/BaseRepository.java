// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.service.IService;

/**
 * Repository基础接口
 * 继承MyBatis-Plus的BaseMapper，提供基础CRUD操作
 * 
 * @param <T> 实体类型
 * @author 左岚团队
 * @version 1.0.0
 */
public interface BaseRepository<T> extends BaseMapper<T> {
    // 继承BaseMapper的所有方法
    // 可以在这里添加自定义的通用方法
}
