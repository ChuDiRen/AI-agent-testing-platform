package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.RobotConfig;
import com.platform.platformserver.service.RobotConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/RobotConfig")
public class RobotConfigController {
    
    @Autowired
    private RobotConfigService robotConfigService;
    
    @GetMapping("/queryAll")
    public Result<List<RobotConfig>> getRobotConfigList() {
        return robotConfigService.getRobotConfigList();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize) {
        var pageResult = robotConfigService.queryByPage(page, pageSize);
        
        // 转换Page<RobotConfig>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<RobotConfig> getRobotConfigById(@RequestParam Long id) {
        return robotConfigService.getRobotConfigById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> createRobotConfig(@RequestBody RobotConfig config) {
        return robotConfigService.createRobotConfig(config);
    }
    
    @PostMapping("/queryByPageWithFilter")
    public Result<Map<String, Object>> queryByPageWithFilter(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Integer coll_id,
            @RequestParam(required = false) String coll_type,
            @RequestParam(required = false) String robot_name,
            @RequestParam(required = false) String type) {
        var pageResult = robotConfigService.queryByPageWithFilter(page, pageSize, coll_id, robot_name, type);
        
        // 转换Page<RobotConfig>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @PutMapping("/update")
    public Result<String> updateRobotConfig(@RequestParam Long id, @RequestBody Map<String, Object> configMap) {
        return robotConfigService.updateRobotConfig(id, configMap);
    }
    
    @DeleteMapping("/delete")
    public Result<String> deleteRobotConfig(@RequestParam Long id) {
        return robotConfigService.deleteRobotConfig(id);
    }
}