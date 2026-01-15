package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_history")
public class ApiHistory extends BaseEntity {
    
    @TableField("case_id")
    private Long caseId;
    
    @TableField("api_id")
    private Long apiId;
    
    @TableField("status")
    private String status;
    
    @TableField("response_time")
    private Long responseTime;
    
    @TableField("response_code")
    private Integer responseCode;
    
    @TableField("response_body")
    private String responseBody;
    
    @TableField("execute_time")
    private LocalDateTime executeTime;
    
    @TableField("collection_info_id")
    private Integer collectionInfoId;
    
    @TableField("history_desc")
    private String historyDesc;
    
    @TableField("history_detail")
    private String historyDetail;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
