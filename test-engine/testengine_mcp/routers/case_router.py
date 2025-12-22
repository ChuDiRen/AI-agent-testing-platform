"""
用例管理路由
提供 4 种测试用例的生成、查询、删除功能
"""
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException
import yaml

from ..models import (
    GenerateApiCaseRequest,
    GenerateWebCaseRequest,
    GenerateMobileCaseRequest,
    GeneratePerfCaseRequest,
    GenerateFromYamlRequest
)
from ..services.generators import get_case_generator

router = APIRouter(prefix="/cases", tags=["用例管理"])


# ============== 用例生成端点 ==============

@router.post("/generate/api", summary="生成 API 测试用例")
async def generate_api_case(request: GenerateApiCaseRequest):
    """
    生成 API 测试用例
    
    输出格式（format 参数）:
    - `pytest`: 生成 Python pytest 脚本（默认）
    - `yaml`: 生成 YAML 格式用例
    
    支持的断言类型:
    - `status_code`: 状态码断言
    - `contains`: 响应包含文本
    - `equals`: 精确匹配
    - `jsonpath`: JSON 路径断言
    - `response_time`: 响应时间断言
    - `json_length`: JSON 数组长度断言
    """
    generator = get_case_generator()
    
    extracts = [e.model_dump() for e in request.extracts] if request.extracts else None
    asserts = [a.model_dump() for a in request.asserts] if request.asserts else None
    
    return generator.generate_api_case(
        name=request.name,
        description=request.description,
        url=request.url,
        method=request.method,
        headers=request.headers,
        params=request.params,
        data=request.data,
        json_body=request.json_body,
        extracts=extracts,
        asserts=asserts,
        save_path=request.save_path,
        format=request.format,
        feature=request.feature,
        story=request.story
    )


@router.post("/generate/web", summary="生成 Web 测试用例")
async def generate_web_case(request: GenerateWebCaseRequest):
    """
    生成 Web 测试用例
    
    输出格式（format 参数）:
    - `pytest`: 生成 Python pytest 脚本（默认）
    - `yaml`: 生成 YAML 格式用例
    
    支持的操作类型:
    - 交互: `click`, `input`, `clear`, `select`, `hover`, `double_click`
    - 等待: `wait`, `wait_element`
    - 导航: `scroll`, `screenshot`
    - 断言: `assert_text`, `assert_title`, `assert_url`, `assert_element`, `assert_element_text`
    """
    generator = get_case_generator()
    actions = [a.model_dump() for a in request.actions] if request.actions else None
    
    return generator.generate_web_case(
        name=request.name,
        description=request.description,
        url=request.url,
        browser=request.browser,
        headless=request.headless,
        actions=actions,
        save_path=request.save_path,
        format=request.format,
        feature=request.feature,
        story=request.story
    )


@router.post("/generate/mobile", summary="生成 Mobile 测试用例")
async def generate_mobile_case(request: GenerateMobileCaseRequest):
    """
    生成 Mobile 测试用例
    
    输出格式（format 参数）:
    - `pytest`: 生成 Python pytest 脚本（默认）
    - `yaml`: 生成 YAML 格式用例
    
    支持的操作类型:
    - 交互: `click`, `input`, `clear`, `long_press`, `swipe`, `tap`
    - 等待: `wait`, `wait_element`
    - 系统: `back`, `home`, `screenshot`
    - 断言: `assert_text`, `assert_element`, `assert_toast`
    """
    generator = get_case_generator()
    actions = [a.model_dump() for a in request.actions] if request.actions else None
    
    return generator.generate_mobile_case(
        name=request.name,
        description=request.description,
        platform=request.platform,
        app_package=request.app_package,
        app_activity=request.app_activity,
        bundle_id=request.bundle_id,
        actions=actions,
        save_path=request.save_path,
        format=request.format,
        feature=request.feature,
        story=request.story
    )


