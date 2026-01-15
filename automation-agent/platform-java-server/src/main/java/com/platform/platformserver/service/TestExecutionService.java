package com.platform.platformserver.service;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiHistory;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.entity.ApiInfoCase;
import com.platform.platformserver.mapper.ApiHistoryMapper;
import com.platform.platformserver.mapper.ApiInfoCaseMapper;
import com.platform.platformserver.mapper.ApiInfoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
public class TestExecutionService {
    
    @Autowired
    private ApiInfoCaseMapper apiInfoCaseMapper;
    
    @Autowired
    private ApiInfoMapper apiInfoMapper;
    
    @Autowired
    private ApiHistoryMapper apiHistoryMapper;
    
    @Autowired
    private RabbitMQProducer rabbitMQProducer;
    
    public Result<Map<String, Object>> executeTestCase(Long caseId) {
        ApiInfoCase testCase = apiInfoCaseMapper.selectById(caseId);
        if (testCase == null) {
            return Result.error("测试用例不存在");
        }
        
        ApiInfo apiInfo = apiInfoMapper.selectById(testCase.getApiId());
        if (apiInfo == null) {
            return Result.error("API信息不存在");
        }
        
        // 模拟测试执行
        Map<String, Object> result = new HashMap<>();
        result.put("caseId", caseId);
        result.put("status", "success");
        result.put("responseTime", 150);
        result.put("responseCode", 200);
        result.put("responseBody", "{\"message\":\"测试成功\"}");
        
        // 记录历史
        ApiHistory history = new ApiHistory();
        history.setCaseId(caseId);
        history.setStatus("success");
        history.setResponseTime(150L);
        history.setResponseCode(200);
        history.setResponseBody("{\"message\":\"测试成功\"}");
        history.setExecuteTime(LocalDateTime.now());
        apiHistoryMapper.insert(history);
        
        // 发送RabbitMQ消息
        rabbitMQProducer.sendTestResultMessage(caseId, "success", "{\"message\":\"测试成功\"}");
        
        return Result.success(result);
    }
    
    public Result<String> sendTestExecutionMessage(Long caseId, String testType) {
        try {
            rabbitMQProducer.sendTestExecutionMessage(caseId, testType);
            return Result.success("测试执行消息已发送到队列");
        } catch (Exception e) {
            return Result.error("发送测试执行消息失败: " + e.getMessage());
        }
    }
    
    public Result<Map<String, Object>> executeBatchTest(String testPlan) {
        // 批量测试执行逻辑
        Map<String, Object> result = new HashMap<>();
        result.put("testPlan", testPlan);
        result.put("totalCases", 10);
        result.put("passedCases", 8);
        result.put("failedCases", 2);
        result.put("executionTime", 1200);
        
        return Result.success(result);
    }
}