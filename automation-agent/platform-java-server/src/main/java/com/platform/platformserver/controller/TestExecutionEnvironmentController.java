package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.service.RealTestExecutionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.Map;

/**
 * 测试执行环境检查控制器
 */
@RestController
@RequestMapping("/api/v1/TestExecution")
public class TestExecutionEnvironmentController {
    
    @Autowired
    private RealTestExecutionService realTestExecutionService;
    
    /**
     * 检查测试执行环境
     */
    @GetMapping("/check-environment")
    public Result<Map<String, Object>> checkEnvironment() {
        return realTestExecutionService.checkExecutionEnvironment();
    }
    
    /**
     * 执行单个测试用例
     */
    @PostMapping("/execute/{caseId}")
    public Result<Map<String, Object>> executeTestCase(@PathVariable Long caseId) {
        return realTestExecutionService.executeTestCase(caseId);
    }
    
    /**
     * 批量执行测试用例
     */
    @PostMapping("/execute-batch")
    public Result<Map<String, Object>> executeBatchTest(@RequestBody Map<String, Object> request) {
        return realTestExecutionService.executeBatchTest(Arrays.asList(1L, 2L, 3L)); // 示例用例ID
    }
}
