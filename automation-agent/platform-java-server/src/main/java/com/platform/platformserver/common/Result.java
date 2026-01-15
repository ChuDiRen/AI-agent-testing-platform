package com.platform.platformserver.common;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> implements Serializable {
    private int code;
    private String message;
    private T data;
    private long timestamp;

    public static <T> Result<T> success() {
        return new Result<>(ResultCode.SUCCESS.getCode(), ResultCode.SUCCESS.getMessage(), null, System.currentTimeMillis());
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(ResultCode.SUCCESS.getCode(), ResultCode.SUCCESS.getMessage(), data, System.currentTimeMillis());
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(ResultCode.SUCCESS.getCode(), message, data, System.currentTimeMillis());
    }

    public static <T> Result<T> error() {
        return new Result<>(ResultCode.ERROR.getCode(), ResultCode.ERROR.getMessage(), null, System.currentTimeMillis());
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(ResultCode.ERROR.getCode(), message, null, System.currentTimeMillis());
    }

    public static <T> Result<T> error(ResultCode resultCode) {
        return new Result<>(resultCode.getCode(), resultCode.getMessage(), null, System.currentTimeMillis());
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null, System.currentTimeMillis());
    }

    public static <T> Result<T> unauthorized() {
        return new Result<>(ResultCode.UNAUTHORIZED.getCode(), ResultCode.UNAUTHORIZED.getMessage(), null, System.currentTimeMillis());
    }

    public static <T> Result<T> forbidden() {
        return new Result<>(ResultCode.FORBIDDEN.getCode(), ResultCode.FORBIDDEN.getMessage(), null, System.currentTimeMillis());
    }
}
