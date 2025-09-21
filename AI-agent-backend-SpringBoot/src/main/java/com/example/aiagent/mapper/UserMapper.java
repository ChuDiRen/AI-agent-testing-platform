// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.aiagent.entity.User;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户Mapper接口
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {
}
