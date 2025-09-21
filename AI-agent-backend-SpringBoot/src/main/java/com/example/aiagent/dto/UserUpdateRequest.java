// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * 用户更新请求DTO
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
@Data
public class UserUpdateRequest {

    /**
     * 邮箱
     */
    @Email(message = "邮箱格式不正确")
    private String email;

    /**
     * 手机号
     */
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;

    /**
     * 真实姓名
     */
    private String realName;

    /**
     * 头像URL
     */
    private String avatar;

    /**
     * 部门ID
     */
    private Long departmentId;

    /**
     * 备注
     */
    private String remark;
}
