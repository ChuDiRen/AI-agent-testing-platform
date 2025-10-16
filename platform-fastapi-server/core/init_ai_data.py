"""初始化AI相关数据：模型、提示词模板"""
from sqlmodel import Session, select
from aiassistant.model.AiModel import AiModel
from aiassistant.model.PromptTemplate import PromptTemplate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def init_ai_models(session: Session):
    """初始化AI模型数据"""
    # 检查是否已存在数据
    existing_models = session.exec(select(AiModel)).first()
    if existing_models:
        logger.info("AI模型数据已存在，跳过初始化")
        return
    
    ai_models = [
        {
            "model_name": "DeepSeek-Chat",
            "model_code": "deepseek-chat",
            "provider": "DeepSeek",
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "api_key": "",  # 需要用户配置
            "is_enabled": False,
            "description": "DeepSeek AI对话模型，支持流式输出，适合生成测试用例"
        },
        {
            "model_name": "通义千问-Max",
            "model_code": "qwen-max",
            "provider": "阿里云",
            "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "api_key": "",
            "is_enabled": False,
            "description": "阿里云通义千问大模型，支持中文场景"
        },
        {
            "model_name": "通义千问-Plus",
            "model_code": "qwen-plus",
            "provider": "阿里云",
            "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "api_key": "",
            "is_enabled": False,
            "description": "阿里云通义千问Plus模型"
        },
        {
            "model_name": "文心一言-4.0",
            "model_code": "ernie-4.0",
            "provider": "百度",
            "api_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
            "api_key": "",
            "is_enabled": False,
            "description": "百度文心一言4.0模型"
        },
        {
            "model_name": "ChatGPT-4",
            "model_code": "gpt-4",
            "provider": "OpenAI",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "",
            "is_enabled": False,
            "description": "OpenAI GPT-4模型，功能强大"
        },
        {
            "model_name": "ChatGPT-3.5-Turbo",
            "model_code": "gpt-3.5-turbo",
            "provider": "OpenAI",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "",
            "is_enabled": False,
            "description": "OpenAI GPT-3.5 Turbo模型，性价比高"
        },
        {
            "model_name": "Kimi",
            "model_code": "moonshot-v1",
            "provider": "Moonshot",
            "api_url": "https://api.moonshot.cn/v1/chat/completions",
            "api_key": "",
            "is_enabled": False,
            "description": "月之暗面Kimi模型，支持超长上下文"
        },
        {
            "model_name": "智谱AI-GLM-4",
            "model_code": "glm-4",
            "provider": "智谱AI",
            "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "api_key": "",
            "is_enabled": False,
            "description": "智谱AI GLM-4模型"
        },
        {
            "model_name": "讯飞星火-3.5",
            "model_code": "spark-3.5",
            "provider": "讯飞",
            "api_url": "https://spark-api.xf-yun.com/v3.5/chat",
            "api_key": "",
            "is_enabled": False,
            "description": "讯飞星火认知大模型3.5"
        },
        {
            "model_name": "Claude-3-Opus",
            "model_code": "claude-3-opus",
            "provider": "Anthropic",
            "api_url": "https://api.anthropic.com/v1/messages",
            "api_key": "",
            "is_enabled": False,
            "description": "Anthropic Claude-3 Opus模型"
        }
    ]
    
    for model_data in ai_models:
        model = AiModel(**model_data, create_time=datetime.now(), modify_time=datetime.now())
        session.add(model)
    
    session.commit()
    logger.info(f"成功初始化{len(ai_models)}个AI模型")


def init_prompt_templates(session: Session):
    """初始化提示词模板"""
    # 检查是否已存在数据
    existing_templates = session.exec(select(PromptTemplate)).first()
    if existing_templates:
        logger.info("提示词模板数据已存在，跳过初始化")
        return
    
    prompt_templates = [
        {
            "name": "API测试用例生成-System",
            "template_type": "system",
            "test_type": "API",
            "content": """你是一位专业的API测试工程师。你的任务是根据用户的需求生成{case_count}个高质量的API测试用例。

请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称（清晰描述测试场景）
- priority: 优先级（P0/P1/P2/P3，P0为最高）
- precondition: 前置条件（测试执行前需要满足的条件）
- test_steps: 测试步骤（数组格式，每个步骤清晰具体）
- expected_result: 预期结果（明确的验证点）

测试用例要求：
1. 覆盖正常流程、边界情况和异常情况
2. 优先级合理分配（核心功能P0，重要功能P1，次要功能P2，边缘情况P3）
3. 测试步骤详细、可执行
4. 预期结果明确、可验证

请直接返回JSON数组，不要添加其他说明文字。""",
            "variables": '["case_count", "test_type"]',
            "is_active": True
        },
        {
            "name": "Web测试用例生成-System",
            "template_type": "system",
            "test_type": "Web",
            "content": """你是一位专业的Web UI测试工程师。你的任务是根据用户的需求生成{case_count}个高质量的Web测试用例。

请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称
- priority: 优先级（P0/P1/P2/P3）
- precondition: 前置条件
- test_steps: 测试步骤（数组格式，包括页面导航、元素定位、用户操作）
- expected_result: 预期结果

Web测试特别要求：
1. 测试步骤包含具体的页面元素（按钮、输入框、链接等）
2. 考虑浏览器兼容性
3. 包含页面加载、渲染、交互等方面
4. 覆盖响应式布局场景

请直接返回JSON数组，不要添加其他说明文字。""",
            "variables": '["case_count"]',
            "is_active": True
        },
        {
            "name": "App测试用例生成-System",
            "template_type": "system",
            "test_type": "App",
            "content": """你是一位专业的移动应用测试工程师。你的任务是根据用户的需求生成{case_count}个高质量的App测试用例。

请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称
- priority: 优先级（P0/P1/P2/P3）
- precondition: 前置条件
- test_steps: 测试步骤（数组格式，包括页面跳转、手势操作、权限请求等）
- expected_result: 预期结果

App测试特别要求：
1. 考虑iOS和Android平台差异
2. 包含特殊场景：网络切换、后台运行、通知推送、权限授权等
3. 考虑不同屏幕尺寸和分辨率
4. 包含性能和电量消耗测试场景

请直接返回JSON数组，不要添加其他说明文字。""",
            "variables": '["case_count"]',
            "is_active": True
        },
        {
            "name": "通用测试用例生成-System",
            "template_type": "system",
            "test_type": "通用",
            "content": """你是一位经验丰富的软件测试工程师。你的任务是根据用户的需求生成{case_count}个测试用例。

请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称
- priority: 优先级（P0/P1/P2/P3）
- precondition: 前置条件
- test_steps: 测试步骤（数组格式）
- expected_result: 预期结果

测试用例要求：
1. 清晰、具体、可执行
2. 覆盖正常流程和异常情况
3. 优先级合理分配
4. 预期结果明确

请直接返回JSON数组，不要添加其他说明文字。""",
            "variables": '["case_count"]',
            "is_active": True
        }
    ]
    
    for template_data in prompt_templates:
        template = PromptTemplate(**template_data, create_time=datetime.now(), modify_time=datetime.now())
        session.add(template)
    
    session.commit()
    logger.info(f"成功初始化{len(prompt_templates)}个提示词模板")


def init_all_ai_data(session: Session):
    """初始化所有AI相关数据"""
    try:
        init_ai_models(session)
        init_prompt_templates(session)
        logger.info("AI数据初始化完成")
    except Exception as e:
        logger.error(f"AI数据初始化失败: {str(e)}")
        session.rollback()
        raise

