package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiCollectionDetail;
import com.platform.platformserver.service.ApiCollectionDetailService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiCollectionDetail")
public class ApiCollectionDetailController {
    
    @Autowired
    private ApiCollectionDetailService apiCollectionDetailService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiCollectionDetail>> queryAll() {
        return apiCollectionDetailService.getAllDetails();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Long collectionInfoId,
            @RequestParam(required = false) Long apiInfoId
    ) {
        var pageResult = apiCollectionDetailService.getDetailsByPage(page, pageSize, collectionInfoId, apiInfoId);
        
        // 转换Page<ApiCollectionDetail>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<ApiCollectionDetail> queryById(@RequestParam Long id) {
        return apiCollectionDetailService.getDetailById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> collectionDetailData) {
        return apiCollectionDetailService.createDetail(collectionDetailData);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> collectionDetailData) {
        return apiCollectionDetailService.updateDetail(id, collectionDetailData);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiCollectionDetailService.deleteDetail(id);
    }
}
