// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.controller;

import com.example.aiagent.dto.Result;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

/**
 * Controller基础类
 * 提供统一的响应格式和通用方法
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
public abstract class BaseController {

    /**
     * 返回成功响应
     */
    protected <T> ResponseEntity<Result<T>> success(T data) {
        return ResponseEntity.ok(Result.success(data));
    }

    /**
     * 返回成功响应（无数据）
     */
    protected ResponseEntity<Result<Void>> success() {
        return ResponseEntity.ok(Result.success());
    }

    /**
     * 返回成功响应（带消息）
     */
    protected <T> ResponseEntity<Result<T>> success(T data, String message) {
        return ResponseEntity.ok(Result.success(data, message));
    }

    /**
     * 返回失败响应
     */
    protected <T> ResponseEntity<Result<T>> error(String message) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Result.error(message));
    }

    /**
     * 返回失败响应（带状态码）
     */
    protected <T> ResponseEntity<Result<T>> error(int code, String message) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Result.error(code, message));
    }

    /**
     * 返回参数错误响应
     */
    protected <T> ResponseEntity<Result<T>> badRequest(String message) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(Result.error(400, message));
    }

    /**
     * 返回未授权响应
     */
    protected <T> ResponseEntity<Result<T>> unauthorized(String message) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Result.error(401, message));
    }

    /**
     * 返回禁止访问响应
     */
    protected <T> ResponseEntity<Result<T>> forbidden(String message) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(Result.error(403, message));
    }

    /**
     * 返回资源未找到响应
     */
    protected <T> ResponseEntity<Result<T>> notFound(String message) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Result.error(404, message));
    }
}
