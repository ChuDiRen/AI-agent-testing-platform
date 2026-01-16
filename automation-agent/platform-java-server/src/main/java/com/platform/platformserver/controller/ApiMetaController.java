package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiMeta;
import com.platform.platformserver.service.ApiMetaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiMeta")
public class ApiMetaController {
    
    @Autowired
    private ApiMetaService apiMetaService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiMeta>> queryAll() {
        return apiMetaService.getAllMetas();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String metaKey
    ) {
        var pageResult = apiMetaService.getMetasByPage(page, pageSize, metaKey);
        
        // 转换Page<ApiMeta>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<ApiMeta> queryById(@RequestParam Long id) {
        return apiMetaService.getMetaById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> metaData) {
        return apiMetaService.createMeta(metaData);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> metaData) {
        return apiMetaService.updateMeta(id, metaData);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiMetaService.deleteMeta(id);
    }
}
