package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiDbBase;
import com.platform.platformserver.mapper.ApiDbBaseMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiDbBaseService {
    
    @Autowired
    private ApiDbBaseMapper apiDbBaseMapper;
    
    public Result<List<ApiDbBase>> getDbConfigList(Long projectId) {
        QueryWrapper<ApiDbBase> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("project_id", projectId);
        queryWrapper.orderByDesc("id");
        List<ApiDbBase> configList = apiDbBaseMapper.selectList(queryWrapper);
        return Result.success(configList);
    }
    
    public Result<ApiDbBase> getDbConfigById(Long id) {
        ApiDbBase config = apiDbBaseMapper.selectById(id);
        if (config == null) {
            return Result.error("数据库配置不存在");
        }
        return Result.success(config);
    }
    
    public Result<String> createDbConfig(ApiDbBase config) {
        apiDbBaseMapper.insert(config);
        return Result.success("数据库配置创建成功");
    }
    
    public Result<String> updateDbConfig(ApiDbBase config) {
        apiDbBaseMapper.updateById(config);
        return Result.success("数据库配置更新成功");
    }
    
    public Result<String> deleteDbConfig(Long id) {
        apiDbBaseMapper.deleteById(id);
        return Result.success("数据库配置删除成功");
    }
}