package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiCollectionInfo;
import com.platform.platformserver.service.ApiCollectionInfoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/v1/ApiCollectionInfo")
@RequiredArgsConstructor
@Tag(name = "API集合管理", description = "API集合信息管理相关接口")
public class ApiCollectionInfoController {
    
    private final ApiCollectionInfoService apiCollectionInfoService;
    
    @GetMapping("/queryAll")
    @Operation(summary = "查询所有集合", description = "查询所有API集合信息")
    public Result<List<ApiCollectionInfo>> queryAll() {
        return apiCollectionInfoService.queryAll();
    }
    
    @PostMapping("/queryByPage")
    @Operation(summary = "分页查询集合", description = "分页查询API集合信息")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(required = false) Integer page,
            @RequestParam(required = false) Integer page_size,
            @RequestParam(required = false) String collection_name) {
        var pageResult = apiCollectionInfoService.queryByPage(page, page_size, collection_name);
        
        // 转换Page<ApiCollectionInfo>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    @Operation(summary = "根据ID查询集合", description = "根据ID查询API集合信息")
    public Result<ApiCollectionInfo> queryById(@RequestParam Long id) {
        return apiCollectionInfoService.queryById(id);
    }
    
    @PostMapping("/insert")
    @Operation(summary = "添加集合", description = "添加新的API集合")
    public Result<Map<String, Object>> insert(@RequestBody ApiCollectionInfo collection) {
        var result = apiCollectionInfoService.insert(collection);
        // 转换Result<String>为Result<Map<String, Object>>
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("message", result.getMessage());
        return Result.success(resultMap);
    }
    
    @PutMapping("/update")
    @Operation(summary = "更新集合", description = "更新API集合信息")
    public Result<String> update(@RequestParam Long id, @RequestBody ApiCollectionInfo collection) {
        return apiCollectionInfoService.update(id, collection);
    }
    
    @DeleteMapping("/delete")
    @Operation(summary = "删除集合", description = "删除API集合")
    public Result<String> delete(@RequestParam Long id) {
        return apiCollectionInfoService.delete(id);
    }
}
