package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.service.ApiInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/api-info")
public class ApiInfoController {
    
    @Autowired
    private ApiInfoService apiInfoService;
    
    @GetMapping("/list")
    public Result<List<ApiInfo>> getApiInfoList(@RequestParam(required = false) Long projectId) {
        return apiInfoService.getApiInfoList(projectId);
    }
    
    @GetMapping("/{id}")
    public Result<ApiInfo> getApiInfoById(@PathVariable Long id) {
        return apiInfoService.getApiInfoById(id);
    }
    
    @PostMapping("/create")
    public Result<String> createApiInfo(@RequestBody ApiInfo apiInfo) {
        return apiInfoService.createApiInfo(apiInfo);
    }
    
    @PutMapping("/update")
    public Result<String> updateApiInfo(@RequestBody ApiInfo apiInfo) {
        return apiInfoService.updateApiInfo(apiInfo);
    }
    
    @DeleteMapping("/delete/{id}")
    public Result<String> deleteApiInfo(@PathVariable Long id) {
        return apiInfoService.deleteApiInfo(id);
    }
}