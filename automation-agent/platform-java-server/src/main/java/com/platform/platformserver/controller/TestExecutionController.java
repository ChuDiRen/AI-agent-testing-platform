package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.service.TestExecutionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/test-execution")
public class TestExecutionController {
    
    @Autowired
    private TestExecutionService testExecutionService;
    
    @PostMapping("/execute/{caseId}")
    public Result<Map<String, Object>> executeTestCase(@PathVariable Long caseId) {
        return testExecutionService.executeTestCase(caseId);
    }
    
    @PostMapping("/execute-async/{caseId}")
    public Result<String> executeTestCaseAsync(@PathVariable Long caseId, @RequestParam(defaultValue = "single") String testType) {
        return testExecutionService.sendTestExecutionMessage(caseId, testType);
    }
    
    @PostMapping("/execute-batch")
    public Result<Map<String, Object>> executeBatchTest(@RequestBody Map<String, Object> testPlan) {
        String plan = testPlan.getOrDefault("testPlan", "").toString();
        return testExecutionService.executeBatchTest(plan);
    }
}