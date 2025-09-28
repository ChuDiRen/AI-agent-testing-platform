// Copyright (c) 2025 左岚. All rights reserved.
package com.example.aiagent.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.springframework.lang.Nullable;

/**
 * 用户实体类
 * 
 * @author 左岚团队
 * @version 1.0.0
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_user")
public class User extends BaseEntity {

    /**
     * 用户名
     */
    @TableField("username")
    private String username;

    /**
     * 密码
     */
    @TableField("password")
    private String password;

    /**
     * 邮箱
     */
    @TableField("email")
    private String email;

    /**
     * 手机号
     */
    @TableField("phone")
    private String phone;

    /**
     * 真实姓名
     */
    @TableField("real_name")
    private String realName;

    /**
     * 头像URL
     */
    @TableField("avatar")
    @Nullable // 头像可以为空
    private String avatar;

    /**
     * 状态（0-禁用，1-启用）
     */
    @TableField("status")
    private Integer status;

    /**
     * 部门ID
     */
    @TableField("department_id")
    @Nullable // 部门ID可以为空
    private Long departmentId;

    /**
     * 最后登录时间
     */
    @TableField("last_login_time")
    @Nullable // 最后登录时间可以为空
    private java.time.LocalDateTime lastLoginTime;

    /**
     * 最后登录IP
     */
    @TableField("last_login_ip")
    @Nullable // 最后登录IP可以为空
    private String lastLoginIp;

    /**
     * 备注
     */
    @TableField("remark")
    @Nullable // 备注可以为空
    private String remark;
}
