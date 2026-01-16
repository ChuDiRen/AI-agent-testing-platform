package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCaseStep;
import com.platform.platformserver.service.ApiInfoCaseStepService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiInfoCaseStep")
public class ApiInfoCaseStepController {
    
    @Autowired
    private ApiInfoCaseStepService apiInfoCaseStepService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiInfoCaseStep>> queryAll() {
        return apiInfoCaseStepService.getAllSteps();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Long caseId
    ) {
        var pageResult = apiInfoCaseStepService.getStepsByPage(page, pageSize, caseId);
        
        // 转换List<ApiInfoCaseStep>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData());
        result.put("total", pageResult.getData().size()); // 简化处理
        result.put("current", page);
        result.put("size", pageSize);
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<ApiInfoCaseStep> queryById(@RequestParam Long id) {
        return apiInfoCaseStepService.getStepById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> stepData) {
        return apiInfoCaseStepService.createStep(stepData);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> stepData) {
        return apiInfoCaseStepService.updateStep(id, stepData);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiInfoCaseStepService.deleteStep(id);
    }
    
    @PostMapping("/queryAllTree")
    public Result<List<Map<String, Object>>> queryAllTree(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Long apiCaseInfoId) {
        return apiInfoCaseStepService.queryAllTree(page, pageSize, apiCaseInfoId);
    }
}
