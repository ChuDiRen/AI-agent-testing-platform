package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCase;
import com.platform.platformserver.mapper.ApiInfoCaseMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiInfoCaseService {
    
    @Autowired
    private ApiInfoCaseMapper apiInfoCaseMapper;
    
    public Result<List<ApiInfoCase>> getCaseList(Long apiId) {
        QueryWrapper<ApiInfoCase> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("api_id", apiId);
        queryWrapper.orderByDesc("id");
        List<ApiInfoCase> caseList = apiInfoCaseMapper.selectList(queryWrapper);
        return Result.success(caseList);
    }
    
    public Result<ApiInfoCase> getCaseById(Long id) {
        ApiInfoCase apiCase = apiInfoCaseMapper.selectById(id);
        if (apiCase == null) {
            return Result.error("测试用例不存在");
        }
        return Result.success(apiCase);
    }
    
    public Result<String> createCase(ApiInfoCase apiCase) {
        apiInfoCaseMapper.insert(apiCase);
        return Result.success("测试用例创建成功");
    }
    
    public Result<String> updateCase(ApiInfoCase apiCase) {
        apiInfoCaseMapper.updateById(apiCase);
        return Result.success("测试用例更新成功");
    }
    
    public Result<String> deleteCase(Long id) {
        apiInfoCaseMapper.deleteById(id);
        return Result.success("测试用例删除成功");
    }
}