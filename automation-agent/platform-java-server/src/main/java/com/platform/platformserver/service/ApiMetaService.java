package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiMeta;
import com.platform.platformserver.mapper.ApiMetaMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class ApiMetaService {
    
    @Autowired
    private ApiMetaMapper apiMetaMapper;
    
    public Result<List<ApiMeta>> getMetaList(Integer projectId, Integer moduleId) {
        QueryWrapper<ApiMeta> queryWrapper = new QueryWrapper<>();
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        if (moduleId != null) {
            queryWrapper.eq("module_id", moduleId);
        }
        queryWrapper.orderByDesc("id");
        List<ApiMeta> metaList = apiMetaMapper.selectList(queryWrapper);
        return Result.success(metaList);
    }
    
    public Result<ApiMeta> getMetaById(Long id) {
        ApiMeta meta = apiMetaMapper.selectById(id);
        if (meta == null) {
            return Result.error("API元数据不存在");
        }
        return Result.success(meta);
    }
    
    public Result<String> createMeta(ApiMeta meta) {
        apiMetaMapper.insert(meta);
        return Result.success("API元数据创建成功");
    }
    
    public Result<String> updateMeta(ApiMeta meta) {
        apiMetaMapper.updateById(meta);
        return Result.success("API元数据更新成功");
    }
    
    public Result<String> deleteMeta(Long id) {
        apiMetaMapper.deleteById(id);
        return Result.success("API元数据删除成功");
    }
    
    // 新增缺失的方法
    public Result<List<ApiMeta>> getAllMetas() {
        List<ApiMeta> list = apiMetaMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiMeta>> getMetasByPage(Integer page, Integer pageSize, String metaKey) {
        Page<ApiMeta> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiMeta> queryWrapper = new QueryWrapper<>();
        if (metaKey != null && !metaKey.isEmpty()) {
            queryWrapper.like("api_name", metaKey);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiMeta> resultPage = apiMetaMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<String> createMeta(Map<String, Object> metaMap) {
        ApiMeta meta = new ApiMeta();
        if (metaMap.containsKey("projectId")) {
            meta.setProjectId(Integer.valueOf(metaMap.get("projectId").toString()));
        }
        if (metaMap.containsKey("moduleId")) {
            meta.setModuleId(Integer.valueOf(metaMap.get("moduleId").toString()));
        }
        if (metaMap.containsKey("apiName")) {
            meta.setApiName(metaMap.get("apiName").toString());
        }
        if (metaMap.containsKey("requestMethod")) {
            meta.setRequestMethod(metaMap.get("requestMethod").toString());
        }
        if (metaMap.containsKey("requestUrl")) {
            meta.setRequestUrl(metaMap.get("requestUrl").toString());
        }
        apiMetaMapper.insert(meta);
        return Result.success("API元数据创建成功");
    }
    
    public Result<String> updateMeta(Long id, Map<String, Object> metaMap) {
        ApiMeta meta = apiMetaMapper.selectById(id);
        if (meta == null) {
            return Result.error("API元数据不存在");
        }
        if (metaMap.containsKey("projectId")) {
            meta.setProjectId(Integer.valueOf(metaMap.get("projectId").toString()));
        }
        if (metaMap.containsKey("moduleId")) {
            meta.setModuleId(Integer.valueOf(metaMap.get("moduleId").toString()));
        }
        if (metaMap.containsKey("apiName")) {
            meta.setApiName(metaMap.get("apiName").toString());
        }
        if (metaMap.containsKey("requestMethod")) {
            meta.setRequestMethod(metaMap.get("requestMethod").toString());
        }
        if (metaMap.containsKey("requestUrl")) {
            meta.setRequestUrl(metaMap.get("requestUrl").toString());
        }
        apiMetaMapper.updateById(meta);
        return Result.success("API元数据更新成功");
    }
}
