// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.dto;

import lombok.Data;

/**
 * 登录响应DTO
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
@Data
public class LoginResponse {

    /**
     * 访问令牌
     */
    private String accessToken;

    /**
     * 令牌类型
     */
    private String tokenType = "Bearer";

    /**
     * 过期时间（秒）
     */
    private Long expiresIn;

    /**
     * 用户信息
     */
    private UserInfo userInfo;

    @Data
    public static class UserInfo {
        private Long id;
        private String username;
        private String email;
        private String realName;
        private String avatar;
        private Integer status;
    }
}
