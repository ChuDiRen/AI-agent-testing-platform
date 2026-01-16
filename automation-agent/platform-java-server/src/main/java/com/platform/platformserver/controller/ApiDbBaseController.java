package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiDbBase;
import com.platform.platformserver.service.ApiDbBaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/ApiDbBase")
public class ApiDbBaseController {
    
    @Autowired
    private ApiDbBaseService apiDbBaseService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiDbBase>> getDbConfigList(@RequestParam Long projectId) {
        return apiDbBaseService.getDbConfigList(projectId);
    }
    
    @GetMapping("/queryById")
    public Result<ApiDbBase> getDbConfigById(@RequestParam Long id) {
        return apiDbBaseService.getDbConfigById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody ApiDbBase config) {
        return apiDbBaseService.createDbConfig(config);
    }
    
    @PutMapping("/update")
    public Result<String> updateDbConfig(@RequestParam Long id, @RequestBody ApiDbBase config) {
        return apiDbBaseService.updateDbConfig(id, config);
    }
    
    @DeleteMapping("/delete")
    public Result<String> deleteDbConfig(@RequestParam Long id) {
        return apiDbBaseService.deleteDbConfig(id);
    }
}