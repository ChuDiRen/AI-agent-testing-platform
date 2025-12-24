-- =====================================================
-- 消息模板表 DDL
-- 创建时间: 2025-12-24
-- 说明: 支持自定义消息模板，变量替换 {{variable}}
-- =====================================================

-- 删除已存在的表（谨慎使用）
-- DROP TABLE IF EXISTS `msg_template`;

-- 创建消息模板表
CREATE TABLE IF NOT EXISTS `msg_template` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `template_code` VARCHAR(50) NOT NULL COMMENT '模板编码（唯一标识）',
    `template_name` VARCHAR(100) NOT NULL COMMENT '模板名称',
    `template_type` VARCHAR(20) NOT NULL COMMENT '模板类型：verify-验证码, notify-通知, marketing-营销, warning-告警, system-系统',
    `channel_type` VARCHAR(20) NOT NULL COMMENT '渠道类型：system-站内消息, email-邮件, sms-短信, wechat-微信, dingtalk-钉钉',
    `title` VARCHAR(200) DEFAULT '' COMMENT '消息标题（站内消息/邮件使用）',
    `content` TEXT NOT NULL COMMENT '模板内容，支持{{variable}}变量',
    `variables` TEXT DEFAULT '[]' COMMENT '变量列表JSON，例：[{"name":"code","desc":"验证码"}]',
    `example_params` TEXT DEFAULT '{}' COMMENT '示例参数JSON，用于预览',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态：0-禁用, 1-启用',
    `remark` VARCHAR(500) DEFAULT '' COMMENT '备注说明',
    `created_by` VARCHAR(50) DEFAULT '' COMMENT '创建人',
    `created_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_template_code` (`template_code`),
    KEY `idx_template_type` (`template_type`),
    KEY `idx_channel_type` (`channel_type`),
    KEY `idx_status` (`status`),
    KEY `idx_created_time` (`created_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息模板表';

-- =====================================================
-- 初始化数据
-- =====================================================

-- 验证码模板（站内消息）
INSERT INTO `msg_template` (`template_code`, `template_name`, `template_type`, `channel_type`, `title`, `content`, `variables`, `example_params`, `status`, `remark`) VALUES
('VERIFY_CODE_SYSTEM', '验证码通知（站内消息）', 'verify', 'system', '验证码通知', '您好，{{userName}}！\n\n您的验证码是：{{code}}，有效时间{{expire}}分钟。\n\n请勿泄露给他人。', '[{"name":"userName","desc":"用户名"},{"name":"code","desc":"验证码"},{"name":"expire","desc":"有效期（分钟）"}]', '{"userName":"张三","code":"123456","expire":"5"}', 1, '站内消息验证码模板'),

-- 验证码模板（短信）
('VERIFY_CODE_SMS', '验证码通知（短信）', 'verify', 'sms', '', '【测试平台】您的验证码是{{code}}，{{expire}}分钟内有效，请勿泄露。', '[{"name":"code","desc":"验证码"},{"name":"expire","desc":"有效期（分钟）"}]', '{"code":"123456","expire":"5"}', 1, '短信验证码模板'),

-- 测试任务完成通知
('TEST_TASK_COMPLETE', '测试任务完成通知', 'notify', 'system', '测试任务完成', '您好，{{userName}}！\n\n测试任务《{{taskName}}》已执行完成。\n\n执行结果：{{result}}\n成功：{{successCount}}条，失败：{{failCount}}条\n执行时间：{{executeTime}}', '[{"name":"userName","desc":"用户名"},{"name":"taskName","desc":"任务名称"},{"name":"result","desc":"执行结果"},{"name":"successCount","desc":"成功数量"},{"name":"failCount","desc":"失败数量"},{"name":"executeTime","desc":"执行时间"}]', '{"userName":"张三","taskName":"登录接口测试","result":"通过","successCount":"10","failCount":"0","executeTime":"2025-12-24 10:00:00"}', 1, '测试任务完成通知模板'),

-- 告警消息模板
('ALERT_MESSAGE', '系统告警通知', 'warning', 'system', '【告警】{{alertLevel}} - {{alertTitle}}', '告警时间：{{alertTime}}\n告警级别：{{alertLevel}}\n告警内容：{{alertContent}}\n\n请及时处理！', '[{"name":"alertLevel","desc":"告警级别"},{"name":"alertTitle","desc":"告警标题"},{"name":"alertTime","desc":"告警时间"},{"name":"alertContent","desc":"告警内容"}]', '{"alertLevel":"严重","alertTitle":"接口响应超时","alertTime":"2025-12-24 10:00:00","alertContent":"API /api/user/list 响应时间超过5秒"}', 1, '系统告警通知模板');

-- =====================================================
-- 查询示例
-- =====================================================

-- 1. 查询所有启用的模板
-- SELECT * FROM msg_template WHERE status = 1;

-- 2. 查询特定类型的模板
-- SELECT * FROM msg_template WHERE template_type = 'verify' AND status = 1;

-- 3. 查询特定渠道的模板
-- SELECT * FROM msg_template WHERE channel_type = 'system' AND status = 1;

-- 4. 根据模板编码查询
-- SELECT * FROM msg_template WHERE template_code = 'VERIFY_CODE_SYSTEM';
