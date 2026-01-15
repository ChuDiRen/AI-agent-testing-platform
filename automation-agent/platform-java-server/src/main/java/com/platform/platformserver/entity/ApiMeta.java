package com.platform.platformserver.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_api_meta")
public class ApiMeta extends BaseEntity {
    
    @TableField("project_id")
    private Integer projectId;
    
    @TableField("module_id")
    private Integer moduleId;
    
    @TableField("api_name")
    private String apiName;
    
    @TableField("request_method")
    private String requestMethod;
    
    @TableField("request_url")
    private String requestUrl;
    
    @TableField("request_params")
    private String requestParams;
    
    @TableField("request_headers")
    private String requestHeaders;
    
    @TableField("debug_vars")
    private String debugVars;
    
    @TableField("request_form_datas")
    private String requestFormDatas;
    
    @TableField("request_www_form_datas")
    private String requestWwwFormDatas;
    
    @TableField("requests_json_data")
    private String requestsJsonData;
    
    @TableField("request_files")
    private String requestFiles;
    
    @TableField("create_time")
    private LocalDateTime createTime;
}
