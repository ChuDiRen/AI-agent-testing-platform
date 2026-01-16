package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiHistory;
import com.platform.platformserver.service.ApiHistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/ApiHistory")
public class ApiHistoryController {
    
    @Autowired
    private ApiHistoryService apiHistoryService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiHistory>> getHistoryList(@RequestParam(required = false) Long caseId) {
        return apiHistoryService.getHistoryList(caseId);
    }
    
    @GetMapping("/queryById")
    public Result<ApiHistory> getHistoryById(@RequestParam Long id) {
        return apiHistoryService.getHistoryById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody ApiHistory history) {
        return apiHistoryService.createHistory(history);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody ApiHistory history) {
        history.setId(id);
        return apiHistoryService.updateHistory(history);
    }
    
    @DeleteMapping("/delete")
    public Result<String> deleteHistory(@RequestParam Long id) {
        return apiHistoryService.deleteHistory(id);
    }
}