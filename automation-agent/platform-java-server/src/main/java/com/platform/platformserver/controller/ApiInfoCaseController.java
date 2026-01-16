package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCase;
import com.platform.platformserver.service.ApiInfoCaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiInfoCase")
public class ApiInfoCaseController {
    
    @Autowired
    private ApiInfoCaseService apiInfoCaseService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiInfoCase>> getCaseList(@PathVariable Long apiId) {
        return apiInfoCaseService.getCaseList(apiId);
    }
    
    @GetMapping("/{id}")
    public Result<ApiInfoCase> getCaseById(@PathVariable Long id) {
        return apiInfoCaseService.getCaseById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody ApiInfoCase apiCase) {
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
    
    @PostMapping("/debugTest")
    public Result<Map<String, Object>> debugTest(@RequestParam Long id) {
        return apiInfoCaseService.debugTest(id);
    }
    
    @PostMapping("/uploadFile")
    public Result<List<Map<String, Object>>> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam("project_id") String projectId) {
        return apiInfoCaseService.uploadFile(file, projectId);
    }
}