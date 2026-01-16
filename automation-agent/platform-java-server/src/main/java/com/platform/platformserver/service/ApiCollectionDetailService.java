package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiCollectionDetail;
import com.platform.platformserver.mapper.ApiCollectionDetailMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class ApiCollectionDetailService {
    
    @Autowired
    private ApiCollectionDetailMapper apiCollectionDetailMapper;
    
    public Result<List<ApiCollectionDetail>> getDetailList(Long collectionId) {
        QueryWrapper<ApiCollectionDetail> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("collection_id", collectionId);
        queryWrapper.orderByDesc("id");
        List<ApiCollectionDetail> detailList = apiCollectionDetailMapper.selectList(queryWrapper);
        return Result.success(detailList);
    }
    
    public Result<ApiCollectionDetail> getDetailById(Long id) {
        ApiCollectionDetail detail = apiCollectionDetailMapper.selectById(id);
        if (detail == null) {
            return Result.error("集合详情不存在");
        }
        return Result.success(detail);
    }
    
    public Result<String> createDetail(ApiCollectionDetail detail) {
        apiCollectionDetailMapper.insert(detail);
        return Result.success("集合详情创建成功");
    }
    
    public Result<String> updateDetail(ApiCollectionDetail detail) {
        apiCollectionDetailMapper.updateById(detail);
        return Result.success("集合详情更新成功");
    }
    
    public Result<String> deleteDetail(Long id) {
        apiCollectionDetailMapper.deleteById(id);
        return Result.success("集合详情删除成功");
    }
    
    // 新增缺失的方法
    public Result<List<ApiCollectionDetail>> getAllDetails() {
        List<ApiCollectionDetail> list = apiCollectionDetailMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiCollectionDetail>> getDetailsByPage(Integer page, Integer pageSize, Long collectionInfoId, Long projectId) {
        Page<ApiCollectionDetail> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiCollectionDetail> queryWrapper = new QueryWrapper<>();
        if (collectionInfoId != null) {
            queryWrapper.eq("collection_info_id", collectionInfoId);
        }
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiCollectionDetail> resultPage = apiCollectionDetailMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<String> createDetail(Map<String, Object> detailMap) {
        ApiCollectionDetail detail = new ApiCollectionDetail();
        // 这里需要根据实际字段进行映射
        if (detailMap.containsKey("collectionInfoId")) {
            detail.setCollectionInfoId(Integer.valueOf(detailMap.get("collectionInfoId").toString()));
        }
        if (detailMap.containsKey("apiInfoId")) {
            detail.setApiInfoId(Integer.valueOf(detailMap.get("apiInfoId").toString()));
        }
        apiCollectionDetailMapper.insert(detail);
        return Result.success("详情创建成功");
    }
    
    public Result<String> updateDetail(Long id, Map<String, Object> detailMap) {
        ApiCollectionDetail detail = apiCollectionDetailMapper.selectById(id);
        if (detail == null) {
            return Result.error("详情不存在");
        }
        // 更新字段
        if (detailMap.containsKey("collectionInfoId")) {
            detail.setCollectionInfoId(Integer.valueOf(detailMap.get("collectionInfoId").toString()));
        }
        if (detailMap.containsKey("apiInfoId")) {
            detail.setApiInfoId(Integer.valueOf(detailMap.get("apiInfoId").toString()));
        }
        apiCollectionDetailMapper.updateById(detail);
        return Result.success("详情更新成功");
    }
}
