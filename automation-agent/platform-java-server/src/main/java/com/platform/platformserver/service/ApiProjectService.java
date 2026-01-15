package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiProject;
import com.platform.platformserver.mapper.ApiProjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiProjectService {
    
    @Autowired
    private ApiProjectMapper apiProjectMapper;
    
    public Result<List<ApiProject>> getProjectList() {
        QueryWrapper<ApiProject> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<ApiProject> projects = apiProjectMapper.selectList(queryWrapper);
        return Result.success(projects);
    }
    
    public Result<ApiProject> getProjectById(Long id) {
        ApiProject project = apiProjectMapper.selectById(id);
        if (project == null) {
            return Result.error("项目不存在");
        }
        return Result.success(project);
    }
    
    public Result<String> createProject(ApiProject project) {
        apiProjectMapper.insert(project);
        return Result.success("项目创建成功");
    }
    
    public Result<String> updateProject(ApiProject project) {
        apiProjectMapper.updateById(project);
        return Result.success("项目更新成功");
    }
    
    public Result<String> deleteProject(Long id) {
        apiProjectMapper.deleteById(id);
        return Result.success("项目删除成功");
    }
}