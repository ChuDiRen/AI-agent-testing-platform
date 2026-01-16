package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiCollectionInfo;
import com.platform.platformserver.mapper.ApiCollectionInfoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiCollectionInfoService {
    
    @Autowired
    private ApiCollectionInfoMapper apiCollectionInfoMapper;
    
    public Result<List<ApiCollectionInfo>> getCollectionList(Long projectId) {
        QueryWrapper<ApiCollectionInfo> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("project_id", projectId);
        queryWrapper.orderByDesc("id");
        List<ApiCollectionInfo> collectionList = apiCollectionInfoMapper.selectList(queryWrapper);
        return Result.success(collectionList);
    }
    
    public Result<ApiCollectionInfo> getCollectionById(Long id) {
        ApiCollectionInfo collection = apiCollectionInfoMapper.selectById(id);
        if (collection == null) {
            return Result.error("集合不存在");
        }
        return Result.success(collection);
    }
    
    public Result<String> createCollection(ApiCollectionInfo collection) {
        apiCollectionInfoMapper.insert(collection);
        return Result.success("集合创建成功");
    }
    
    public Result<String> updateCollection(ApiCollectionInfo collection) {
        apiCollectionInfoMapper.updateById(collection);
        return Result.success("集合更新成功");
    }
    
    public Result<String> deleteCollection(Long id) {
        apiCollectionInfoMapper.deleteById(id);
        return Result.success("集合删除成功");
    }
    
    // 新增缺失的方法
    public Result<List<ApiCollectionInfo>> queryAll() {
        List<ApiCollectionInfo> list = apiCollectionInfoMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiCollectionInfo>> queryByPage(Integer page, Integer pageSize, String name) {
        Page<ApiCollectionInfo> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiCollectionInfo> queryWrapper = new QueryWrapper<>();
        if (name != null && !name.isEmpty()) {
            queryWrapper.like("name", name);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiCollectionInfo> resultPage = apiCollectionInfoMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<ApiCollectionInfo> queryById(Long id) {
        ApiCollectionInfo collection = apiCollectionInfoMapper.selectById(id);
        if (collection == null) {
            return Result.error("集合不存在");
        }
        return Result.success(collection);
    }
    
    public Result<String> insert(ApiCollectionInfo collection) {
        apiCollectionInfoMapper.insert(collection);
        return Result.success("集合创建成功");
    }
    
    public Result<String> update(Long id, ApiCollectionInfo collection) {
        collection.setId(id);
        apiCollectionInfoMapper.updateById(collection);
        return Result.success("集合更新成功");
    }
    
    public Result<String> delete(Long id) {
        apiCollectionInfoMapper.deleteById(id);
        return Result.success("集合删除成功");
    }
}