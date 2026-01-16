package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.entity.ApiKeyWord;
import com.platform.platformserver.entity.ApiOperationType;
import com.platform.platformserver.mapper.ApiInfoMapper;
import com.platform.platformserver.mapper.ApiKeyWordMapper;
import com.platform.platformserver.mapper.ApiOperationTypeMapper;
import com.platform.platformserver.utils.SwaggerImportUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class ApiInfoService {
    
    @Autowired
    private ApiInfoMapper apiInfoMapper;
    
    @Autowired
    private SwaggerImportUtil swaggerImportUtil;
    
    @Autowired
    private ApiOperationTypeMapper apiOperationTypeMapper;
    
    @Autowired
    private ApiKeyWordMapper apiKeyWordMapper;
    
    public Result<Map<String, Object>> queryByPage(Integer page, Integer page_size, Long project_id, Long module_id, String api_name) {
        QueryWrapper<ApiInfo> queryWrapper = new QueryWrapper<>();
        
        if (project_id != null) {
            queryWrapper.eq("project_id", project_id);
        }
        if (module_id != null) {
            queryWrapper.eq("module_id", module_id);
        }
        if (api_name != null && !api_name.isEmpty()) {
            queryWrapper.like("api_name", api_name);
        }
        
        queryWrapper.orderByDesc("id");
        
        Page<ApiInfo> pageResult = new Page<>(page != null ? page : 1, page_size != null ? page_size : 10);
        Page<ApiInfo> resultPage = apiInfoMapper.selectPage(pageResult, queryWrapper);
        
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("data", resultPage.getRecords());
        resultMap.put("total", resultPage.getTotal());
        
        return Result.success(resultMap);
    }
    
    public Result<ApiInfo> queryById(Long id) {
        ApiInfo apiInfo = apiInfoMapper.selectById(id);
        if (apiInfo == null) {
            return Result.error("查询成功,但是没有数据");
        }
        return Result.success(apiInfo);
    }
    
    public Result<Map<String, Object>> insert(ApiInfo apiInfo) {
        apiInfoMapper.insert(apiInfo);
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("id", apiInfo.getId());
        return Result.success("生成文件成功", resultMap);
    }
    
    public Result<String> update(Long id, ApiInfo apiInfo) {
        ApiInfo existingApiInfo = apiInfoMapper.selectById(id);
        if (existingApiInfo == null) {
            return Result.error("数据不存在");
        }
        
        existingApiInfo.setProjectId(apiInfo.getProjectId());
        existingApiInfo.setModuleId(apiInfo.getModuleId());
        existingApiInfo.setApiName(apiInfo.getApiName());
        existingApiInfo.setRequestMethod(apiInfo.getRequestMethod());
        existingApiInfo.setRequestUrl(apiInfo.getRequestUrl());
        existingApiInfo.setRequestParams(apiInfo.getRequestParams());
        existingApiInfo.setRequestHeaders(apiInfo.getRequestHeaders());
        existingApiInfo.setDebugVars(apiInfo.getDebugVars());
        existingApiInfo.setRequestFormDatas(apiInfo.getRequestFormDatas());
        existingApiInfo.setRequestWwwFormDatas(apiInfo.getRequestWwwFormDatas());
        existingApiInfo.setRequestsJsonData(apiInfo.getRequestsJsonData());
        existingApiInfo.setRequestFiles(apiInfo.getRequestFiles());
        
        apiInfoMapper.updateById(existingApiInfo);
        return Result.success("修改成功");
    }
    
    public Result<String> delete(Long id) {
        apiInfoMapper.deleteById(id);
        return Result.success("删除成功");
    }
    
    public Result<Map<String, Object>> swaggerImport(MultipartFile file, Long project_id) {
        try {
            String content = new String(file.getBytes());
            int importedCount = swaggerImportUtil.importSwagger(content, project_id);
            
            Map<String, Object> resultMap = new HashMap<>();
            resultMap.put("imported_count", importedCount);
            
            return Result.success("成功导入 " + importedCount + " 个 API 接口", resultMap);
        } catch (IOException e) {
            return Result.error("Swagger 导入失败: " + e.getMessage());
        }
    }
    
    public Result<Map<String, Object>> debugExecute(Long id, Boolean download_response) {
        ApiInfo apiInfo = apiInfoMapper.selectById(id);
        if (apiInfo == null) {
            return Result.error("API信息不存在");
        }
        
        try {
            String casesDir = System.getProperty("user.dir") + File.separator + "test_cases";
            String executeUuid = UUID.randomUUID().toString();
            String runTmpDir = casesDir + File.separator + executeUuid;
            
            Files.createDirectories(Paths.get(runTmpDir));
            
            ObjectMapper objectMapper = new ObjectMapper();
            
            Map<String, Object> contextData = new HashMap<>();
            if (apiInfo.getDebugVars() != null && !apiInfo.getDebugVars().isEmpty() && !apiInfo.getDebugVars().equals("null")) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> tempContextData = objectMapper.readValue(apiInfo.getDebugVars(), Map.class);
                    contextData.putAll(tempContextData);
                } catch (Exception e) {
                    contextData = new HashMap<>();
                }
            }
            
            String contextYamlFile = runTmpDir + File.separator + "context.yaml";
            objectMapper.writeValue(new File(contextYamlFile), contextData);
            
            Map<String, Object> stepsInfo = new HashMap<>();
            stepsInfo.put("method", apiInfo.getRequestMethod());
            stepsInfo.put("url", apiInfo.getRequestUrl());
            
            if (download_response) {
                stepsInfo.put("关键字", "send_request_and_download");
            } else {
                stepsInfo.put("关键字", "send_request");
            }
            
            if (apiInfo.getRequestParams() != null && !apiInfo.getRequestParams().isEmpty()) {
                stepsInfo.put("params", apiInfo.getRequestParams());
            }
            
            if (apiInfo.getRequestHeaders() != null && !apiInfo.getRequestHeaders().isEmpty()) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, String> headersMap = (Map<String, String>) objectMapper.readValue(apiInfo.getRequestHeaders(), Map.class);
                    stepsInfo.put("headers", headersMap);
                } catch (Exception e) {
                    stepsInfo.put("headers", apiInfo.getRequestHeaders());
                }
            }
            
            if (apiInfo.getRequestsJsonData() != null && !apiInfo.getRequestsJsonData().isEmpty()) {
                stepsInfo.put("json", apiInfo.getRequestsJsonData());
            }
            
            Map<String, Object> testCaseData = new HashMap<>();
            testCaseData.put("desc", apiInfo.getApiName());
            Map<String, Object> stepWrapper = new HashMap<>();
            stepWrapper.put(apiInfo.getApiName(), stepsInfo);
            testCaseData.put("steps", List.of(stepWrapper));
            
            String testCaseFile = runTmpDir + File.separator + "test_case.yaml";
            objectMapper.writeValue(new File(testCaseFile), testCaseData);
            
            Map<String, Object> executionResult = new HashMap<>();
            executionResult.put("execute_uuid", executeUuid);
            executionResult.put("test_case_file", testCaseFile);
            executionResult.put("context_file", contextYamlFile);
            executionResult.put("status", "created");
            executionResult.put("message", "测试用例创建成功，等待执行");
            
            return Result.success("调试执行创建成功", executionResult);
            
        } catch (IOException e) {
            return Result.error("调试执行失败: " + e.getMessage());
        }
    }
    
    public Result<List<ApiInfo>> getApiInfoList(Long projectId) {
        QueryWrapper<ApiInfo> queryWrapper = new QueryWrapper<>();
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        queryWrapper.orderByDesc("id");
        List<ApiInfo> apiInfoList = apiInfoMapper.selectList(queryWrapper);
        return Result.success(apiInfoList);
    }
    
    public Result<ApiInfo> getApiInfoById(Long id) {
        ApiInfo apiInfo = apiInfoMapper.selectById(id);
        if (apiInfo == null) {
            return Result.error("API信息不存在");
        }
        return Result.success(apiInfo);
    }
    
    public Result<String> createApiInfo(ApiInfo apiInfo) {
        apiInfoMapper.insert(apiInfo);
        return Result.success("API信息创建成功");
    }
    
    public Result<String> updateApiInfo(ApiInfo apiInfo) {
        apiInfoMapper.updateById(apiInfo);
        return Result.success("API信息更新成功");
    }
    
    public Result<String> deleteApiInfo(Long id) {
        apiInfoMapper.deleteById(id);
        return Result.success("API信息删除成功");
    }
    
    public Result<Map<String, Object>> generateKeywordFile(String keywordFunName, String keywordValue) {
        try {
            // 关键字目录
            String keyWordsDir = System.getProperty("user.dir") + "/keywords";
            java.io.File dir = new java.io.File(keyWordsDir);
            if (!dir.exists()) {
                dir.mkdirs();
            }
            
            // 生成Python文件
            String filePath = keyWordsDir + "/" + keywordFunName + ".py";
            try (java.io.FileWriter writer = new java.io.FileWriter(filePath, false)) {
                writer.write(keywordValue);
            }
            
            Map<String, Object> result = new HashMap<>();
            result.put("id", keywordFunName);
            
            return Result.success("生成文件成功", result);
            
        } catch (Exception e) {
            return Result.error("生成文件失败: " + e.getMessage());
        }
    }
    
    public Result<List<Map<String, Object>>> queryAllKeyWordList() {
        try {
            List<Map<String, Object>> allDatas = new ArrayList<>();
            
            // 获取所有操作类型
            List<ApiOperationType> allOperationTypes = apiOperationTypeMapper.selectList(new QueryWrapper<>());
            
            for (ApiOperationType operationType : allOperationTypes) {
                Map<String, Object> apiData = new HashMap<>();
                apiData.put("id", operationType.getId());
                apiData.put("value", operationType.getOperationTypeFunName());
                apiData.put("label", operationType.getOperationTypeName());
                apiData.put("children", new ArrayList<>());
                
                // 查询当前操作类型对应的关键字
                QueryWrapper<ApiKeyWord> keywordQuery = new QueryWrapper<>();
                keywordQuery.eq("operation_type_id", operationType.getId());
                List<ApiKeyWord> keywordData = apiKeyWordMapper.selectList(keywordQuery);
                
                List<Map<String, Object>> children = new ArrayList<>();
                for (ApiKeyWord keyword : keywordData) {
                    Map<String, Object> child = new HashMap<>();
                    child.put("id", keyword.getId());
                    child.put("value", keyword.getKeywordFunName());
                    child.put("label", keyword.getName());
                    child.put("keyword_desc", keyword.getKeywordDesc());
                    children.add(child);
                }
                
                apiData.put("children", children);
                allDatas.add(apiData);
            }
            
            return Result.success(allDatas);
            
        } catch (Exception e) {
            return Result.error("查询失败: " + e.getMessage());
        }
    }
    
    // 新增缺失的方法 - 关键字相关
    public Result<List<ApiKeyWord>> getAllKeywords() {
        List<ApiKeyWord> list = apiKeyWordMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiKeyWord>> getKeywordsByPage(Integer page, Integer pageSize, String name) {
        Page<ApiKeyWord> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiKeyWord> queryWrapper = new QueryWrapper<>();
        if (name != null && !name.isEmpty()) {
            queryWrapper.like("name", name);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiKeyWord> resultPage = apiKeyWordMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<ApiKeyWord> getKeywordById(Long id) {
        ApiKeyWord keyword = apiKeyWordMapper.selectById(id);
        if (keyword == null) {
            return Result.error("关键字不存在");
        }
        return Result.success(keyword);
    }
    
    public Result<String> createKeyword(Map<String, Object> keywordMap) {
        ApiKeyWord keyword = new ApiKeyWord();
        if (keywordMap.containsKey("name")) {
            keyword.setName(keywordMap.get("name").toString());
        }
        if (keywordMap.containsKey("keywordFunName")) {
            keyword.setKeywordFunName(keywordMap.get("keywordFunName").toString());
        }
        if (keywordMap.containsKey("keywordDesc")) {
            keyword.setKeywordDesc(keywordMap.get("keywordDesc").toString());
        }
        apiKeyWordMapper.insert(keyword);
        return Result.success("关键字创建成功");
    }
    
    public Result<String> updateKeyword(Long id, Map<String, Object> keywordMap) {
        ApiKeyWord keyword = apiKeyWordMapper.selectById(id);
        if (keyword == null) {
            return Result.error("关键字不存在");
        }
        if (keywordMap.containsKey("name")) {
            keyword.setName(keywordMap.get("name").toString());
        }
        if (keywordMap.containsKey("keywordFunName")) {
            keyword.setKeywordFunName(keywordMap.get("keywordFunName").toString());
        }
        if (keywordMap.containsKey("keywordDesc")) {
            keyword.setKeywordDesc(keywordMap.get("keywordDesc").toString());
        }
        apiKeyWordMapper.updateById(keyword);
        return Result.success("关键字更新成功");
    }
    
    public Result<String> deleteKeyword(Long id) {
        apiKeyWordMapper.deleteById(id);
        return Result.success("关键字删除成功");
    }
    
    // 新增缺失的方法 - 元数据相关
    public Result<List<ApiOperationType>> getAllMetas() {
        List<ApiOperationType> list = apiOperationTypeMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiOperationType>> getMetasByPage(Integer page, Integer pageSize, String name) {
        Page<ApiOperationType> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiOperationType> queryWrapper = new QueryWrapper<>();
        if (name != null && !name.isEmpty()) {
            queryWrapper.like("name", name);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiOperationType> resultPage = apiOperationTypeMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<ApiOperationType> getMetaById(Long id) {
        ApiOperationType meta = apiOperationTypeMapper.selectById(id);
        if (meta == null) {
            return Result.error("元数据不存在");
        }
        return Result.success(meta);
    }
    
    public Result<String> createMeta(Map<String, Object> metaMap) {
        ApiOperationType meta = new ApiOperationType();
        if (metaMap.containsKey("name")) {
            meta.setOperationTypeName(metaMap.get("name").toString());
        }
        if (metaMap.containsKey("operationDesc")) {
            meta.setOperationTypeDesc(metaMap.get("operationDesc").toString());
        }
        apiOperationTypeMapper.insert(meta);
        return Result.success("元数据创建成功");
    }
    
    public Result<String> updateMeta(Long id, Map<String, Object> metaMap) {
        ApiOperationType meta = apiOperationTypeMapper.selectById(id);
        if (meta == null) {
            return Result.error("元数据不存在");
        }
        if (metaMap.containsKey("name")) {
            meta.setOperationTypeName(metaMap.get("name").toString());
        }
        if (metaMap.containsKey("operationDesc")) {
            meta.setOperationTypeDesc(metaMap.get("operationDesc").toString());
        }
        apiOperationTypeMapper.updateById(meta);
        return Result.success("元数据更新成功");
    }
    
    public Result<String> deleteMeta(Long id) {
        apiOperationTypeMapper.deleteById(id);
        return Result.success("元数据删除成功");
    }
    
    // 新增缺失的方法 - 操作类型相关
    public Result<List<ApiOperationType>> getAllOperationTypes() {
        List<ApiOperationType> list = apiOperationTypeMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiOperationType>> getOperationTypesByPage(Integer page, Integer pageSize, String name) {
        Page<ApiOperationType> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiOperationType> queryWrapper = new QueryWrapper<>();
        if (name != null && !name.isEmpty()) {
            queryWrapper.like("name", name);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiOperationType> resultPage = apiOperationTypeMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<ApiOperationType> getOperationTypeById(Long id) {
        ApiOperationType operationType = apiOperationTypeMapper.selectById(id);
        if (operationType == null) {
            return Result.error("操作类型不存在");
        }
        return Result.success(operationType);
    }
    
    public Result<String> createOperationType(Map<String, Object> typeMap) {
        ApiOperationType operationType = new ApiOperationType();
        if (typeMap.containsKey("name")) {
            operationType.setOperationTypeName(typeMap.get("name").toString());
        }
        if (typeMap.containsKey("operationDesc")) {
            operationType.setOperationTypeDesc(typeMap.get("operationDesc").toString());
        }
        apiOperationTypeMapper.insert(operationType);
        return Result.success("操作类型创建成功");
    }
    
    public Result<String> updateOperationType(Long id, Map<String, Object> typeMap) {
        ApiOperationType operationType = apiOperationTypeMapper.selectById(id);
        if (operationType == null) {
            return Result.error("操作类型不存在");
        }
        if (typeMap.containsKey("name")) {
            operationType.setOperationTypeName(typeMap.get("name").toString());
        }
        if (typeMap.containsKey("operationDesc")) {
            operationType.setOperationTypeDesc(typeMap.get("operationDesc").toString());
        }
        apiOperationTypeMapper.updateById(operationType);
        return Result.success("操作类型更新成功");
    }
    
    public Result<String> deleteOperationType(Long id) {
        apiOperationTypeMapper.deleteById(id);
        return Result.success("操作类型删除成功");
    }
}