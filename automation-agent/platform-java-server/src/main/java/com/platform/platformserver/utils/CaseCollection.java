package com.platform.platformserver.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Slf4j
@Component
public class CaseCollection {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public List<Map<String, Object>> generateHistoryInfo(String collType, Map<String, Object> caseCollectionInfo, 
                                                           String reportDataPath, String executeUuid) {
        List<Map<String, Object>> historyList = new ArrayList<>();
        
        try {
            File reportDir = new File(reportDataPath);
            if (!reportDir.exists() || !reportDir.isDirectory()) {
                return historyList;
            }

            File[] files = reportDir.listFiles((dir, name) -> name.endsWith("result.json"));
            if (files == null) {
                return historyList;
            }

            for (File file : files) {
                try {
                    JsonNode data = objectMapper.readTree(file);
                    if (data != null && !data.isEmpty()) {
                        String name = data.has("name") ? data.get("name").asText() : "";
                        String status = data.has("status") ? data.get("status").asText() : "";
                        long start = data.has("start") ? data.get("start").asLong() : 0;
                        long stop = data.has("stop") ? data.get("stop").asLong() : 0;
                        long duration = stop - start;

                        Map<String, Object> historyRecord = new HashMap<>();
                        historyRecord.put("name", name);
                        historyRecord.put("status", status);
                        historyRecord.put("type", collType);
                        historyRecord.put("project_id", caseCollectionInfo.get("project_id"));
                        historyRecord.put("coll_id", caseCollectionInfo.get("id"));
                        historyRecord.put("duration", duration);
                        historyRecord.put("create_time", LocalDateTime.now().format(formatter));
                        historyRecord.put("detail", executeUuid);

                        historyList.add(historyRecord);
                    }
                } catch (IOException e) {
                    log.error("解析结果文件失败: {}", file.getName(), e);
                }
            }
        } catch (Exception e) {
            log.error("生成历史记录信息失败", e);
        }

        return historyList;
    }

    public Map<String, Object> parseResultFile(String resultFilePath) {
        try {
            File file = new File(resultFilePath);
            if (file.exists()) {
                JsonNode data = objectMapper.readTree(file);
                @SuppressWarnings("unchecked")
                Map<String, Object> result = (Map<String, Object>) objectMapper.convertValue(data, Map.class);
                return result;
            }
        } catch (Exception e) {
            log.error("解析结果文件失败: {}", resultFilePath, e);
        }
        return new HashMap<>();
    }

    public List<String> listReportFiles(String reportDir) {
        try {
            File dir = new File(reportDir);
            if (dir.exists() && dir.isDirectory()) {
                File[] files = dir.listFiles();
                if (files != null) {
                    List<String> fileList = new ArrayList<>();
                    for (File file : files) {
                        fileList.add(file.getName());
                    }
                    return fileList;
                }
            }
        } catch (Exception e) {
            log.error("列出报告文件失败: {}", reportDir, e);
        }
        return new ArrayList<>();
    }

    public Map<String, Object> createHistoryRecords(String collType, Map<String, Object> caseCollectionInfo,
                                                   Map<String, Object> executionData, String reportDir) {
        Map<String, Object> historyRecord = new HashMap<>();
        historyRecord.put("name", caseCollectionInfo.get("collection_name"));
        historyRecord.put("status", executionData.getOrDefault("status", "completed"));
        historyRecord.put("type", collType);
        historyRecord.put("project_id", caseCollectionInfo.get("project_id"));
        historyRecord.put("coll_id", caseCollectionInfo.get("id"));
        historyRecord.put("duration", executionData.getOrDefault("duration", 0));
        historyRecord.put("create_time", LocalDateTime.now().format(formatter));
        historyRecord.put("detail", executionData.get("execute_uuid"));
        return historyRecord;
    }
}
