package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCaseStep;
import com.platform.platformserver.mapper.ApiInfoCaseStepMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ApiInfoCaseStepService {
    
    @Autowired
    private ApiInfoCaseStepMapper apiInfoCaseStepMapper;
    
    public Result<List<ApiInfoCaseStep>> getStepList(Long caseId) {
        QueryWrapper<ApiInfoCaseStep> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("case_id", caseId);
        queryWrapper.orderByAsc("step_order");
        List<ApiInfoCaseStep> stepList = apiInfoCaseStepMapper.selectList(queryWrapper);
        return Result.success(stepList);
    }
    
    public Result<ApiInfoCaseStep> getStepById(Long id) {
        ApiInfoCaseStep step = apiInfoCaseStepMapper.selectById(id);
        if (step == null) {
            return Result.error("步骤不存在");
        }
        return Result.success(step);
    }
    
    public Result<String> createStep(ApiInfoCaseStep step) {
        apiInfoCaseStepMapper.insert(step);
        return Result.success("步骤创建成功");
    }
    
    public Result<String> updateStep(ApiInfoCaseStep step) {
        apiInfoCaseStepMapper.updateById(step);
        return Result.success("步骤更新成功");
    }
    
    public Result<String> deleteStep(Long id) {
        apiInfoCaseStepMapper.deleteById(id);
        return Result.success("步骤删除成功");
    }
    
    public Result<List<ApiInfoCaseStep>> getAllSteps() {
        QueryWrapper<ApiInfoCaseStep> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<ApiInfoCaseStep> stepList = apiInfoCaseStepMapper.selectList(queryWrapper);
        return Result.success(stepList);
    }
    
    public Result<Map<String, Object>> getStepsByPage(Integer page, Integer pageSize, Long caseId) {
        QueryWrapper<ApiInfoCaseStep> queryWrapper = new QueryWrapper<>();
        if (caseId != null) {
            queryWrapper.eq("api_case_info_id", caseId);
        }
        queryWrapper.orderByDesc("id");
        queryWrapper.last("LIMIT " + pageSize + " OFFSET " + ((page - 1) * pageSize));
        List<ApiInfoCaseStep> resultPage = apiInfoCaseStepMapper.selectList(queryWrapper);
        
        Map<String, Object> result = new HashMap<>();
        result.put("data", resultPage);
        result.put("total", resultPage.size());
        result.put("current", page);
        result.put("size", pageSize);
        
        return Result.success(result);
    }
    
    public Result<String> createStep(Map<String, Object> stepMap) {
        ApiInfoCaseStep step = new ApiInfoCaseStep();
        if (stepMap.containsKey("apiCaseInfoId")) {
            step.setApiCaseInfoId(Integer.valueOf(stepMap.get("apiCaseInfoId").toString()));
        }
        if (stepMap.containsKey("keyWordId")) {
            step.setKeyWordId(Integer.valueOf(stepMap.get("keyWordId").toString()));
        }
        if (stepMap.containsKey("stepDesc")) {
            step.setStepDesc(stepMap.get("stepDesc").toString());
        }
        if (stepMap.containsKey("refVariable")) {
            step.setRefVariable(stepMap.get("refVariable").toString());
        }
        if (stepMap.containsKey("runOrder")) {
            step.setRunOrder(Integer.valueOf(stepMap.get("runOrder").toString()));
        }
        
        apiInfoCaseStepMapper.insert(step);
        return Result.success("步骤创建成功");
    }
    
    public Result<String> updateStep(Long id, Map<String, Object> stepMap) {
        ApiInfoCaseStep step = apiInfoCaseStepMapper.selectById(id);
        if (step == null) {
            return Result.error("步骤不存在");
        }
        
        if (stepMap.containsKey("apiCaseInfoId")) {
            step.setApiCaseInfoId(Integer.valueOf(stepMap.get("apiCaseInfoId").toString()));
        }
        if (stepMap.containsKey("keyWordId")) {
            step.setKeyWordId(Integer.valueOf(stepMap.get("keyWordId").toString()));
        }
        if (stepMap.containsKey("stepDesc")) {
            step.setStepDesc(stepMap.get("stepDesc").toString());
        }
        if (stepMap.containsKey("refVariable")) {
            step.setRefVariable(stepMap.get("refVariable").toString());
        }
        if (stepMap.containsKey("runOrder")) {
            step.setRunOrder(Integer.valueOf(stepMap.get("runOrder").toString()));
        }
        
        apiInfoCaseStepMapper.updateById(step);
        return Result.success("步骤更新成功");
    }
    
    public Result<List<Map<String, Object>>> queryAllTree(Integer page, Integer pageSize, Long apiCaseInfoId) {
        QueryWrapper<ApiInfoCaseStep> queryWrapper = new QueryWrapper<>();
        if (apiCaseInfoId != null) {
            queryWrapper.eq("api_case_info_id", apiCaseInfoId);
        }
        queryWrapper.orderByDesc("id");
        
        if (page != null && pageSize != null) {
            queryWrapper.last("LIMIT " + pageSize + " OFFSET " + ((page - 1) * pageSize));
        }
        
        List<ApiInfoCaseStep> allSteps = apiInfoCaseStepMapper.selectList(queryWrapper);
        
        List<Map<String, Object>> result = new ArrayList<>();
        for (ApiInfoCaseStep step : allSteps) {
            Map<String, Object> stepMap = new HashMap<>();
            stepMap.put("id", step.getId());
            stepMap.put("apiCaseInfoId", step.getApiCaseInfoId());
            stepMap.put("keyWordId", step.getKeyWordId());
            stepMap.put("stepDesc", step.getStepDesc());
            stepMap.put("refVariable", step.getRefVariable());
            stepMap.put("runOrder", step.getRunOrder());
            stepMap.put("createTime", step.getCreateTime());
            result.add(stepMap);
        }
        
        return Result.success(result);
    }
    
    public Result<String> batchCreateSteps(List<ApiInfoCaseStep> steps) {
        for (ApiInfoCaseStep step : steps) {
            apiInfoCaseStepMapper.insert(step);
        }
        return Result.success("批量创建步骤成功");
    }
}
