package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiHistory;
import com.platform.platformserver.mapper.ApiHistoryMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class ApiHistoryService {
    
    @Autowired
    private ApiHistoryMapper apiHistoryMapper;
    
    public Result<List<ApiHistory>> getHistoryList(Long caseId) {
        QueryWrapper<ApiHistory> queryWrapper = new QueryWrapper<>();
        if (caseId != null) {
            queryWrapper.eq("case_id", caseId);
        }
        queryWrapper.orderByDesc("execute_time");
        List<ApiHistory> historyList = apiHistoryMapper.selectList(queryWrapper);
        return Result.success(historyList);
    }
    
    public Result<ApiHistory> getHistoryById(Long id) {
        ApiHistory history = apiHistoryMapper.selectById(id);
        if (history == null) {
            return Result.error("历史记录不存在");
        }
        return Result.success(history);
    }
    
    public Result<String> createHistory(ApiHistory history) {
        history.setExecuteTime(LocalDateTime.now());
        apiHistoryMapper.insert(history);
        return Result.success("历史记录创建成功");
    }
    
    public Result<String> updateHistory(ApiHistory history) {
        apiHistoryMapper.updateById(history);
        return Result.success("历史记录更新成功");
    }
    
    public Result<String> deleteHistory(Long id) {
        apiHistoryMapper.deleteById(id);
        return Result.success("历史记录删除成功");
    }
}