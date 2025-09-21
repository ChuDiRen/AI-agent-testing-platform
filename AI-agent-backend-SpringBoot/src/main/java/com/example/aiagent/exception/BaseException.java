// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.exception;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 基础异常类
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class BaseException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /**
     * 错误码
     */
    private Integer code;

    /**
     * 错误消息
     */
    private String message;

    public BaseException() {
        super();
    }

    public BaseException(String message) {
        super(message);
        this.message = message;
        this.code = 500;
    }

    public BaseException(Integer code, String message) {
        super(message);
        this.code = code;
        this.message = message;
    }

    public BaseException(Integer code, String message, Throwable cause) {
        super(message, cause);
        this.code = code;
        this.message = message;
    }
}
