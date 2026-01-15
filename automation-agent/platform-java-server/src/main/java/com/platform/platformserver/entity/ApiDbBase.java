package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_database")
public class ApiDbBase extends BaseEntity {
    
    @TableField("project_id")
    private Integer projectId;
    
    @TableField("name")
    private String name;
    
    @TableField("ref_name")
    private String refName;
    
    @TableField("db_type")
    private String dbType;
    
    @TableField("db_info")
    private String dbInfo;
    
    @TableField("is_enabled")
    private String isEnabled;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}