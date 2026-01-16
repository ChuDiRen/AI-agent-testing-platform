package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiTestPlanChart;
import com.platform.platformserver.service.ApiTestPlanChartService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiTestPlanChart")
public class ApiTestPlanChartController {
    
    @Autowired
    private ApiTestPlanChartService apiTestPlanChartService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiTestPlanChart>> queryAll() {
        return apiTestPlanChartService.getAllTestPlanCharts();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Long projectId
    ) {
        var pageResult = apiTestPlanChartService.getTestPlanChartsByPage(page, pageSize, projectId);
        
        // 转换Page<ApiTestPlanChart>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<ApiTestPlanChart> queryById(@RequestParam Long id) {
        return apiTestPlanChartService.getTestPlanChartById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> chartData) {
        // 需要创建ApiTestPlanChart对象
        ApiTestPlanChart chart = new ApiTestPlanChart();
        // 这里可以根据chartData设置chart的属性
        apiTestPlanChartService.createTestPlanChart(chart);
        return Result.success("测试计划图表创建成功");
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> chartData) {
        // 需要创建ApiTestPlanChart对象
        ApiTestPlanChart chart = new ApiTestPlanChart();
        chart.setId(id);
        // 这里可以根据chartData设置chart的属性
        apiTestPlanChartService.updateTestPlanChart(chart);
        return Result.success("测试计划图表更新成功");
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiTestPlanChartService.deleteTestPlanChart(id);
    }
}
