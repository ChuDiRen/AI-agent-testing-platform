package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCase;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.mapper.ApiInfoCaseMapper;
import com.platform.platformserver.mapper.ApiInfoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ApiInfoCaseService {
    
    @Autowired
    private ApiInfoCaseMapper apiInfoCaseMapper;

    @Autowired
    private ApiInfoMapper apiInfoMapper;

    public Result<List<ApiInfoCase>> getCaseList(Long apiId) {
        QueryWrapper<ApiInfoCase> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("api_id", apiId);
        queryWrapper.orderByDesc("id");
        List<ApiInfoCase> caseList = apiInfoCaseMapper.selectList(queryWrapper);
        return Result.success(caseList);
    }

    public Result<ApiInfoCase> getCaseById(Long id) {
        ApiInfoCase apiCase = apiInfoCaseMapper.selectById(id);
        if (apiCase == null) {
            return Result.error("测试用例不存在");
        }
        return Result.success(apiCase);
    }

    public Result<String> createCase(ApiInfoCase apiCase) {
        apiInfoCaseMapper.insert(apiCase);
        return Result.success("测试用例创建成功");
    }

    public Result<String> updateCase(ApiInfoCase apiCase) {
        apiInfoCaseMapper.updateById(apiCase);
        return Result.success("测试用例更新成功");
    }

    public Result<String> deleteCase(Long id) {
        apiInfoCaseMapper.deleteById(id);
        return Result.success("测试用例删除成功");
    }

    public Result<Map<String, Object>> debugTest(Long id) {
        ApiInfoCase apiCase = apiInfoCaseMapper.selectById(id);
        if (apiCase == null) {
            return Result.error("测试用例不存在");
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("case_id", id);
        result.put("case_name", apiCase.getCaseName());
        result.put("status", "debugging");
        result.put("message", "调试测试已开始");
        
        return Result.success(result);
    }

    public Result<List<Map<String, Object>>> uploadFile(MultipartFile file, String apiName) {
        try {
            // 解析上传的API文件
            String content = new String(file.getBytes());

            // 导入API信息到数据库
            ApiInfo apiInfo = new ApiInfo();
            apiInfo.setApiName(apiName);
            apiInfo.setRequestsJsonData(content);

            apiInfoMapper.insert(apiInfo);

            List<Map<String, Object>> result = new ArrayList<>();
            Map<String, Object> fileInfo = new HashMap<>();
            fileInfo.put("message", "API文件上传成功");
            fileInfo.put("api_name", apiName);
            fileInfo.put("api_id", apiInfo.getId());
            result.add(fileInfo);

            return Result.success(result);
        } catch (Exception e) {
            return Result.error("API文件上传失败: " + e.getMessage());
        }
    }

    public Result<List<ApiInfoCase>> getAllSteps() {
        QueryWrapper<ApiInfoCase> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<ApiInfoCase> stepList = apiInfoCaseMapper.selectList(queryWrapper);
        return Result.success(stepList);
    }

    public Result<List<ApiInfoCase>> getStepsByPage(Integer page, Integer pageSize, Long apiId) {
        QueryWrapper<ApiInfoCase> queryWrapper = new QueryWrapper<>();
        if (apiId != null) {
            queryWrapper.eq("api_id", apiId);
        }
        queryWrapper.orderByDesc("id");
        queryWrapper.last("LIMIT " + pageSize + " OFFSET " + ((page - 1) * pageSize));
        List<ApiInfoCase> resultPage = apiInfoCaseMapper.selectList(queryWrapper);
        return Result.success(resultPage);
    }

    public Result<ApiInfoCase> getStepById(Long id) {
        ApiInfoCase step = apiInfoCaseMapper.selectById(id);
        if (step == null) {
            return Result.error("步骤不存在");
        }
        return Result.success(step);
    }

    public Result<String> createStep(Map<String, Object> stepMap) {
        ApiInfoCase step = new ApiInfoCase();
        if (stepMap.containsKey("apiId")) {
            step.setApiId(Long.valueOf(stepMap.get("apiId").toString()));
        }
        if (stepMap.containsKey("caseName")) {
            step.setCaseName(stepMap.get("caseName").toString());
        }
        if (stepMap.containsKey("caseDesc")) {
            step.setCaseDesc(stepMap.get("caseDesc").toString());
        }
        if (stepMap.containsKey("paramData")) {
            step.setParamData(stepMap.get("paramData").toString());
        }

        apiInfoCaseMapper.insert(step);
        return Result.success("步骤创建成功");
    }

    public Result<String> updateStep(Long id, Map<String, Object> stepMap) {
        ApiInfoCase step = apiInfoCaseMapper.selectById(id);
        if (step == null) {
            return Result.error("步骤不存在");
        }

        if (stepMap.containsKey("apiId")) {
            step.setApiId(Long.valueOf(stepMap.get("apiId").toString()));
        }
        if (stepMap.containsKey("caseName")) {
            step.setCaseName(stepMap.get("caseName").toString());
        }
        if (stepMap.containsKey("caseDesc")) {
            step.setCaseDesc(stepMap.get("caseDesc").toString());
        }
        if (stepMap.containsKey("paramData")) {
            step.setParamData(stepMap.get("paramData").toString());
        }

        apiInfoCaseMapper.updateById(step);
        return Result.success("步骤更新成功");
    }

    public Result<String> deleteStep(Long id) {
        apiInfoCaseMapper.deleteById(id);
        return Result.success("步骤删除成功");
    }

    public Result<List<ApiInfoCase>> queryAllTree(Integer page, Integer pageSize, Long apiId) {
        QueryWrapper<ApiInfoCase> queryWrapper = new QueryWrapper<>();
        if (apiId != null) {
            queryWrapper.eq("api_id", apiId);
        }
        queryWrapper.orderByDesc("id");
        
        if (page != null && pageSize != null) {
            queryWrapper.last("LIMIT " + pageSize + " OFFSET " + ((page - 1) * pageSize));
        }
        
        List<ApiInfoCase> allSteps = apiInfoCaseMapper.selectList(queryWrapper);

        // 构建树形结构 - 暂时简化处理
        List<ApiInfoCase> rootSteps = new ArrayList<>();
        for (ApiInfoCase step : allSteps) {
            rootSteps.add(step);
        }

        return Result.success(rootSteps);
    }
}