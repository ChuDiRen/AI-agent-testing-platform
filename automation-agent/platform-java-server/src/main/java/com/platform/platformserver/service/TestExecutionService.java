package com.platform.platformserver.service;

import com.platform.platformserver.common.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Slf4j
@Service
public class TestExecutionService {
    
    @Autowired
    private RabbitMQProducer rabbitMQProducer;
    
    @Autowired
    private RealTestExecutionService realTestExecutionService;
    
    public Result<Map<String, Object>> executeTestCase(Long caseId) {
        try {
            // 使用真实的CLI执行功能
            return realTestExecutionService.executeTestCase(caseId);
        } catch (Exception e) {
            log.error("测试用例执行失败: caseId={}", caseId, e);
            return Result.error("测试用例执行失败: " + e.getMessage());
        }
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
        try {
            // 解析测试计划中的用例ID列表
            List<Long> caseIds = parseTestPlan(testPlan);
            
            // 使用真实的批量执行功能
            return realTestExecutionService.executeBatchTest(caseIds);
            
        } catch (Exception e) {
            log.error("批量测试执行失败: testPlan={}", testPlan, e);
            return Result.error("批量测试执行失败: " + e.getMessage());
        }
    }
    
    private List<Long> parseTestPlan(String testPlan) {
        // 简单的测试计划解析，实际项目中可能需要更复杂的解析逻辑
        List<Long> caseIds = new ArrayList<>();
        if (testPlan != null && !testPlan.trim().isEmpty()) {
            String[] ids = testPlan.split(",");
            for (String id : ids) {
                try {
                    caseIds.add(Long.parseLong(id.trim()));
                } catch (NumberFormatException e) {
                    log.warn("无效的用例ID: {}", id);
                }
            }
        }
        return caseIds;
    }
}