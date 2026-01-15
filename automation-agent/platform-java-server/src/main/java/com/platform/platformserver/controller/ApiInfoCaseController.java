package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCase;
import com.platform.platformserver.service.ApiInfoCaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/test-case")
public class ApiInfoCaseController {
    
    @Autowired
    private ApiInfoCaseService apiInfoCaseService;
    
    @GetMapping("/list/{apiId}")
    public Result<List<ApiInfoCase>> getCaseList(@PathVariable Long apiId) {
        return apiInfoCaseService.getCaseList(apiId);
    }
    
    @GetMapping("/{id}")
    public Result<ApiInfoCase> getCaseById(@PathVariable Long id) {
        return apiInfoCaseService.getCaseById(id);
    }
    
    @PostMapping("/create")
    public Result<String> createCase(@RequestBody ApiInfoCase apiCase) {
        return apiInfoCaseService.createCase(apiCase);
    }
    
    @PutMapping("/update")
    public Result<String> updateCase(@RequestBody ApiInfoCase apiCase) {
        return apiInfoCaseService.updateCase(apiCase);
    }
    
    @DeleteMapping("/delete/{id}")
    public Result<String> deleteCase(@PathVariable Long id) {
        return apiInfoCaseService.deleteCase(id);
    }
}