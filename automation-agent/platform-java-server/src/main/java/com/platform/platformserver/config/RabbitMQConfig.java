package com.platform.platformserver.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {
    
    // 测试执行队列
    public static final String TEST_EXECUTION_QUEUE = "test.execution.queue";
    public static final String TEST_EXECUTION_EXCHANGE = "test.execution.exchange";
    public static final String TEST_EXECUTION_ROUTING_KEY = "test.execution.key";
    
    // 测试结果队列
    public static final String TEST_RESULT_QUEUE = "test.result.queue";
    public static final String TEST_RESULT_EXCHANGE = "test.result.exchange";
    public static final String TEST_RESULT_ROUTING_KEY = "test.result.key";
    
    @Bean
    public Queue testExecutionQueue() {
        return new Queue(TEST_EXECUTION_QUEUE, true);
    }
    
    @Bean
    public Queue testResultQueue() {
        return new Queue(TEST_RESULT_QUEUE, true);
    }
    
    @Bean
    public DirectExchange testExecutionExchange() {
        return new DirectExchange(TEST_EXECUTION_EXCHANGE);
    }
    
    @Bean
    public DirectExchange testResultExchange() {
        return new DirectExchange(TEST_RESULT_EXCHANGE);
    }
    
    @Bean
    public Binding testExecutionBinding() {
        return BindingBuilder
                .bind(testExecutionQueue())
                .to(testExecutionExchange())
                .with(TEST_EXECUTION_ROUTING_KEY);
    }
    
    @Bean
    public Binding testResultBinding() {
        return BindingBuilder
                .bind(testResultQueue())
                .to(testResultExchange())
                .with(TEST_RESULT_ROUTING_KEY);
    }
    
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }
    
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(jsonMessageConverter());
        return rabbitTemplate;
    }
}