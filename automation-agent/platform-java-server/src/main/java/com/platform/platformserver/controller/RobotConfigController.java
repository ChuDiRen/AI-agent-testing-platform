package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.RobotConfig;
import com.platform.platformserver.service.RobotConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/robot-config")
public class RobotConfigController {
    
    @Autowired
    private RobotConfigService robotConfigService;
    
    @GetMapping("/list")
    public Result<List<RobotConfig>> getRobotConfigList() {
        return robotConfigService.getRobotConfigList();
    }
    
    @GetMapping("/{id}")
    public Result<RobotConfig> getRobotConfigById(@PathVariable Long id) {
        return robotConfigService.getRobotConfigById(id);
    }
    
    @PostMapping("/create")
    public Result<String> createRobotConfig(@RequestBody RobotConfig config) {
        return robotConfigService.createRobotConfig(config);
    }
    
    @PutMapping("/update")
    public Result<String> updateRobotConfig(@RequestBody RobotConfig config) {
        return robotConfigService.updateRobotConfig(config);
    }
    
    @DeleteMapping("/delete/{id}")
    public Result<String> deleteRobotConfig(@PathVariable Long id) {
        return robotConfigService.deleteRobotConfig(id);
    }
}