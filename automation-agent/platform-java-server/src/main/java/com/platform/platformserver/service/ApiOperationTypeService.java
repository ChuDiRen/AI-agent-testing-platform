package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiOperationType;
import com.platform.platformserver.mapper.ApiOperationTypeMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiOperationTypeService {
    
    @Autowired
    private ApiOperationTypeMapper apiOperationTypeMapper;
    
    public Result<List<ApiOperationType>> getOperationTypeList() {
        QueryWrapper<ApiOperationType> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<ApiOperationType> typeList = apiOperationTypeMapper.selectList(queryWrapper);
        return Result.success(typeList);
    }
    
    public Result<ApiOperationType> getOperationTypeById(Long id) {
        ApiOperationType type = apiOperationTypeMapper.selectById(id);
        if (type == null) {
            return Result.error("操作类型不存在");
        }
        return Result.success(type);
    }
    
    public Result<String> createOperationType(ApiOperationType type) {
        apiOperationTypeMapper.insert(type);
        return Result.success("操作类型创建成功");
    }
    
    public Result<String> updateOperationType(ApiOperationType type) {
        apiOperationTypeMapper.updateById(type);
        return Result.success("操作类型更新成功");
    }
    
    public Result<String> deleteOperationType(Long id) {
        apiOperationTypeMapper.deleteById(id);
        return Result.success("操作类型删除成功");
    }
}
