// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.exception;

/**
 * 业务异常类
 * 用于处理业务逻辑相关的异常
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
public class BusinessException extends BaseException {

    private static final long serialVersionUID = 1L;

    public BusinessException(String message) {
        super(400, message);
    }

    public BusinessException(Integer code, String message) {
        super(code, message);
    }

    public BusinessException(Integer code, String message, Throwable cause) {
        super(code, message, cause);
    }
}