@router.post("/generate/perf", summary="生成性能测试用例")
async def generate_perf_case(request: GeneratePerfCaseRequest):
    """
    生成性能测试用例
    
    输出格式（format 参数）:
    - `pytest`: 生成 Locust Python 脚本（默认）
    - `yaml`: 生成 YAML 格式用例
    
    场景配置:
    - `method`: HTTP 方法
    - `url`: 请求路径
    - `name`: 请求名称（报告分组）
    
    断言配置:
    - `check_status`: 状态码检查
    - `check_response_time`: 响应时间检查
    - `check_contains`: 响应内容检查
    - `validate_json`: JSON 验证
    """
    generator = get_case_generator()
    
    # 处理 json_body -> json 的转换
    scenarios = []
    for s in request.scenarios:
        scenario_dict = s.model_dump(by_alias=True)
        # 将 json_body 转为 json
        if 'json_body' in scenario_dict and scenario_dict['json_body'] is not None:
            scenario_dict['json'] = scenario_dict.pop('json_body')
        elif 'json_body' in scenario_dict:
            del scenario_dict['json_body']
        scenarios.append(scenario_dict)
    
    return generator.generate_perf_case(
        name=request.name,
        description=request.description,
        host=request.host,
        scenarios=scenarios,
        users=request.users,
        spawn_rate=request.spawn_rate,
        run_time=request.run_time,
        think_time=request.think_time,
        save_path=request.save_path,
        format=request.format
    )


@router.post("/generate/yaml", summary="从 YAML 创建用例")
async def generate_from_yaml(request: GenerateFromYamlRequest):
    """直接从 YAML 字符串创建测试用例文件"""
    generator = get_case_generator()
    return generator.generate_case_from_yaml(
        yaml_content=request.yaml_content,
        engine_type=request.engine_type,
        save_path=request.save_path
    )


# ============== 用例查询端点 ==============

@router.get("/list/{engine_type}", summary="列出测试用例")
async def list_cases(engine_type: str):
    """列出指定引擎类型的测试用例"""
    generator = get_case_generator()
    
    engine_dirs = {
        "api": "api-cases_yaml",
        "web": "web-cases_yaml",
        "mobile": "mobile-cases_yaml",
        "perf": "perf-cases_yaml"
    }
    
    dir_name = engine_dirs.get(engine_type)
    if not dir_name:
        raise HTTPException(status_code=400, detail=f"不支持的引擎类型: {engine_type}，可选: api/web/mobile/perf")
    
    cases_dir = generator.examples_dir / dir_name
    
    cases = []
    if cases_dir.exists():
        for f in sorted(cases_dir.glob("*.yaml")):
            if f.name == "context.yaml":
                continue
            
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    content = yaml.safe_load(file)
                    desc = content.get("desc", f.stem) if content else f.stem
            except:
                desc = f.stem
            
            cases.append({
                "name": f.name,
                "path": str(f),
                "description": desc
            })
    
    return {
        "engine_type": engine_type,
        "cases_dir": str(cases_dir),
        "count": len(cases),
        "cases": cases
    }


@router.get("/content", summary="获取用例内容")
async def get_case_content(case_path: str):
    """获取用例文件内容"""
    case_file = Path(case_path)
    if not case_file.exists():
        raise HTTPException(status_code=404, detail=f"用例文件不存在: {case_path}")
    
    try:
        with open(case_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        
        with open(case_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        return {
            "path": str(case_file),
            "content": content,
            "raw_yaml": raw_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取用例失败: {str(e)}")


@router.delete("/delete", summary="删除用例")
async def delete_case(case_path: str):
    """删除测试用例文件"""
    case_file = Path(case_path)
    if not case_file.exists():
        raise HTTPException(status_code=404, detail=f"用例文件不存在: {case_path}")
    
    try:
        case_file.unlink()
        return {"success": True, "message": f"用例已删除: {case_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
