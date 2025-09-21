// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * AI Agent Testing Platform - SpringBoot应用程序入口类
 *
 * @author 左岚团队
 * @version 1.0.0
 */
@SpringBootApplication(exclude = {
    org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class,
    com.baomidou.mybatisplus.autoconfigure.MybatisPlusAutoConfiguration.class,
    org.springframework.boot.autoconfigure.security.servlet.SecurityFilterAutoConfiguration.class
})
// @MapperScan("com.example.aiagent.mapper") // 暂时禁用
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}