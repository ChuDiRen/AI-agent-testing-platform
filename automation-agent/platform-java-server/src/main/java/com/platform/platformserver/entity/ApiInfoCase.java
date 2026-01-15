package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_info_case")
public class ApiInfoCase extends BaseEntity {
    
    @TableField("project_id")
    private Integer projectId;
    
    @TableField("module_id")
    private Integer moduleId;
    
    @TableField("api_id")
    private Long apiId;
    
    @TableField("case_name")
    private String caseName;
    
    @TableField("case_desc")
    private String caseDesc;
    
    @TableField("param_data")
    private String paramData;
    
    @TableField("pre_request")
    private String preRequest;
    
    @TableField("post_request")
    private String postRequest;
    
    @TableField("debug_info")
    private String debugInfo;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
