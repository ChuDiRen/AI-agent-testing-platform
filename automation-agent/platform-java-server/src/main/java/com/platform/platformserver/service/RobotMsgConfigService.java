package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.RobotMsgConfig;
import com.platform.platformserver.mapper.RobotMsgConfigMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class RobotMsgConfigService {
    
    @Autowired
    private RobotMsgConfigMapper robotMsgConfigMapper;
    
    public Result<List<RobotMsgConfig>> getAllMsgConfigs() {
        QueryWrapper<RobotMsgConfig> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("id");
        List<RobotMsgConfig> configList = robotMsgConfigMapper.selectList(queryWrapper);
        return Result.success(configList);
    }
    
    public Result<Page<RobotMsgConfig>> getMsgConfigsByPage(Integer page, Integer pageSize, Long robotId, String msgType) {
        Page<RobotMsgConfig> pageParam = new Page<>(page, pageSize);
        QueryWrapper<RobotMsgConfig> queryWrapper = new QueryWrapper<>();
        if (robotId != null) {
            queryWrapper.eq("robot_id", robotId);
        }
        if (msgType != null && !msgType.isEmpty()) {
            queryWrapper.like("msg_type", msgType);
        }
        queryWrapper.orderByDesc("id");
        Page<RobotMsgConfig> resultPage = robotMsgConfigMapper.selectPage(pageParam, queryWrapper);
        return Result.success(resultPage);
    }
    
    public Result<RobotMsgConfig> getMsgConfigById(Long id) {
        RobotMsgConfig config = robotMsgConfigMapper.selectById(id);
        if (config == null) {
            return Result.error("消息配置不存在");
        }
        return Result.success(config);
    }
    
    public Result<String> createMsgConfig(Map<String, Object> configMap) {
        RobotMsgConfig config = new RobotMsgConfig();
        if (configMap.containsKey("robotId")) {
            config.setRobotId(Integer.valueOf(configMap.get("robotId").toString()));
        }
        if (configMap.containsKey("msgType")) {
            config.setMsgType(configMap.get("msgType").toString());
        }
        if (configMap.containsKey("msgContent")) {
            config.setMsgContent(configMap.get("msgContent").toString());
        }
        if (configMap.containsKey("msgVars")) {
            config.setMsgVars(configMap.get("msgVars").toString());
        }
        if (configMap.containsKey("isEnabled")) {
            config.setIsEnabled(configMap.get("isEnabled").toString());
        }
        robotMsgConfigMapper.insert(config);
        return Result.success("消息配置创建成功");
    }
    
    public Result<String> updateMsgConfig(Long id, Map<String, Object> configMap) {
        RobotMsgConfig config = robotMsgConfigMapper.selectById(id);
        if (config == null) {
            return Result.error("消息配置不存在");
        }
        if (configMap.containsKey("robotId")) {
            config.setRobotId(Integer.valueOf(configMap.get("robotId").toString()));
        }
        if (configMap.containsKey("msgType")) {
            config.setMsgType(configMap.get("msgType").toString());
        }
        if (configMap.containsKey("msgContent")) {
            config.setMsgContent(configMap.get("msgContent").toString());
        }
        if (configMap.containsKey("msgVars")) {
            config.setMsgVars(configMap.get("msgVars").toString());
        }
        if (configMap.containsKey("isEnabled")) {
            config.setIsEnabled(configMap.get("isEnabled").toString());
        }
        robotMsgConfigMapper.updateById(config);
        return Result.success("消息配置更新成功");
    }
    
    public Result<String> deleteMsgConfig(Long id) {
        robotMsgConfigMapper.deleteById(id);
        return Result.success("消息配置删除成功");
    }
}
