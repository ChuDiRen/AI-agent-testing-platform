package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_operation_type")
public class ApiOperationType extends BaseEntity {
    
    @TableField("operation_type_name")
    private String operationTypeName;
    
    @TableField("operation_type_desc")
    private String operationTypeDesc;
    
    @TableField("operation_type_fun_name")
    private String operationTypeFunName;
    
    @TableField("operation_type_value")
    private String operationTypeValue;
    
    @TableField("is_enabled")
    private String isEnabled;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
