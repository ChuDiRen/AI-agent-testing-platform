package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_robot_msg_config")
public class RobotMsgConfig extends BaseEntity {
    
    @TableField("robot_id")
    private Integer robotId;
    
    @TableField("msg_type")
    private String msgType;
    
    @TableField("msg_content")
    private String msgContent;
    
    @TableField("msg_vars")
    private String msgVars;
    
    @TableField("is_enabled")
    private String isEnabled;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
