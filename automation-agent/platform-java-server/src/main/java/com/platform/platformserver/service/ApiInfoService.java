package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.mapper.ApiInfoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiInfoService {
    
    @Autowired
    private ApiInfoMapper apiInfoMapper;
    
    public Result<List<ApiInfo>> getApiInfoList(Long projectId) {
        QueryWrapper<ApiInfo> queryWrapper = new QueryWrapper<>();
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        queryWrapper.orderByDesc("id");
        List<ApiInfo> apiInfoList = apiInfoMapper.selectList(queryWrapper);
        return Result.success(apiInfoList);
    }
    
    public Result<ApiInfo> getApiInfoById(Long id) {
        ApiInfo apiInfo = apiInfoMapper.selectById(id);
        if (apiInfo == null) {
            return Result.error("API信息不存在");
        }
        return Result.success(apiInfo);
    }
    
    public Result<String> createApiInfo(ApiInfo apiInfo) {
        apiInfoMapper.insert(apiInfo);
        return Result.success("API信息创建成功");
    }
    
    public Result<String> updateApiInfo(ApiInfo apiInfo) {
        apiInfoMapper.updateById(apiInfo);
        return Result.success("API信息更新成功");
    }
    
    public Result<String> deleteApiInfo(Long id) {
        apiInfoMapper.deleteById(id);
        return Result.success("API信息删除成功");
    }
}