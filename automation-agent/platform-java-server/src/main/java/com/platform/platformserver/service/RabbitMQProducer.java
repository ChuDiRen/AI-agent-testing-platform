package com.platform.platformserver.service;

import com.platform.platformserver.config.RabbitMQConfig;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class RabbitMQProducer {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public void sendTestExecutionMessage(Long caseId, String testType) {
        Map<String, Object> message = new HashMap<>();
        message.put("caseId", caseId);
        message.put("testType", testType);
        message.put("timestamp", System.currentTimeMillis());
        
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.TEST_EXECUTION_EXCHANGE,
            RabbitMQConfig.TEST_EXECUTION_ROUTING_KEY,
            message
        );
    }
    
    public void sendTestResultMessage(Long caseId, String status, String result) {
        Map<String, Object> message = new HashMap<>();
        message.put("caseId", caseId);
        message.put("status", status);
        message.put("result", result);
        message.put("timestamp", System.currentTimeMillis());
        
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.TEST_RESULT_EXCHANGE,
            RabbitMQConfig.TEST_RESULT_ROUTING_KEY,
            message
        );
    }
}