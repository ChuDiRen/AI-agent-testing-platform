package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@Tag(name = "系统", description = "系统相关接口")
public class SystemController {
    
    @GetMapping("/")
    @Operation(summary = "根路径", description = "系统根路径")
    public Result<Map<String, Object>> root() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "API 测试平台后端服务 - Java");
        response.put("version", "1.0.0");
        return Result.success(response);
    }
    
    @GetMapping("/health")
    @Operation(summary = "健康检查", description = "系统健康检查接口")
    public Result<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("framework", "Spring Boot");
        response.put("version", "1.0.0");
        return Result.success(response);
    }
}
