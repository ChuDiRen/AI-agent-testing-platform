-- Copyright (c) 2025 左岚. All rights reserved.
-- SQLite数据库初始化数据

-- 插入默认角色
INSERT OR IGNORE INTO role (id, name, description) VALUES 
(1, 'ADMIN', '管理员'),
(2, 'USER', '普通用户');

-- 插入默认用户 (密码: admin123 的BCrypt加密值)
INSERT OR IGNORE INTO user (id, username, password, email, status) VALUES 
(1, 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iKXIGfR8f5.7JfZfZjKbKr.jHKGO', 'admin@example.com', 1);

-- 插入用户角色关联
INSERT OR IGNORE INTO user_role (user_id, role_id) VALUES 
(1, 1);
