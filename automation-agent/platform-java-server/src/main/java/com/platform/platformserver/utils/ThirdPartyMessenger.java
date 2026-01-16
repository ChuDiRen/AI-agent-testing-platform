package com.platform.platformserver.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

@Slf4j
@Component
public class ThirdPartyMessenger {

    @Autowired
    private RestTemplate restTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public Map<String, Object> sendWechatMessage(String webhookUrl, String message, String keywords) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("msgtype", "text");
            
            Map<String, Object> text = new HashMap<>();
            text.put("content", message);
            if (keywords != null && !keywords.isEmpty()) {
                List<String> mentionedList = Arrays.asList(keywords.split(","));
                text.put("mentioned_list", mentionedList);
            }
            payload.put("text", text);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(webhookUrl, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                log.info("企业微信消息发送成功: {}", response.getBody());
                @SuppressWarnings("unchecked")
                Map<String, Object> resultMap = (Map<String, Object>) objectMapper.readValue(response.getBody(), Map.class);
                return resultMap;
            } else {
                log.error("企业微信消息发送失败: {}", response.getBody());
                return createErrorResponse("发送失败");
            }
        } catch (Exception e) {
            log.error("发送企业微信消息异常", e);
            return createErrorResponse("发送异常: " + e.getMessage());
        }
    }

    public Map<String, Object> sendDingtalkMessage(String webhookUrl, String message, String keywords) {
        try {
            String webhookUrlWithSign = webhookUrl;
            
            if (keywords != null && !keywords.isEmpty()) {
                @SuppressWarnings("unchecked")
                Map<String, Object> keywordsMap = (Map<String, Object>) objectMapper.readValue(keywords, Map.class);
                String secret = (String) keywordsMap.get("secret_key");
                
                long timestamp = System.currentTimeMillis();
                String stringToSign = timestamp + "\n" + secret;
                
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
                byte[] signData = mac.doFinal(stringToSign.getBytes(StandardCharsets.UTF_8));
                String sign = Base64.getEncoder().encodeToString(signData);
                sign = URLEncoder.encode(sign, "UTF-8");
                
                webhookUrlWithSign = webhookUrl + "&timestamp=" + timestamp + "&sign=" + sign;
            }
            
            Map<String, Object> data = new HashMap<>();
            data.put("msgtype", "text");
            
            Map<String, Object> text = new HashMap<>();
            text.put("content", message);
            text.put("mentioned_list", Arrays.asList("@all"));
            data.put("text", text);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(webhookUrlWithSign, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                log.info("钉钉消息发送成功: {}", response.getBody());
                @SuppressWarnings("unchecked")
                Map<String, Object> resultMap = (Map<String, Object>) objectMapper.readValue(response.getBody(), Map.class);
                return resultMap;
            } else {
                log.error("钉钉消息发送失败: {}", response.getBody());
                return createErrorResponse("发送失败");
            }
        } catch (Exception e) {
            log.error("发送钉钉消息异常", e);
            return createErrorResponse("发送异常: " + e.getMessage());
        }
    }

    public Map<String, Object> sendFeishuMessage(String webhookUrl, String message, String keywords) {
        try {
            Map<String, Object> data = new HashMap<>();
            
            if (keywords != null && !keywords.isEmpty()) {
                @SuppressWarnings("unchecked")
                Map<String, Object> keywordsMap = (Map<String, Object>) objectMapper.readValue(keywords, Map.class);
                String secret = (String) keywordsMap.get("sign");
                
                long timestamp = System.currentTimeMillis();
                String stringToSign = timestamp + "\n" + secret;
                
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                byte[] hash = md.digest(stringToSign.getBytes(StandardCharsets.UTF_8));
                String sign = Base64.getEncoder().encodeToString(hash);
                
                data.put("sign", sign);
            }
            
            data.put("msg_type", "text");
            Map<String, String> content = new HashMap<>();
            content.put("text", message);
            data.put("content", content);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(webhookUrl, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                log.info("飞书消息发送成功: {}", response.getBody());
                @SuppressWarnings("unchecked")
                Map<String, Object> resultMap = (Map<String, Object>) objectMapper.readValue(response.getBody(), Map.class);
                return resultMap;
            } else {
                log.error("飞书消息发送失败: {}", response.getBody());
                return createErrorResponse("发送失败");
            }
        } catch (Exception e) {
            log.error("发送飞书消息异常", e);
            return createErrorResponse("发送异常: " + e.getMessage());
        }
    }

    public Map<String, Object> sendMessage(Map<String, Object> caseCollectionInfo, String collType, Map<String, Object> testResult) {
        try {
            String messageTemplate = (String) testResult.get("message_template");
            String message = messageTemplate.replace("{{coll_name}}", (String) caseCollectionInfo.get("collection_name"));
            message = message.replace("{{status}}", (String) testResult.get("status"));
            
            String reportUrl;
            String reportBaseUrl = getReportBaseUrl(collType);
            reportUrl = reportBaseUrl + "/" + testResult.get("detail") + "/index.html";
            message = message.replace("{{report_url}}", reportUrl);
            
            Object robotConfigObj = testResult.get("robot_config");
            Map<String, Object> robotConfig;
            if (robotConfigObj instanceof Map) {
                robotConfig = (Map<String, Object>) robotConfigObj;
            } else {
                robotConfig = new HashMap<>();
            }
            
            String robotType = robotConfig != null ? String.valueOf(robotConfig.get("robot_type")) : "";
            String webhookUrl = robotConfig != null ? (String) robotConfig.get("webhook_url") : "";
            String keywords = robotConfig != null ? (String) robotConfig.get("keywords") : "";
            
            if (robotType.equals("1") || robotType.equals("企业微信")) {
                log.info("---发送企业微信消息---");
                return sendWechatMessage(webhookUrl, message, keywords);
            } else if (robotType.equals("2") || robotType.equals("钉钉")) {
                log.info("---发送钉钉消息---");
                return sendDingtalkMessage(webhookUrl, message, keywords);
            } else if (robotType.equals("3") || robotType.equals("飞书")) {
                log.info("---发送飞书消息---");
                return sendFeishuMessage(webhookUrl, message, keywords);
            } else {
                return createErrorResponse("未知的机器人类型");
            }
        } catch (Exception e) {
            log.error("发送消息异常", e);
            return createErrorResponse("服务器错误,请联系管理员: " + e.getMessage());
        }
    }

    private String getReportBaseUrl(String collType) {
        switch (collType) {
            case "web":
                return "http://127.0.0.1:8080/ApiReportViewer";
            case "app":
                return "http://127.0.0.1:8080";
            case "api":
                return "http://127.0.0.1:8080/ApiReportViewer";
            default:
                return "http://127.0.0.1:8080";
        }
    }

    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return response;
    }
}
