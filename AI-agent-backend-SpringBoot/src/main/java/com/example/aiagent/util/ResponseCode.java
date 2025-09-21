// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.util;

/**
 * 响应码常量类
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
public class ResponseCode {

    // 成功响应码
    public static final int SUCCESS = 200;

    // 客户端错误响应码
    public static final int BAD_REQUEST = 400;
    public static final int UNAUTHORIZED = 401;
    public static final int FORBIDDEN = 403;
    public static final int NOT_FOUND = 404;
    public static final int METHOD_NOT_ALLOWED = 405;
    public static final int CONFLICT = 409;
    public static final int UNPROCESSABLE_ENTITY = 422;

    // 服务器错误响应码
    public static final int INTERNAL_SERVER_ERROR = 500;
    public static final int BAD_GATEWAY = 502;
    public static final int SERVICE_UNAVAILABLE = 503;
    public static final int GATEWAY_TIMEOUT = 504;

    // 业务错误响应码
    public static final int BUSINESS_ERROR = 1000;
    public static final int VALIDATION_ERROR = 1001;
    public static final int DATA_NOT_FOUND = 1002;
    public static final int DATA_ALREADY_EXISTS = 1003;
    public static final int OPERATION_FAILED = 1004;

    // 认证相关错误码
    public static final int LOGIN_FAILED = 2001;
    public static final int TOKEN_INVALID = 2002;
    public static final int TOKEN_EXPIRED = 2003;
    public static final int PERMISSION_DENIED = 2004;
    public static final int ACCOUNT_DISABLED = 2005;
    public static final int ACCOUNT_LOCKED = 2006;

    private ResponseCode() {
        // 工具类，禁止实例化
    }
}
