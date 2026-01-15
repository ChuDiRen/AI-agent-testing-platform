package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_collection_detail")
public class ApiCollectionDetail extends BaseEntity {
    
    @TableField("collection_info_id")
    private Integer collectionInfoId;
    
    @TableField("api_info_id")
    private Integer apiInfoId;
    
    @TableField("run_order")
    private Integer runOrder;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
