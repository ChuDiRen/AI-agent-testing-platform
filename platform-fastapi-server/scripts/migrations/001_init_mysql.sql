-- ============================================
-- AI Agent Testing Platform - MySQL Schema
-- Generated: 2025-11-22 15:45:49
-- ============================================

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;


-- 系统管理模块
--------------------------------------------------------------------------------

-- 表: t_user
DROP TABLE IF EXISTS `t_user`;

CREATE TABLE t_user (
	id INT NOT NULL, 
	username VARCHAR NOT NULL, 
	password VARCHAR NOT NULL, 
	dept_id INT, 
	email VARCHAR, 
	mobile VARCHAR, 
	status VARCHAR NOT NULL, 
	ssex VARCHAR, 
	avatar VARCHAR, 
	description VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	last_login_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_role
DROP TABLE IF EXISTS `t_role`;

CREATE TABLE t_role (
	id INT NOT NULL, 
	role_name VARCHAR NOT NULL, 
	remark VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_menu
DROP TABLE IF EXISTS `t_menu`;

CREATE TABLE t_menu (
	id INT NOT NULL, 
	parent_id INT NOT NULL, 
	menu_name VARCHAR NOT NULL, 
	path VARCHAR, 
	component VARCHAR, 
	"query" VARCHAR, 
	perms VARCHAR, 
	icon VARCHAR, 
	menu_type VARCHAR NOT NULL, 
	visible VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	is_cache VARCHAR NOT NULL, 
	is_frame VARCHAR NOT NULL, 
	order_num INT NOT NULL, 
	remark VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_dept
DROP TABLE IF EXISTS `t_dept`;

CREATE TABLE t_dept (
	id INT NOT NULL, 
	parent_id INT NOT NULL, 
	dept_name VARCHAR NOT NULL, 
	order_num INT NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- API测试模块
--------------------------------------------------------------------------------

-- 表: t_api_project
DROP TABLE IF EXISTS `t_api_project`;

CREATE TABLE t_api_project (
	id INT NOT NULL, 
	project_name VARCHAR NOT NULL, 
	project_desc VARCHAR NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_database
DROP TABLE IF EXISTS `t_api_database`;

CREATE TABLE t_api_database (
	id INT NOT NULL, 
	project_id INT NOT NULL, 
	name VARCHAR NOT NULL, 
	ref_name VARCHAR NOT NULL, 
	db_type VARCHAR NOT NULL, 
	db_info VARCHAR NOT NULL, 
	is_enabled VARCHAR NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_keyword
DROP TABLE IF EXISTS `t_api_keyword`;

CREATE TABLE t_api_keyword (
	id INT NOT NULL, 
	name VARCHAR NOT NULL, 
	keyword_desc VARCHAR NOT NULL, 
	operation_type_id INT NOT NULL, 
	keyword_fun_name VARCHAR NOT NULL, 
	keyword_value VARCHAR NOT NULL, 
	is_enabled VARCHAR NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_operationtype
DROP TABLE IF EXISTS `t_api_operationtype`;

CREATE TABLE t_api_operationtype (
	id INT NOT NULL, 
	operation_type_name VARCHAR NOT NULL, 
	ex_fun_name VARCHAR NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_meta
DROP TABLE IF EXISTS `t_api_meta`;

CREATE TABLE t_api_meta (
	id INT NOT NULL, 
	project_id INT NOT NULL, 
	mate_name VARCHAR, 
	object_url VARCHAR, 
	file_type VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_info
DROP TABLE IF EXISTS `t_api_info`;

CREATE TABLE t_api_info (
	id INT NOT NULL, 
	project_id INT, 
	api_name VARCHAR, 
	request_method VARCHAR, 
	request_url VARCHAR, 
	request_params VARCHAR, 
	request_headers VARCHAR, 
	debug_vars VARCHAR, 
	request_form_datas VARCHAR, 
	request_www_form_datas VARCHAR, 
	requests_json_data VARCHAR, 
	request_files VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_info_group
DROP TABLE IF EXISTS `t_api_info_group`;

CREATE TABLE t_api_info_group (
	id INT NOT NULL, 
	project_id INT NOT NULL, 
	group_name VARCHAR NOT NULL, 
	group_desc VARCHAR, 
	parent_id INT NOT NULL, 
	order_num INT NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_info_case
DROP TABLE IF EXISTS `t_api_info_case`;

CREATE TABLE t_api_info_case (
	id INT NOT NULL, 
	project_id INT, 
	case_name VARCHAR NOT NULL, 
	case_desc VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_info_case_step
DROP TABLE IF EXISTS `t_api_info_case_step`;

CREATE TABLE t_api_info_case_step (
	id INT NOT NULL, 
	case_info_id INT NOT NULL, 
	run_order INT NOT NULL, 
	step_desc VARCHAR, 
	operation_type_id INT, 
	keyword_id INT, 
	step_data VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_collection_info
DROP TABLE IF EXISTS `t_api_collection_info`;

CREATE TABLE t_api_collection_info (
	id INT NOT NULL, 
	project_id INT, 
	plan_name VARCHAR NOT NULL, 
	plan_desc VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_collection_detail
DROP TABLE IF EXISTS `t_api_collection_detail`;

CREATE TABLE t_api_collection_detail (
	id INT NOT NULL, 
	collection_info_id INT NOT NULL, 
	case_info_id INT NOT NULL, 
	run_order INT NOT NULL, 
	ddt_data VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_api_history
DROP TABLE IF EXISTS `t_api_history`;

CREATE TABLE t_api_history (
	id INT NOT NULL, 
	api_info_id INT NOT NULL, 
	project_id INT NOT NULL, 
	plan_id INT, 
	case_info_id INT, 
	execution_uuid VARCHAR, 
	test_name VARCHAR NOT NULL, 
	test_status VARCHAR NOT NULL, 
	request_url VARCHAR, 
	request_method VARCHAR, 
	request_headers VARCHAR, 
	request_params VARCHAR, 
	request_body VARCHAR, 
	request_data VARCHAR, 
	response_data VARCHAR, 
	response_time INT, 
	status_code INT, 
	response_headers VARCHAR, 
	response_body VARCHAR, 
	error_message VARCHAR, 
	allure_report_path VARCHAR, 
	yaml_content VARCHAR, 
	execution_log VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	finish_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 消息管理模块
--------------------------------------------------------------------------------

-- 表: t_robot_config
DROP TABLE IF EXISTS `t_robot_config`;

CREATE TABLE t_robot_config (
	id INT NOT NULL, 
	robot_type VARCHAR NOT NULL, 
	robot_name VARCHAR NOT NULL, 
	webhook_url VARCHAR NOT NULL, 
	secret_key VARCHAR, 
	is_enabled BOOLEAN NOT NULL, 
	description VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	update_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	last_test_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: t_robot_msg_config
DROP TABLE IF EXISTS `t_robot_msg_config`;

CREATE TABLE t_robot_msg_config (
	id INT NOT NULL, 
	robot_id INT NOT NULL, 
	msg_type VARCHAR NOT NULL, 
	template_name VARCHAR NOT NULL, 
	template_content VARCHAR NOT NULL, 
	variables VARCHAR, 
	is_enabled BOOLEAN NOT NULL, 
	description VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	update_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(robot_id) REFERENCES t_robot_config (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- AI助手模块
--------------------------------------------------------------------------------

-- 表: ai_model
DROP TABLE IF EXISTS `ai_model`;

CREATE TABLE ai_model (
	id INT NOT NULL, 
	model_name VARCHAR NOT NULL, 
	model_code VARCHAR NOT NULL, 
	provider VARCHAR NOT NULL, 
	api_url VARCHAR NOT NULL, 
	api_key VARCHAR, 
	is_enabled BOOLEAN NOT NULL, 
	description VARCHAR, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (model_code)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: ai_conversation
DROP TABLE IF EXISTS `ai_conversation`;

CREATE TABLE ai_conversation (
	id INT NOT NULL, 
	user_id INT NOT NULL, 
	session_title VARCHAR NOT NULL, 
	model_id INT NOT NULL, 
	test_type VARCHAR, 
	project_id INT, 
	status VARCHAR NOT NULL, 
	message_count INT NOT NULL, 
	test_case_count INT NOT NULL, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	update_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	last_message_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: ai_message
DROP TABLE IF EXISTS `ai_message`;

CREATE TABLE ai_message (
	id INT NOT NULL, 
	conversation_id INT NOT NULL, 
	role VARCHAR NOT NULL, 
	content TEXT NOT NULL, 
	message_type VARCHAR NOT NULL, 
	test_cases_json TEXT, 
	message_metadata TEXT, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: prompt_template
DROP TABLE IF EXISTS `prompt_template`;

CREATE TABLE prompt_template (
	id INT NOT NULL, 
	name VARCHAR NOT NULL, 
	template_type VARCHAR NOT NULL, 
	test_type VARCHAR NOT NULL, 
	content TEXT NOT NULL, 
	variables VARCHAR, 
	is_active BOOLEAN NOT NULL, 
	created_by INT, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 表: test_case
DROP TABLE IF EXISTS `test_case`;

CREATE TABLE test_case (
	id INT NOT NULL, 
	case_name VARCHAR NOT NULL, 
	project_id INT NOT NULL, 
	module_name VARCHAR, 
	test_type VARCHAR NOT NULL, 
	priority VARCHAR NOT NULL, 
	precondition TEXT, 
	test_steps TEXT, 
	expected_result TEXT, 
	test_data TEXT, 
	case_format VARCHAR NOT NULL, 
	yaml_content TEXT, 
	created_by INT, 
	create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	modify_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


SET FOREIGN_KEY_CHECKS = 1;