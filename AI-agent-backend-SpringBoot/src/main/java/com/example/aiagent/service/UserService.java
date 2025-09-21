// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.service;

import com.example.aiagent.dto.LoginRequest;
import com.example.aiagent.dto.LoginResponse;
import com.example.aiagent.dto.UserCreateRequest;
import com.example.aiagent.dto.UserUpdateRequest;
import com.example.aiagent.entity.User;

/**
 * 用户Service接口
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
public interface UserService extends BaseService<User> {

    /**
     * 用户登录
     */
    LoginResponse login(LoginRequest request);

    /**
     * 根据用户名查询用户
     */
    User findByUsername(String username);

    /**
     * 创建用户
     */
    User createUser(UserCreateRequest request);

    /**
     * 更新用户
     */
    User updateUser(Long id, UserUpdateRequest request);

    /**
     * 检查用户名是否存在
     */
    boolean existsByUsername(String username);

    /**
     * 检查邮箱是否存在
     */
    boolean existsByEmail(String email);

    /**
     * 检查手机号是否存在
     */
    boolean existsByPhone(String phone);

    /**
     * 启用/禁用用户
     */
    void updateUserStatus(Long id, Integer status);
}
