package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_project")
public class ApiProject extends BaseEntity {
    
    @TableField("project_name")
    private String projectName;
    
    @TableField("project_desc")
    private String projectDesc;
}
