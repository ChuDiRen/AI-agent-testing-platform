// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.controller;

import com.example.aiagent.dto.Result;
import com.example.aiagent.dto.LoginRequest;
import com.example.aiagent.dto.LoginResponse;
import com.example.aiagent.dto.UserCreateRequest;
import com.example.aiagent.dto.UserUpdateRequest;
import com.example.aiagent.entity.User;
import com.example.aiagent.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;

/**
 * 用户管理控制器
 */
@Tag(name = "用户管理", description = "用户相关API")
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Validated
public class UserController extends BaseController {

    private final UserService userService;

    @Operation(summary = "用户注册", description = "创建新用户账户")
    @PostMapping("/register")
    public Result<User> register(@Valid @RequestBody UserCreateRequest request) {
        User user = userService.createUser(request);
        return Result.success(user);
    }

    @Operation(summary = "用户登录", description = "用户登录接口")
    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = userService.login(request);
        return Result.success(response);
    }

    @Operation(summary = "创建用户", description = "创建新用户")
    @PostMapping
    public Result<User> createUser(@Valid @RequestBody UserCreateRequest request) {
        User user = userService.createUser(request);
        return Result.success(user);
    }

    @Operation(summary = "根据用户名查询用户", description = "根据用户名查询用户信息")
    @GetMapping("/username/{username}")
    public Result<User> getUserByUsername(
            @Parameter(description = "用户名") @PathVariable String username) {
        User user = userService.findByUsername(username);
        if (user == null) {
            return Result.error("用户不存在");
        }
        return Result.success(user);
    }

    @Operation(summary = "更新用户信息", description = "更新指定用户的信息")
    @PutMapping("/{id}")
    public Result<User> updateUser(
            @Parameter(description = "用户ID") @PathVariable @NotNull Long id,
            @Valid @RequestBody UserUpdateRequest request) {
        User user = userService.updateUser(id, request);
        return Result.success(user);
    }

    @Operation(summary = "更新用户状态", description = "启用或禁用用户")
    @PutMapping("/{id}/status")
    public Result<Void> updateUserStatus(
            @Parameter(description = "用户ID") @PathVariable @NotNull Long id,
            @Parameter(description = "状态：1-启用，0-禁用") @RequestParam Integer status) {
        userService.updateUserStatus(id, status);
        return Result.success();
    }

    @Operation(summary = "检查用户名是否存在", description = "检查用户名是否已被使用")
    @GetMapping("/check/username")
    public Result<Boolean> checkUsername(@RequestParam String username) {
        boolean exists = userService.existsByUsername(username);
        return Result.success(exists);
    }

    @Operation(summary = "检查邮箱是否存在", description = "检查邮箱是否已被使用")
    @GetMapping("/check/email")
    public Result<Boolean> checkEmail(@RequestParam String email) {
        boolean exists = userService.existsByEmail(email);
        return Result.success(exists);
    }

    @Operation(summary = "检查手机号是否存在", description = "检查手机号是否已被使用")
    @GetMapping("/check/phone")
    public Result<Boolean> checkPhone(@RequestParam String phone) {
        boolean exists = userService.existsByPhone(phone);
        return Result.success(exists);
    }
}