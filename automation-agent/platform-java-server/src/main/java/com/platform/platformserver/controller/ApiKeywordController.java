package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiKeyWord;
import com.platform.platformserver.service.ApiInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiKeyWord")
public class ApiKeywordController {
    
    @Autowired
    private ApiInfoService apiInfoService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiKeyWord>> queryAll() {
        return apiInfoService.getAllKeywords();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String keywordName
    ) {
        var pageResult = apiInfoService.getKeywordsByPage(page, pageSize, keywordName);
        
        // 转换Page<ApiKeyWord>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<ApiKeyWord> queryById(@RequestParam Long id) {
        return apiInfoService.getKeywordById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> keywordData) {
        return apiInfoService.createKeyword(keywordData);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> keywordData) {
        return apiInfoService.updateKeyword(id, keywordData);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiInfoService.deleteKeyword(id);
    }
    
    @PostMapping("/keywordFile")
    public Result<Map<String, Object>> keywordFile(
            @RequestParam String keyword_fun_name,
            @RequestParam String keyword_value) {
        return apiInfoService.generateKeywordFile(keyword_fun_name, keyword_value);
    }
    
    @GetMapping("/queryAllKeyWordList")
    public Result<List<Map<String, Object>>> queryAllKeyWordList() {
        return apiInfoService.queryAllKeyWordList();
    }
}
