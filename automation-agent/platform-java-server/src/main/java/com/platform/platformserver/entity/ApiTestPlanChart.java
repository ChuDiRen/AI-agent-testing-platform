package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_test_plan_chart")
public class ApiTestPlanChart extends BaseEntity {
    
    @TableField("project_id")
    private Integer projectId;
    
    @TableField("chart_name")
    private String chartName;
    
    @TableField("chart_type")
    private String chartType;
    
    @TableField("chart_data")
    private String chartData;
    
    @TableField("chart_config")
    private String chartConfig;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
