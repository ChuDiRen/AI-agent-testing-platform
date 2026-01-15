package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_robot_config")
public class RobotConfig extends BaseEntity {
    
    @TableField("robot_name")
    private String robotName;
    
    @TableField("robot_type")
    private String robotType;
    
    @TableField("webhook_url")
    private String webhookUrl;
    
    @TableField("message_template")
    private String messageTemplate;
    
    @TableField("keywords")
    private String keywords;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
