package com.platform.platformserver.common;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ResultCode {
    SUCCESS(200, "操作成功"),
    ERROR(500, "操作失败"),
    UNAUTHORIZED(401, "未授权"),
    FORBIDDEN(403, "禁止访问"),
    NOT_FOUND(404, "资源不存在"),
    PARAM_ERROR(400, "参数错误"),
    LOGIN_ERROR(1001, "用户名或密码错误"),
    TOKEN_EXPIRED(1002, "Token已过期"),
    TOKEN_INVALID(1003, "Token无效"),
    USER_NOT_EXIST(1004, "用户不存在"),
    USER_ALREADY_EXIST(1005, "用户已存在"),
    CASE_NOT_FOUND(2001, "测试用例不存在"),
    API_NOT_FOUND(2002, "API不存在"),
    EXECUTION_FAILED(2003, "执行失败");

    private final int code;
    private final String message;
}
