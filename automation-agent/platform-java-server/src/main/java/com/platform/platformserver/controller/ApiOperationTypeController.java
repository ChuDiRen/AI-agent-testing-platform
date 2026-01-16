package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiOperationType;
import com.platform.platformserver.service.ApiInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiOperationType")
public class ApiOperationTypeController {
    
    @Autowired
    private ApiInfoService apiInfoService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiOperationType>> queryAll() {
        return apiInfoService.getAllOperationTypes();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String typeName
    ) {
        var pageResult = apiInfoService.getOperationTypesByPage(page, pageSize, typeName);
        
        // 转换Page<ApiOperationType>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<ApiOperationType> queryById(@RequestParam Long id) {
        return apiInfoService.getOperationTypeById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> typeData) {
        return apiInfoService.createOperationType(typeData);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> typeData) {
        return apiInfoService.updateOperationType(id, typeData);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiInfoService.deleteOperationType(id);
    }
}
