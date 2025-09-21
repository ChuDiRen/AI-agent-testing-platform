// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.repository;

import com.example.aiagent.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 用户Repository接口
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
@Mapper
public interface UserRepository extends BaseRepository<User> {

    /**
     * 根据用户名查询用户
     */
    User findByUsername(@Param("username") String username);

    /**
     * 根据邮箱查询用户
     */
    User findByEmail(@Param("email") String email);

    /**
     * 根据手机号查询用户
     */
    User findByPhone(@Param("phone") String phone);

    /**
     * 检查用户名是否存在
     */
    boolean existsByUsername(@Param("username") String username);

    /**
     * 检查邮箱是否存在
     */
    boolean existsByEmail(@Param("email") String email);

    /**
     * 检查手机号是否存在
     */
    boolean existsByPhone(@Param("phone") String phone);
}
