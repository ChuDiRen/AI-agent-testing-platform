// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.controller;

import com.example.aiagent.dto.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 根路径控制器 - 提供API信息和导航
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
@RestController
@RequestMapping("/")
@Tag(name = "根路径接口", description = "提供API信息和可用端点导航")
public class RootController extends BaseController {

    /**
     * API欢迎页面和信息
     */
    @GetMapping
    @Operation(summary = "API信息", description = "获取API基本信息和可用端点列表")
    public ResponseEntity<Result<Map<String, Object>>> apiInfo() {
        Map<String, Object> data = new HashMap<>();
        
        // 基本信息
        data.put("name", "AI Agent Testing Platform API");
        data.put("version", "1.0.0");
        data.put("description", "AI智能代理测试平台后端服务");
        data.put("author", "左岚团队");
        data.put("timestamp", LocalDateTime.now());
        data.put("status", "运行中");
        
        // 可用端点列表
        List<Map<String, String>> endpoints = new ArrayList<>();
        
        // 测试接口
        Map<String, String> healthEndpoint = new HashMap<>();
        healthEndpoint.put("path", "/api/test/health");
        healthEndpoint.put("method", "GET");
        healthEndpoint.put("description", "健康检查接口");
        endpoints.add(healthEndpoint);
        
        Map<String, String> infoEndpoint = new HashMap<>();
        infoEndpoint.put("path", "/api/test/info");
        infoEndpoint.put("method", "GET");
        infoEndpoint.put("description", "服务信息接口");
        endpoints.add(infoEndpoint);
        
        Map<String, String> echoEndpoint = new HashMap<>();
        echoEndpoint.put("path", "/api/test/echo");
        echoEndpoint.put("method", "POST");
        echoEndpoint.put("description", "Echo测试接口");
        endpoints.add(echoEndpoint);
        
        Map<String, String> paramEndpoint = new HashMap<>();
        paramEndpoint.put("path", "/api/test/param");
        paramEndpoint.put("method", "GET");
        paramEndpoint.put("description", "参数测试接口");
        endpoints.add(paramEndpoint);
        
        // API文档
        Map<String, String> docsEndpoint = new HashMap<>();
        docsEndpoint.put("path", "/api/swagger-ui.html");
        docsEndpoint.put("method", "GET");
        docsEndpoint.put("description", "API文档界面");
        endpoints.add(docsEndpoint);
        
        data.put("endpoints", endpoints);
        
        return success(data, "欢迎使用AI Agent Testing Platform API");
    }
}