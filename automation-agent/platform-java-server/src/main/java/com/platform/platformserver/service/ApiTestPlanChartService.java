package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiTestPlanChart;
import com.platform.platformserver.mapper.ApiTestPlanChartMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiTestPlanChartService {
    
    @Autowired
    private ApiTestPlanChartMapper apiTestPlanChartMapper;
    
    public Result<List<ApiTestPlanChart>> getAllTestPlanCharts() {
        List<ApiTestPlanChart> list = apiTestPlanChartMapper.selectList(null);
        return Result.success(list);
    }
    
    public Result<Page<ApiTestPlanChart>> getTestPlanChartsByPage(Integer page, Integer pageSize, Long projectId) {
        Page<ApiTestPlanChart> pageParam = new Page<>(page, pageSize);
        QueryWrapper<ApiTestPlanChart> queryWrapper = new QueryWrapper<>();
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        queryWrapper.orderByDesc("id");
        Page<ApiTestPlanChart> resultPage = apiTestPlanChartMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<ApiTestPlanChart> getTestPlanChartById(Long id) {
        ApiTestPlanChart chart = apiTestPlanChartMapper.selectById(id);
        if (chart == null) {
            return Result.error("测试计划图表不存在");
        }
        return Result.success(chart);
    }
    
    public Result<String> createTestPlanChart(ApiTestPlanChart chart) {
        apiTestPlanChartMapper.insert(chart);
        return Result.success("测试计划图表创建成功");
    }
    
    public Result<String> updateTestPlanChart(ApiTestPlanChart chart) {
        apiTestPlanChartMapper.updateById(chart);
        return Result.success("测试计划图表更新成功");
    }
    
    public Result<String> deleteTestPlanChart(Long id) {
        apiTestPlanChartMapper.deleteById(id);
        return Result.success("测试计划图表删除成功");
    }
}
