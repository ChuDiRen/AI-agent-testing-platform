package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiDbBase;
import com.platform.platformserver.service.ApiDbBaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/db-config")
public class ApiDbBaseController {
    
    @Autowired
    private ApiDbBaseService apiDbBaseService;
    
    @GetMapping("/list")
    public Result<List<ApiDbBase>> getDbConfigList(@RequestParam Long projectId) {
        return apiDbBaseService.getDbConfigList(projectId);
    }
    
    @GetMapping("/{id}")
    public Result<ApiDbBase> getDbConfigById(@PathVariable Long id) {
        return apiDbBaseService.getDbConfigById(id);
    }
    
    @PostMapping("/create")
    public Result<String> createDbConfig(@RequestBody ApiDbBase config) {
        return apiDbBaseService.createDbConfig(config);
    }
    
    @PutMapping("/update")
    public Result<String> updateDbConfig(@RequestBody ApiDbBase config) {
        return apiDbBaseService.updateDbConfig(config);
    }
    
    @DeleteMapping("/delete/{id}")
    public Result<String> deleteDbConfig(@PathVariable Long id) {
        return apiDbBaseService.deleteDbConfig(id);
    }
}