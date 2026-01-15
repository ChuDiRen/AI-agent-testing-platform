package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiHistory;
import com.platform.platformserver.service.ApiHistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/api-history")
public class ApiHistoryController {
    
    @Autowired
    private ApiHistoryService apiHistoryService;
    
    @GetMapping("/list")
    public Result<List<ApiHistory>> getHistoryList(@RequestParam(required = false) Long caseId) {
        return apiHistoryService.getHistoryList(caseId);
    }
    
    @GetMapping("/{id}")
    public Result<ApiHistory> getHistoryById(@PathVariable Long id) {
        return apiHistoryService.getHistoryById(id);
    }
    
    @DeleteMapping("/delete/{id}")
    public Result<String> deleteHistory(@PathVariable Long id) {
        return apiHistoryService.deleteHistory(id);
    }
}