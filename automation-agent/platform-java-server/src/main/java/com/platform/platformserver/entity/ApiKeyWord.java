package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_keyword")
public class ApiKeyWord extends BaseEntity {
    
    @TableField("name")
    private String name;
    
    @TableField("keyword_desc")
    private String keywordDesc;
    
    @TableField("operation_type_id")
    private Integer operationTypeId;
    
    @TableField("keyword_fun_name")
    private String keywordFunName;
    
    @TableField("keyword_value")
    private String keywordValue;
    
    @TableField("is_enabled")
    private String isEnabled;
    
    @TableField("page_id")
    private Integer pageId;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
