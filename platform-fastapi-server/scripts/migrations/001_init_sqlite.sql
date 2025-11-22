-- ============================================
-- AI Agent Testing Platform - SQLite Schema
-- Generated: 2025-11-22 15:45:45
-- ============================================


-- 系统管理模块
--------------------------------------------------------------------------------

-- 表: t_user

CREATE TABLE t_user (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	password VARCHAR NOT NULL, 
	dept_id INTEGER, 
	email VARCHAR, 
	mobile VARCHAR, 
	status VARCHAR NOT NULL, 
	ssex VARCHAR, 
	avatar VARCHAR, 
	description VARCHAR, 
	create_time DATETIME, 
	modify_time DATETIME, 
	last_login_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_role

CREATE TABLE t_role (
	id INTEGER NOT NULL, 
	role_name VARCHAR NOT NULL, 
	remark VARCHAR, 
	create_time DATETIME, 
	modify_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_menu

CREATE TABLE t_menu (
	id INTEGER NOT NULL, 
	parent_id INTEGER NOT NULL, 
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
	order_num INTEGER NOT NULL, 
	remark VARCHAR, 
	create_time DATETIME, 
	modify_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_dept

CREATE TABLE t_dept (
	id INTEGER NOT NULL, 
	parent_id INTEGER NOT NULL, 
	dept_name VARCHAR NOT NULL, 
	order_num INTEGER NOT NULL, 
	create_time DATETIME, 
	modify_time DATETIME, 
	PRIMARY KEY (id)
)

;


-- API测试模块
--------------------------------------------------------------------------------

-- 表: t_api_project

CREATE TABLE t_api_project (
	id INTEGER NOT NULL, 
	project_name VARCHAR NOT NULL, 
	project_desc VARCHAR NOT NULL, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_database

CREATE TABLE t_api_database (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	ref_name VARCHAR NOT NULL, 
	db_type VARCHAR NOT NULL, 
	db_info VARCHAR NOT NULL, 
	is_enabled VARCHAR NOT NULL, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_keyword

CREATE TABLE t_api_keyword (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	keyword_desc VARCHAR NOT NULL, 
	operation_type_id INTEGER NOT NULL, 
	keyword_fun_name VARCHAR NOT NULL, 
	keyword_value VARCHAR NOT NULL, 
	is_enabled VARCHAR NOT NULL, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_operationtype

CREATE TABLE t_api_operationtype (
	id INTEGER NOT NULL, 
	operation_type_name VARCHAR NOT NULL, 
	ex_fun_name VARCHAR NOT NULL, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_meta

CREATE TABLE t_api_meta (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	mate_name VARCHAR, 
	object_url VARCHAR, 
	file_type VARCHAR, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_info

CREATE TABLE t_api_info (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
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
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_info_group

CREATE TABLE t_api_info_group (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	group_name VARCHAR NOT NULL, 
	group_desc VARCHAR, 
	parent_id INTEGER NOT NULL, 
	order_num INTEGER NOT NULL, 
	create_time DATETIME, 
	modify_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_info_case

CREATE TABLE t_api_info_case (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
	case_name VARCHAR NOT NULL, 
	case_desc VARCHAR, 
	create_time DATETIME, 
	modify_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_info_case_step

CREATE TABLE t_api_info_case_step (
	id INTEGER NOT NULL, 
	case_info_id INTEGER NOT NULL, 
	run_order INTEGER NOT NULL, 
	step_desc VARCHAR, 
	operation_type_id INTEGER, 
	keyword_id INTEGER, 
	step_data VARCHAR, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_collection_info

CREATE TABLE t_api_collection_info (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
	plan_name VARCHAR NOT NULL, 
	plan_desc VARCHAR, 
	create_time DATETIME, 
	modify_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_collection_detail

CREATE TABLE t_api_collection_detail (
	id INTEGER NOT NULL, 
	collection_info_id INTEGER NOT NULL, 
	case_info_id INTEGER NOT NULL, 
	run_order INTEGER NOT NULL, 
	ddt_data VARCHAR, 
	create_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_api_history

CREATE TABLE t_api_history (
	id INTEGER NOT NULL, 
	api_info_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	plan_id INTEGER, 
	case_info_id INTEGER, 
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
	response_time INTEGER, 
	status_code INTEGER, 
	response_headers VARCHAR, 
	response_body VARCHAR, 
	error_message VARCHAR, 
	allure_report_path VARCHAR, 
	yaml_content VARCHAR, 
	execution_log VARCHAR, 
	create_time DATETIME, 
	modify_time DATETIME, 
	finish_time DATETIME, 
	PRIMARY KEY (id)
)

;


-- 消息管理模块
--------------------------------------------------------------------------------

-- 表: t_robot_config

CREATE TABLE t_robot_config (
	id INTEGER NOT NULL, 
	robot_type VARCHAR NOT NULL, 
	robot_name VARCHAR NOT NULL, 
	webhook_url VARCHAR NOT NULL, 
	secret_key VARCHAR, 
	is_enabled BOOLEAN NOT NULL, 
	description VARCHAR, 
	create_time DATETIME, 
	update_time DATETIME, 
	last_test_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: t_robot_msg_config

CREATE TABLE t_robot_msg_config (
	id INTEGER NOT NULL, 
	robot_id INTEGER NOT NULL, 
	msg_type VARCHAR NOT NULL, 
	template_name VARCHAR NOT NULL, 
	template_content VARCHAR NOT NULL, 
	variables VARCHAR, 
	is_enabled BOOLEAN NOT NULL, 
	description VARCHAR, 
	create_time DATETIME, 
	update_time DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(robot_id) REFERENCES t_robot_config (id)
)

;


-- AI助手模块
--------------------------------------------------------------------------------

-- 表: ai_model

CREATE TABLE ai_model (
	id INTEGER NOT NULL, 
	model_name VARCHAR NOT NULL, 
	model_code VARCHAR NOT NULL, 
	provider VARCHAR NOT NULL, 
	api_url VARCHAR NOT NULL, 
	api_key VARCHAR, 
	is_enabled BOOLEAN NOT NULL, 
	description VARCHAR, 
	create_time DATETIME NOT NULL, 
	modify_time DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (model_code)
)

;

-- 表: ai_conversation

CREATE TABLE ai_conversation (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	session_title VARCHAR NOT NULL, 
	model_id INTEGER NOT NULL, 
	test_type VARCHAR, 
	project_id INTEGER, 
	status VARCHAR NOT NULL, 
	message_count INTEGER NOT NULL, 
	test_case_count INTEGER NOT NULL, 
	create_time DATETIME NOT NULL, 
	update_time DATETIME NOT NULL, 
	last_message_time DATETIME, 
	PRIMARY KEY (id)
)

;

-- 表: ai_message

CREATE TABLE ai_message (
	id INTEGER NOT NULL, 
	conversation_id INTEGER NOT NULL, 
	role VARCHAR NOT NULL, 
	content TEXT NOT NULL, 
	message_type VARCHAR NOT NULL, 
	test_cases_json TEXT, 
	message_metadata TEXT, 
	create_time DATETIME NOT NULL, 
	PRIMARY KEY (id)
)

;

-- 表: prompt_template

CREATE TABLE prompt_template (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	template_type VARCHAR NOT NULL, 
	test_type VARCHAR NOT NULL, 
	content TEXT NOT NULL, 
	variables VARCHAR, 
	is_active BOOLEAN NOT NULL, 
	created_by INTEGER, 
	create_time DATETIME NOT NULL, 
	modify_time DATETIME NOT NULL, 
	PRIMARY KEY (id)
)

;

-- 表: test_case

CREATE TABLE test_case (
	id INTEGER NOT NULL, 
	case_name VARCHAR NOT NULL, 
	project_id INTEGER NOT NULL, 
	module_name VARCHAR, 
	test_type VARCHAR NOT NULL, 
	priority VARCHAR NOT NULL, 
	precondition TEXT, 
	test_steps TEXT, 
	expected_result TEXT, 
	test_data TEXT, 
	case_format VARCHAR NOT NULL, 
	yaml_content TEXT, 
	created_by INTEGER, 
	create_time DATETIME NOT NULL, 
	modify_time DATETIME NOT NULL, 
	PRIMARY KEY (id)
)

;
