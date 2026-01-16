package com.platform.platformserver.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.mapper.ApiInfoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

@Component
public class SwaggerImportUtil {

    @Autowired
    private ApiInfoMapper apiInfoMapper;

    private final ObjectMapper jsonMapper = new ObjectMapper();
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());

    public int importSwagger(String content, Long projectId) throws IOException {
        JsonNode rootNode;
        try {
            rootNode = yamlMapper.readTree(content);
        } catch (IOException e) {
            rootNode = jsonMapper.readTree(content);
        }

        List<ApiInfo> apiInfoList = new ArrayList<>();
        JsonNode pathsNode = rootNode.path("paths");

        Iterator<Map.Entry<String, JsonNode>> pathIterator = pathsNode.fields();
        while (pathIterator.hasNext()) {
            Map.Entry<String, JsonNode> pathEntry = pathIterator.next();
            String path = pathEntry.getKey();
            JsonNode methodsNode = pathEntry.getValue();

            Iterator<Map.Entry<String, JsonNode>> methodIterator = methodsNode.fields();
            while (methodIterator.hasNext()) {
                Map.Entry<String, JsonNode> methodEntry = methodIterator.next();
                String method = methodEntry.getKey().toUpperCase();
                JsonNode details = methodEntry.getValue();

                if (isValidMethod(method)) {
                    ApiInfo apiInfo = buildApiInfo(details, path, method, projectId);
                    apiInfoList.add(apiInfo);
                }
            }
        }

        for (ApiInfo apiInfo : apiInfoList) {
            apiInfoMapper.insert(apiInfo);
        }

        return apiInfoList.size();
    }

    private boolean isValidMethod(String method) {
        return method.equals("GET") || method.equals("POST") || 
               method.equals("PUT") || method.equals("DELETE") || 
               method.equals("PATCH");
    }

    private ApiInfo buildApiInfo(JsonNode details, String path, String method, Long projectId) {
        ApiInfo apiInfo = new ApiInfo();
        apiInfo.setProjectId(projectId);
        apiInfo.setApiName(details.has("summary") ? details.get("summary").asText() : method + " " + path);
        apiInfo.setRequestMethod(method);
        apiInfo.setRequestUrl(path);
        apiInfo.setRequestParams(extractParameters(details));
        apiInfo.setRequestHeaders(extractHeaders(details));
        apiInfo.setDebugVars("{}");
        apiInfo.setRequestFormDatas("{}");
        apiInfo.setRequestWwwFormDatas("{}");
        apiInfo.setRequestsJsonData(extractRequestBody(details));
        apiInfo.setRequestFiles("{}");
        return apiInfo;
    }

    private String extractParameters(JsonNode details) {
        try {
            JsonNode parameters = details.path("parameters");
            return jsonMapper.writeValueAsString(parameters);
        } catch (Exception e) {
            return "[]";
        }
    }

    private String extractHeaders(JsonNode details) {
        try {
            JsonNode responses = details.path("responses");
            return jsonMapper.writeValueAsString(responses);
        } catch (Exception e) {
            return "{}";
        }
    }

    private String extractRequestBody(JsonNode details) {
        try {
            JsonNode requestBody = details.path("requestBody");
            JsonNode content = requestBody.path("content");
            if (content.isObject()) {
                Iterator<Map.Entry<String, JsonNode>> contentIterator = content.fields();
                if (contentIterator.hasNext()) {
                    Map.Entry<String, JsonNode> contentType = contentIterator.next();
                    JsonNode schema = contentType.getValue().path("schema");
                    return jsonMapper.writeValueAsString(schema);
                }
            }
            return "{}";
        } catch (Exception e) {
            return "{}";
        }
    }
}
