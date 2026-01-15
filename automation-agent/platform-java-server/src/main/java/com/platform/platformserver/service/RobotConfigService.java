package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.RobotConfig;
import com.platform.platformserver.mapper.RobotConfigMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RobotConfigService {
    
    @Autowired
    private RobotConfigMapper robotConfigMapper;
    
    public Result<List<RobotConfig>> getRobotConfigList() {
        QueryWrapper<RobotConfig> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<RobotConfig> configList = robotConfigMapper.selectList(queryWrapper);
        return Result.success(configList);
    }
    
    public Result<RobotConfig> getRobotConfigById(Long id) {
        RobotConfig config = robotConfigMapper.selectById(id);
        if (config == null) {
            return Result.error("机器人配置不存在");
        }
        return Result.success(config);
    }
    
    public Result<String> createRobotConfig(RobotConfig config) {
        robotConfigMapper.insert(config);
        return Result.success("机器人配置创建成功");
    }
    
    public Result<String> updateRobotConfig(RobotConfig config) {
        robotConfigMapper.updateById(config);
        return Result.success("机器人配置更新成功");
    }
    
    public Result<String> deleteRobotConfig(Long id) {
        robotConfigMapper.deleteById(id);
        return Result.success("机器人配置删除成功");
    }
}