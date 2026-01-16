package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.RobotConfig;
import com.platform.platformserver.mapper.RobotConfigMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

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
    
    public Result<String> updateRobotConfig(Long id, Map<String, Object> configMap) {
        RobotConfig config = robotConfigMapper.selectById(id);
        if (config == null) {
            return Result.error("机器人配置不存在");
        }
        if (configMap.containsKey("robotName")) {
            config.setRobotName(configMap.get("robotName").toString());
        }
        if (configMap.containsKey("robotType")) {
            config.setRobotType(configMap.get("robotType").toString());
        }
        if (configMap.containsKey("webhookUrl")) {
            config.setWebhookUrl(configMap.get("webhookUrl").toString());
        }
        if (configMap.containsKey("messageTemplate")) {
            config.setMessageTemplate(configMap.get("messageTemplate").toString());
        }
        robotConfigMapper.updateById(config);
        return Result.success("机器人配置更新成功");
    }
    
    public Result<String> deleteRobotConfig(Long id) {
        robotConfigMapper.deleteById(id);
        return Result.success("机器人配置删除成功");
    }
    
    // 新增缺失的方法
    public Result<Page<RobotConfig>> queryByPage(Integer page, Integer pageSize) {
        Page<RobotConfig> pageParam = new Page<>(page, pageSize);
        QueryWrapper<RobotConfig> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        Page<RobotConfig> resultPage = robotConfigMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<Page<RobotConfig>> queryByPageWithFilter(Integer page, Integer pageSize, Integer projectId, String configName, String isEnabled) {
        Page<RobotConfig> pageParam = new Page<>(page, pageSize);
        QueryWrapper<RobotConfig> queryWrapper = new QueryWrapper<>();
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        if (configName != null && !configName.isEmpty()) {
            queryWrapper.like("robot_name", configName);
        }
        if (isEnabled != null) {
            queryWrapper.eq("is_enabled", isEnabled);
        }
        queryWrapper.orderByDesc("id");
        Page<RobotConfig> resultPage = robotConfigMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    // RobotMsgConfig相关方法
    public Result<List<RobotConfig>> getAllMsgConfigs() {
        QueryWrapper<RobotConfig> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<RobotConfig> configList = robotConfigMapper.selectList(queryWrapper);
        return Result.success(configList);
    }
    
    public Result<Page<RobotConfig>> getMsgConfigsByPage(Integer page, Integer pageSize, Long projectId, String msgType) {
        Page<RobotConfig> pageParam = new Page<>(page, pageSize);
        QueryWrapper<RobotConfig> queryWrapper = new QueryWrapper<>();
        if (projectId != null) {
            queryWrapper.eq("project_id", projectId);
        }
        if (msgType != null && !msgType.isEmpty()) {
            queryWrapper.like("msg_type", msgType);
        }
        queryWrapper.orderByDesc("id");
        Page<RobotConfig> resultPage = robotConfigMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<RobotConfig> getMsgConfigById(Long id) {
        RobotConfig config = robotConfigMapper.selectById(id);
        if (config == null) {
            return Result.error("消息配置不存在");
        }
        return Result.success(config);
    }
    
    public Result<String> createMsgConfig(Map<String, Object> configMap) {
        RobotConfig config = new RobotConfig();
        if (configMap.containsKey("robotName")) {
            config.setRobotName(configMap.get("robotName").toString());
        }
        if (configMap.containsKey("robotType")) {
            config.setRobotType(configMap.get("robotType").toString());
        }
        if (configMap.containsKey("webhookUrl")) {
            config.setWebhookUrl(configMap.get("webhookUrl").toString());
        }
        if (configMap.containsKey("messageTemplate")) {
            config.setMessageTemplate(configMap.get("messageTemplate").toString());
        }
        robotConfigMapper.insert(config);
        return Result.success("消息配置创建成功");
    }
    
    public Result<String> updateMsgConfig(Long id, Map<String, Object> configMap) {
        RobotConfig config = robotConfigMapper.selectById(id);
        if (config == null) {
            return Result.error("消息配置不存在");
        }
        if (configMap.containsKey("robotName")) {
            config.setRobotName(configMap.get("robotName").toString());
        }
        if (configMap.containsKey("robotType")) {
            config.setRobotType(configMap.get("robotType").toString());
        }
        if (configMap.containsKey("webhookUrl")) {
            config.setWebhookUrl(configMap.get("webhookUrl").toString());
        }
        if (configMap.containsKey("messageTemplate")) {
            config.setMessageTemplate(configMap.get("messageTemplate").toString());
        }
        robotConfigMapper.updateById(config);
        return Result.success("消息配置更新成功");
    }
    
    public Result<String> deleteMsgConfig(Long id) {
        robotConfigMapper.deleteById(id);
        return Result.success("消息配置删除成功");
    }
}