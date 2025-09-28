// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.example.aiagent.dto.LoginRequest;
import com.example.aiagent.dto.LoginResponse;
import com.example.aiagent.dto.UserCreateRequest;
import com.example.aiagent.dto.UserUpdateRequest;
import com.example.aiagent.entity.User;
import com.example.aiagent.mapper.UserMapper;
import com.example.aiagent.service.UserService;
import com.example.aiagent.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Collections;

/**
 * 用户服务实现类
 */
@Service
@RequiredArgsConstructor
public class UserServiceImpl extends BaseServiceImpl<UserMapper, User> implements UserService, UserDetailsService {

    private final UserMapper userMapper; // 启用数据库操作
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil; // 添加JWT工具类依赖

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = findByUsername(username);
        if (user == null) {
            throw new UsernameNotFoundException("用户不存在: " + username);
        }

        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getUsername())
                .password(user.getPassword())
                .authorities(Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER")))
                .accountExpired(false)
                .accountLocked(user.getStatus() == 0) // 状态为0时账户被锁定
                .credentialsExpired(false)
                .disabled(user.getStatus() == 0)
                .build();
    }

    @Override
    public User findByUsername(String username) {
        return userMapper.selectOne(new QueryWrapper<User>().eq("username", username));
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        User user = findByUsername(request.getUsername());
        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        // 生成JWT令牌
        String token = jwtUtil.generateToken(user.getUsername(), user.getId());
        
        LoginResponse response = new LoginResponse();
        response.setAccessToken(token);
        response.setExpiresIn(86400L); // 24小时

        // 设置用户信息
        LoginResponse.UserInfo userInfo = new LoginResponse.UserInfo();
        userInfo.setId(user.getId());
        userInfo.setUsername(user.getUsername());
        userInfo.setEmail(user.getEmail());
        userInfo.setStatus(user.getStatus());
        response.setUserInfo(userInfo);

        return response;
    }

    @Override
    public User createUser(UserCreateRequest request) {
        // 检查用户名是否已存在
        if (existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }

        if (existsByEmail(request.getEmail())) {
            throw new RuntimeException("邮箱已存在");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setEmail(request.getEmail());
        user.setPhone(request.getPhone());
        user.setStatus(1); // 默认启用

        userMapper.insert(user);
        return user;
    }

    @Override
    public User updateUser(Long id, UserUpdateRequest request) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        if (request.getEmail() != null && !request.getEmail().equals(user.getEmail())) {
            if (existsByEmail(request.getEmail())) {
                throw new RuntimeException("邮箱已存在");
            }
            user.setEmail(request.getEmail());
        }

        if (request.getPhone() != null) {
            user.setPhone(request.getPhone());
        }

        userMapper.updateById(user);
        return user;
    }

    @Override
    public boolean existsByUsername(String username) {
        return userMapper.selectCount(new QueryWrapper<User>().eq("username", username)) > 0;
    }

    @Override
    public boolean existsByEmail(String email) {
        return userMapper.selectCount(new QueryWrapper<User>().eq("email", email)) > 0;
    }

    @Override
    public boolean existsByPhone(String phone) {
        return userMapper.selectCount(new QueryWrapper<User>().eq("phone", phone)) > 0;
    }

    @Override
    public void updateUserStatus(Long id, Integer status) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        user.setStatus(status);
        userMapper.updateById(user);
    }
}
