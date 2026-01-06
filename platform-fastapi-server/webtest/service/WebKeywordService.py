"""
Web关键字Service层
"""
import json
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any

from core.logger import get_logger
from sqlmodel import Session, select, func

from ..model.WebKeywordModel import WebKeyword
from ..schemas.WebKeywordSchema import (
    WebKeywordCreate, WebKeywordUpdate, WebKeywordQuery,
    WebKeywordGenerateRequest, WebKeywordGenerateResponse, WebKeywordImport,
    WebKeywordExport, WebKeywordTestRequest, WebKeywordTestResponse
)

logger = get_logger(__name__)


class WebKeywordService:
    """Web关键字服务类"""
    
    @staticmethod
    def create_keyword(session: Session, keyword_data: WebKeywordCreate) -> WebKeyword:
        """创建Web关键字"""
        try:
            # 转换参数定义
            params_json = json.dumps([param.dict() for param in keyword_data.params], ensure_ascii=False)
            
            keyword = WebKeyword(
                name=keyword_data.name,
                display_name=keyword_data.display_name,
                description=keyword_data.description,
                category=keyword_data.category,
                params=params_json,
                return_type=keyword_data.return_type,
                code_template=keyword_data.code_template,
                python_code=keyword_data.python_code,
                is_builtin=keyword_data.is_builtin,
                author=keyword_data.author,
                version=keyword_data.version
            )
            
            session.add(keyword)
            session.commit()
            session.refresh(keyword)
            logger.info(f"创建Web关键字成功，ID: {keyword.id}, 名称: {keyword.name}")
            return keyword
        except Exception as e:
            session.rollback()
            logger.error(f"创建Web关键字失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update_keyword(session: Session, keyword_id: int, keyword_data: WebKeywordUpdate) -> Optional[WebKeyword]:
        """更新Web关键字"""
        try:
            keyword = session.get(WebKeyword, keyword_id)
            if not keyword:
                return None
            
            # 更新字段
            update_data = keyword_data.dict(exclude_unset=True)
            
            # 处理参数更新
            if 'params' in update_data:
                params_json = json.dumps([param.dict() for param in update_data['params']], ensure_ascii=False)
                update_data['params'] = params_json
            
            for field, value in update_data.items():
                setattr(keyword, field, value)
            
            keyword.update_time = datetime.now()
            session.commit()
            session.refresh(keyword)
            logger.info(f"更新Web关键字成功，ID: {keyword.id}")
            return keyword
        except Exception as e:
            session.rollback()
            logger.error(f"更新Web关键字失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete_keyword(session: Session, keyword_id: int) -> bool:
        """删除Web关键字"""
        try:
            keyword = session.get(WebKeyword, keyword_id)
            if not keyword:
                return False
            
            # 检查是否为内置关键字
            if keyword.is_builtin:
                raise ValueError("不能删除内置关键字")
            
            session.delete(keyword)
            session.commit()
            logger.info(f"删除Web关键字成功，ID: {keyword_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web关键字失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete_keywords(session: Session, keyword_ids: List[int]) -> int:
        """批量删除Web关键字"""
        try:
            count = 0
            for keyword_id in keyword_ids:
                if WebKeywordService.delete_keyword(session, keyword_id):
                    count += 1
            logger.info(f"批量删除Web关键字成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web关键字失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_keyword_by_id(session: Session, keyword_id: int) -> Optional[WebKeyword]:
        """根据ID获取Web关键字"""
        try:
            return session.get(WebKeyword, keyword_id)
        except Exception as e:
            logger.error(f"查询Web关键字失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def query_keywords_by_page(session: Session, query: WebKeywordQuery) -> Tuple[List[WebKeyword], int]:
        """分页查询Web关键字"""
        try:
            # 构建查询条件
            statement = select(WebKeyword)
            
            # 添加过滤条件
            if query.name:
                statement = statement.where(WebKeyword.name.contains(query.name))
            if query.category:
                statement = statement.where(WebKeyword.category == query.category)
            if query.is_builtin is not None:
                statement = statement.where(WebKeyword.is_builtin == query.is_builtin)
            if query.is_active is not None:
                statement = statement.where(WebKeyword.is_active == query.is_active)
            if query.author:
                statement = statement.where(WebKeyword.author.contains(query.author))
            
            # 计算总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()
            
            # 分页查询
            statement = statement.offset((query.page - 1) * query.pageSize).limit(query.pageSize)
            statement = statement.order_by(WebKeyword.category, WebKeyword.name)
            keywords = session.exec(statement).all()
            
            return list(keywords), total
        except Exception as e:
            logger.error(f"分页查询Web关键字失败: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def generate_keyword_file(session: Session, request: WebKeywordGenerateRequest) -> WebKeywordGenerateResponse:
        """生成关键字文件"""
        try:
            # 查询关键字
            keyword_ids = request.keyword_ids
            keywords = []
            
            for keyword_id in keyword_ids:
                keyword = session.get(WebKeyword, keyword_id)
                if keyword:
                    keywords.append(keyword)
            
            # 生成文件内容
            file_content = WebKeywordService._generate_file_content(keywords, request.file_format, request.include_builtin)
            
            # 计算文件大小
            file_size = len(file_content.encode('utf-8'))
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"web_keywords_{timestamp}.{request.file_format}"
            
            return WebKeywordGenerateResponse(
                file_name=file_name,
                file_content=file_content,
                file_size=file_size,
                generate_time=datetime.now()
            )
        except Exception as e:
            logger.error(f"生成关键字文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _generate_file_content(keywords: List[WebKeyword], file_format: str, include_builtin: bool) -> str:
        """生成文件内容"""
        try:
            if file_format == 'python':
                return WebKeywordService._generate_python_file(keywords, include_builtin)
            elif file_format == 'java':
                return WebKeywordService._generate_java_file(keywords, include_builtin)
            elif file_format == 'javascript':
                return WebKeywordService._generate_javascript_file(keywords, include_builtin)
            else:
                raise ValueError(f"不支持的文件格式: {file_format}")
        except Exception as e:
            logger.error(f"生成文件内容失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _generate_python_file(keywords: List[WebKeyword], include_builtin: bool) -> str:
        """生成Python文件"""
        content = [
            '"""',
            'Web测试关键字文件',
            f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '关键字数量: ' + str(len(keywords)),
            '"""',
            '',
            'from selenium import webdriver',
            'from selenium.webdriver.common.by import By',
            'from selenium.webdriver.support.ui import WebDriverWait',
            'from selenium.webdriver.support import expected_conditions as EC',
            'import time',
            '',
            'class WebKeywords:',
            '    """Web测试关键字类"""',
            '',
            '    def __init__(self, driver):',
            '        self.driver = driver',
            '        self.wait = WebDriverWait(driver, 10)',
            '',
        ]
        
        for keyword in keywords:
            if not include_builtin and keyword.is_builtin:
                continue
            
            # 解析参数
            params = []
            if keyword.params:
                try:
                    params_data = json.loads(keyword.params)
                    params = [f"{param['name']}: {param['type']}" for param in params_data]
                except json.JSONDecodeError:
                    pass
            
            # 生成方法
            method_signature = f"    def {keyword.name}(self{', ' + ', '.join(params) if params else ''}):"
            content.extend([
                method_signature,
                f'        """{keyword.description or keyword.display_name}"""',
                f'        {keyword.python_code or keyword.code_template}',
                '',
            ])
        
        content.extend([
            '',
            '# 使用示例',
            '# driver = webdriver.Chrome()',
            '# keywords = WebKeywords(driver)',
            '# keywords.click_element("id", "submit-btn")',
            ''
        ])
        
        return '\n'.join(content)
    
    @staticmethod
    def _generate_java_file(keywords: List[WebKeyword], include_builtin: bool) -> str:
        """生成Java文件"""
        content = [
            'package webtest.keywords;',
            '',
            'import org.openqa.selenium.WebDriver;',
            'import org.openqa.selenium.By;',
            'import org.openqa.selenium.support.ui.WebDriverWait;',
            'import org.openqa.selenium.support.ui.ExpectedConditions;',
            'import org.openqa.selenium.WebElement;',
            'import java.time.Duration;',
            '',
            '/**',
            ' * Web测试关键字类',
            f' * 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f' * 关键字数量: {len(keywords)}',
            ' */',
            'public class WebKeywords {',
            '    ',
            '    private WebDriver driver;',
            '    private WebDriverWait wait;',
            '    ',
            '    public WebKeywords(WebDriver driver) {',
            '        this.driver = driver;',
            '        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));',
            '    }',
            '    ',
        ]
        
        for keyword in keywords:
            if not include_builtin and keyword.is_builtin:
                continue
            
            # 解析参数
            params = []
            param_declarations = []
            if keyword.params:
                try:
                    params_data = json.loads(keyword.params)
                    for param in params_data:
                        java_type = WebKeywordService._convert_to_java_type(param.get('type', 'String'))
                        params.append(f"{param['name']}")
                        param_declarations.append(f"{java_type} {param['name']}")
                except json.JSONDecodeError:
                    pass
            
            # 生成方法
            param_str = ", ".join(param_declarations)
            return_type = WebKeywordService._convert_to_java_type(keyword.return_type or 'void')
            
            content.extend([
                f'    /**',
                f'     * {keyword.description or keyword.display_name}',
                f'     */',
                f'    public {return_type} {keyword.name}({param_str}) {{',
                f'        // TODO: 实现关键字逻辑',
                f'        {keyword.java_code or "// " + (keyword.description or keyword.display_name)}',
                f'    }}',
                f'    ',
            ])
        
        content.extend([
            '}',
            '',
            '// 使用示例',
            '// WebDriver driver = new ChromeDriver();',
            '// WebKeywords keywords = new WebKeywords(driver);',
            '// keywords.clickElement("id", "submit-btn");',
            ''
        ])
        
        return '\n'.join(content)
    
    @staticmethod
    def _generate_javascript_file(keywords: List[WebKeyword], include_builtin: bool) -> str:
        """生成JavaScript文件"""
        content = [
            '/**',
            ' * Web测试关键字模块',
            f' * 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f' * 关键字数量: {len(keywords)}',
            ' */',
            '',
            'class WebKeywords {',
            '    ',
            '    /**',
            '     * 构造函数',
            '     * @param {object} driver - WebDriver instance',
            '     */
            '    constructor(driver) {',
            '        this.driver = driver;',
            '        this.wait = new driver.wait(10000); // 10秒等待',
            '    }',
            '    ',
        ]
        
        for keyword in keywords:
            if not include_builtin and keyword.is_builtin:
                continue
            
            # 解析参数
            params = []
            if keyword.params:
                try:
                    params_data = json.loads(keyword.params)
                    params = [param['name'] for param in params_data]
                except json.JSONDecodeError:
                    pass
            
            # 生成方法
            param_str = ", ".join(params)
            
            content.extend([
                f'    /**',
                f'     * {keyword.description or keyword.display_name}',
                f'     */',
                f'    async {keyword.name}({param_str}) {{',
                f'        // TODO: 实现关键字逻辑',
                f'        {keyword.javascript_code or "// " + (keyword.description or keyword.display_name)}',
                f'    }}',
                f'    ',
            ])
        
        content.extend([
            '}',
            '',
            '// 使用示例',
            '// const { Builder } = require("selenium-webdriver");',
            '// const driver = await new Builder().forBrowser("chrome").build();',
            '// const keywords = new WebKeywords(driver);',
            '// await keywords.clickElement("id", "submit-btn");',
            '',
            'module.exports = WebKeywords;',
            ''
        ])
        
        return '\n'.join(content)
    
    @staticmethod
    def _convert_to_java_type(python_type: str) -> str:
        """将Python类型转换为Java类型"""
        type_mapping = {
            'str': 'String',
            'string': 'String',
            'int': 'int',
            'integer': 'int',
            'float': 'double',
            'double': 'double',
            'bool': 'boolean',
            'boolean': 'boolean',
            'list': 'List<String>',
            'dict': 'Map<String, Object>',
            'void': 'void'
        }
        return type_mapping.get(python_type.lower(), 'String')
    
    @staticmethod
    def import_keywords(session: Session, keywords: List[WebKeywordCreate], overwrite: bool = False) -> Tuple[int, int]:
        """导入Web关键字"""
        try:
            success_count = 0
            error_count = 0
            
            for keyword_data in keywords:
                try:
                    # 检查是否已存在同名关键字
                    existing_statement = select(WebKeyword).where(WebKeyword.name == keyword_data.name)
                    existing = session.exec(existing_statement).first()
                    
                    if existing:
                        if overwrite:
                            # 更新现有关键字
                            update_data = keyword_data.dict()
                            for field, value in update_data.items():
                                setattr(existing, field, value)
                            existing.update_time = datetime.now()
                            success_count += 1
                        else:
                            # 跳过已存在的关键字
                            continue
                    else:
                        # 创建新关键字
                        keyword = WebKeyword(**keyword_data.dict())
                        session.add(keyword)
                        success_count += 1
                    
                except Exception as e:
                    logger.error(f"导入关键字失败: {keyword_data.name}, 错误: {e}")
                    error_count += 1
                    continue
            
            session.commit()
            logger.info(f"导入Web关键字完成，成功: {success_count}, 失败: {error_count}")
            return success_count, error_count
        except Exception as e:
            session.rollback()
            logger.error(f"批量导入Web关键字失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def export_keywords(session: Session, export_request: WebKeywordExport) -> List[WebKeyword]:
        """导出Web关键字"""
        try:
            statement = select(WebKeyword)
            
            if export_request.ids:
                statement = statement.where(WebKeyword.id.in_(export_request.ids))
            
            if not export_request.include_code:
                # 不包含代码的字段
                statement = statement.with_entities(
                    WebKeyword.id, WebKeyword.name, WebKeyword.display_name,
                    WebKeyword.description, WebKeyword.category, WebKeyword.params,
                    WebKeyword.return_type, WebKeyword.is_builtin, WebKeyword.author,
                    WebKeyword.version
                )
            
            keywords = session.exec(statement).all()
            return list(keywords)
        except Exception as e:
            logger.error(f"导出Web关键字失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def test_keyword(session: Session, request: WebKeywordTestRequest) -> WebKeywordTestResponse:
        """测试关键字"""
        try:
            keyword = session.get(WebKeyword, keyword_id=request.keyword_id)
            if not keyword:
                return WebKeywordTestResponse(
                    keyword_id=request.keyword_id,
                    test_result='error',
                    execution_time=0.0,
                    error_message='关键字不存在'
                )
            
            # TODO: 实际执行关键字测试
            # 1. 初始化浏览器
            # 2. 执行关键字代码
            # 3. 捕获执行结果
            # 4. 清理资源
            
            # 模拟测试结果
            return WebKeywordTestResponse(
                keyword_id=request.keyword_id,
                test_result='passed',
                execution_time=1.5,
                return_value='success',
                screenshot_path=None
            )
        except Exception as e:
            logger.error(f"测试关键字失败: {e}", exc_info=True)
            return WebKeywordTestResponse(
                keyword_id=request.keyword_id,
                test_result='error',
                execution_time=0.0,
                error_message=str(e)
            )
    
    @staticmethod
    def get_keyword_categories(session: Session) -> List[str]:
        """获取关键字分类"""
        try:
            statement = select(WebKeyword.category).distinct()
            categories = session.exec(statement).all()
            return list(categories)
        except Exception as e:
            logger.error(f"获取关键字分类失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_builtin_keywords(session: Session) -> List[WebKeyword]:
        """获取内置关键字"""
        try:
            statement = select(WebKeyword).where(WebKeyword.is_builtin == True).order_by(WebKeyword.name)
            keywords = session.exec(statement).all()
            return list(keywords)
        except Exception as e:
            logger.error(f"获取内置关键字失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def validate_keyword_code(session: Session, keyword_id: int, code: str) -> Dict[str, Any]:
        """验证关键字代码"""
        try:
            # TODO: 实现代码验证
            # 1. 语法检查
            # 2. 安全检查
            # 3. 依赖检查
            
            return {
                "keyword_id": keyword_id,
                "validation_result": 'valid',
                "error_message": None,
                "execution_time": 0.1
            }
        except Exception as e:
            logger.error(f"验证关键字代码失败: {e}", exc_info=True)
            return {
                "keyword_id": keyword_id,
                "validation_result": 'error',
                "error_message": str(e),
                "execution_time": 0.0
            }
    
    @staticmethod
    def get_keyword_usage_stats(session: Session, keyword_id: int) -> Dict[str, Any]:
        """获取关键字使用统计"""
        try:
            keyword = session.get(WebKeyword, keyword_id)
            if not keyword:
                return {}
            
            # TODO: 统计关键字在用例中的使用情况
            # 这里返回模拟数据
            return {
                "keyword_id": keyword_id,
                "keyword_name": keyword.name,
                "usage_count": keyword.usage_count,
                "last_used": None,
                "used_in_cases": [],
                "popular_projects": []
            }
        except Exception as e:
            logger.error(f"获取关键字使用统计失败: {e}", exc_info=True)
            return {}
