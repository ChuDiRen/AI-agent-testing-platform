// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.util;

/**
 * 系统常量类
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
public class Constants {

    // 系统相关常量
    public static final String SYSTEM_NAME = "AI Agent Testing Platform";
    public static final String SYSTEM_VERSION = "1.0.0";
    public static final String SYSTEM_AUTHOR = "左岚团队";

    // 用户状态常量
    public static final int USER_STATUS_DISABLED = 0;
    public static final int USER_STATUS_ENABLED = 1;

    // 角色状态常量
    public static final int ROLE_STATUS_DISABLED = 0;
    public static final int ROLE_STATUS_ENABLED = 1;

    // 逻辑删除常量
    public static final int DELETED_FALSE = 0;
    public static final int DELETED_TRUE = 1;

    // 默认密码
    public static final String DEFAULT_PASSWORD = "123456";

    // 分页常量
    public static final int DEFAULT_PAGE_SIZE = 20;
    public static final int MAX_PAGE_SIZE = 100;

    // 缓存相关常量
    public static final String CACHE_PREFIX = "ai_agent:";
    public static final int CACHE_EXPIRE_TIME = 3600; // 1小时

    // JWT相关常量
    public static final String JWT_HEADER = "Authorization";
    public static final String JWT_PREFIX = "Bearer ";
    public static final long JWT_EXPIRATION = 86400; // 24小时

    // 文件上传常量
    public static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    public static final String UPLOAD_PATH = "/uploads/";

    // 日期时间格式常量
    public static final String DATE_FORMAT = "yyyy-MM-dd";
    public static final String DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
    public static final String TIME_FORMAT = "HH:mm:ss";

    // 字符编码常量
    public static final String UTF8 = "UTF-8";
    public static final String GBK = "GBK";

    // HTTP相关常量
    public static final String CONTENT_TYPE_JSON = "application/json";
    public static final String CONTENT_TYPE_FORM = "application/x-www-form-urlencoded";
    public static final String CONTENT_TYPE_MULTIPART = "multipart/form-data";

    private Constants() {
        // 工具类，禁止实例化
    }
}
