package com.platform.platformserver.service;

import com.platform.platformserver.config.RabbitMQConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class RabbitMQConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(RabbitMQConsumer.class);
    
    @Autowired
    private TestExecutionService testExecutionService;
    
    @RabbitListener(queues = RabbitMQConfig.TEST_EXECUTION_QUEUE)
    public void handleTestExecutionMessage(Map<String, Object> message) {
        logger.info("收到测试执行消息: {}", message);
        try {
            Long caseId = Long.valueOf(message.get("caseId").toString());
            String testType = message.get("testType").toString();
            
            logger.info("开始执行测试用例: {}, 类型: {}", caseId, testType);
            testExecutionService.executeTestCase(caseId);
            logger.info("测试用例执行完成: {}", caseId);
            
        } catch (Exception e) {
            logger.error("测试执行失败: {}", e.getMessage(), e);
        }
    }
    
    @RabbitListener(queues = RabbitMQConfig.TEST_RESULT_QUEUE)
    public void handleTestResultMessage(Map<String, Object> message) {
        logger.info("收到测试结果消息: {}", message);
        try {
            Long caseId = Long.valueOf(message.get("caseId").toString());
            String status = message.get("status").toString();
            String result = message.get("result").toString();
            
            logger.info("处理测试结果 - 用例ID: {}, 状态: {}, 结果: {}", caseId, status, result);
            // 这里可以添加处理测试结果的逻辑
            
        } catch (Exception e) {
            logger.error("处理测试结果失败: {}", e.getMessage(), e);
        }
    }
}