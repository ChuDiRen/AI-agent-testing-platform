package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_info_step")
public class ApiInfoCaseStep extends BaseEntity {
    
    @TableField("api_case_info_id")
    private Integer apiCaseInfoId;
    
    @TableField("key_word_id")
    private Integer keyWordId;
    
    @TableField("step_desc")
    private String stepDesc;
    
    @TableField("ref_variable")
    private String refVariable;
    
    @TableField("run_order")
    private Integer runOrder;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
