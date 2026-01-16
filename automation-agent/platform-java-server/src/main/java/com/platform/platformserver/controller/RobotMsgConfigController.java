package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.RobotMsgConfig;
import com.platform.platformserver.service.RobotMsgConfigService;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/RobotMsgConfig")
public class RobotMsgConfigController {
    
    @Autowired
    private RobotMsgConfigService robotMsgConfigService;
    
    @GetMapping("/queryAll")
    public Result<List<RobotMsgConfig>> queryAll() {
        return robotMsgConfigService.getAllMsgConfigs();
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Long robotId,
            @RequestParam(required = false) String msgType
    ) {
        Result<Page<RobotMsgConfig>> pageResult = robotMsgConfigService.getMsgConfigsByPage(page, pageSize, robotId, msgType);
        
        // 转换Page<RobotMsgConfig>为Map<String, Object>
        Map<String, Object> result = new HashMap<>();
        result.put("data", pageResult.getData().getRecords());
        result.put("total", pageResult.getData().getTotal());
        result.put("current", pageResult.getData().getCurrent());
        result.put("size", pageResult.getData().getSize());
        
        return Result.success(result);
    }
    
    @GetMapping("/queryById")
    public Result<RobotMsgConfig> queryById(@RequestParam Long id) {
        return robotMsgConfigService.getMsgConfigById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody Map<String, Object> msgConfigData) {
        return robotMsgConfigService.createMsgConfig(msgConfigData);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody Map<String, Object> msgConfigData) {
        return robotMsgConfigService.updateMsgConfig(id, msgConfigData);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return robotMsgConfigService.deleteMsgConfig(id);
    }
}
