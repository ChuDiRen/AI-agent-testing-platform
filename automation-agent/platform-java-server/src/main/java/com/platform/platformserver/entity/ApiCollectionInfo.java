package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_collection_info")
public class ApiCollectionInfo extends BaseEntity {
    
    @TableField("project_id")
    private Integer projectId;
    
    @TableField("collection_name")
    private String collectionName;
    
    @TableField("collection_desc")
    private String collectionDesc;
    
    @TableField("collection_env")
    private String collectionEnv;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
