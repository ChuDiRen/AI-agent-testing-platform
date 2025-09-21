// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.controller;

import com.example.aiagent.dto.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 测试控制器
 * 提供基础的API测试接口
 *
 * @author 左岚团队
 * @version 1.0.0
 */
@RestController
@RequestMapping("/test")
@Tag(name = "测试接口", description = "用于测试API功能的基础接口")
public class TestController extends BaseController {

    /**
     * 健康检查接口
     */
    @GetMapping("/health")
    @Operation(summary = "健康检查", description = "检查服务是否正常运行")
    public ResponseEntity<Result<Map<String, Object>>> health() {
        Map<String, Object> data = new HashMap<>();
        data.put("status", "UP");
        data.put("timestamp", LocalDateTime.now());
        data.put("service", "AI Agent Testing Platform");
        data.put("version", "1.0.0");
        
        return success(data, "服务运行正常");
    }

    /**
     * Echo测试接口
     */
    @PostMapping("/echo")
    @Operation(summary = "Echo测试", description = "返回发送的消息")
    public ResponseEntity<Result<Map<String, Object>>> echo(@RequestBody Map<String, Object> request) {
        Map<String, Object> data = new HashMap<>();
        data.put("received", request);
        data.put("timestamp", LocalDateTime.now());
        data.put("echo", "Message received successfully");
        
        return success(data, "Echo测试成功");
    }

    /**
     * 获取服务信息
     */
    @GetMapping("/info")
    @Operation(summary = "服务信息", description = "获取服务基本信息")
    public ResponseEntity<Result<Map<String, Object>>> info() {
        Map<String, Object> data = new HashMap<>();
        data.put("name", "AI Agent Testing Platform");
        data.put("version", "1.0.0");
        data.put("description", "AI智能代理测试平台后端服务");
        data.put("author", "左岚团队");
        data.put("timestamp", LocalDateTime.now());
        
        return success(data, "获取服务信息成功");
    }

    /**
     * 测试参数接口
     */
    @GetMapping("/param")
    @Operation(summary = "参数测试", description = "测试URL参数和查询参数")
    public ResponseEntity<Result<Map<String, Object>>> testParam(
            @RequestParam(value = "name", defaultValue = "Guest") String name,
            @RequestParam(value = "age", required = false) Integer age) {
        
        Map<String, Object> data = new HashMap<>();
        data.put("name", name);
        data.put("age", age);
        data.put("message", "Hello, " + name + "!");
        data.put("timestamp", LocalDateTime.now());
        
        return success(data, "参数测试成功");
    }
}
