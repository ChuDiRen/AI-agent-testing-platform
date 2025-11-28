"""批量处理器 - 并行处理多个接口的测试用例生成

核心优化策略:
1. 并行处理: 同时处理多个接口，大幅提升速度
2. 批次控制: 避免同时请求过多导致API限流
3. 进度追踪: 实时显示处理进度
4. 错误恢复: 单个接口失败不影响其他接口
5. 结果合并: 自动合并所有接口的测试用例
"""
import asyncio
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from .models import TestCaseState


@dataclass
class BatchConfig:
    """批量处理配置"""
    # 并发控制
    max_concurrent: int = 5  # 最大并发数 (建议3-10)
    batch_size: int = 10     # 每批处理数量
    
    # 超时控制
    per_api_timeout: float = 180.0  # 单个接口超时时间(秒)
    total_timeout: float = 3600.0   # 总超时时间(秒)
    
    # 重试控制
    max_retries: int = 2     # 失败重试次数
    retry_delay: float = 5.0 # 重试间隔(秒)
    
    # 简化模式 (跳过评审，加快速度)
    skip_review: bool = False
    max_iterations: int = 1


@dataclass
class BatchResult:
    """批量处理结果"""
    total: int = 0           # 总接口数
    success: int = 0         # 成功数
    failed: int = 0          # 失败数
    skipped: int = 0         # 跳过数
    
    results: List[TestCaseState] = field(default_factory=list)  # 成功的结果
    errors: List[Dict[str, Any]] = field(default_factory=list)  # 错误信息
    
    start_time: float = 0.0
    end_time: float = 0.0
    
    @property
    def duration(self) -> float:
        """总耗时(秒)"""
        return self.end_time - self.start_time
    
    @property
    def avg_time_per_api(self) -> float:
        """平均每个接口耗时(秒)"""
        if self.success == 0:
            return 0.0
        return self.duration / self.success


class BatchProcessor:
    """批量处理器 - 并行处理多个接口"""
    
    def __init__(
        self,
        generator,  # TestCaseGeneratorV3 实例
        config: Optional[BatchConfig] = None,
    ):
        self.generator = generator
        self.config = config or BatchConfig()
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """设置进度回调函数
        
        Args:
            callback: 回调函数，参数为 (当前进度, 总数, 状态信息)
        """
        self._progress_callback = callback
    
    def _report_progress(self, current: int, total: int, status: str):
        """报告进度"""
        if self._progress_callback:
            self._progress_callback(current, total, status)
        else:
            percent = (current / total * 100) if total > 0 else 0
            print(f"  [{current}/{total}] ({percent:.1f}%) {status}")
    
    async def _process_single_api(
        self,
        api_info: Dict[str, Any],
        index: int,
        total: int,
    ) -> Optional[TestCaseState]:
        """处理单个接口
        
        Args:
            api_info: 接口信息 (包含 requirement, name 等)
            index: 当前索引
            total: 总数
            
        Returns:
            成功返回 TestCaseState，失败返回 None
        """
        async with self._semaphore:
            api_name = api_info.get("name", f"API-{index+1}")
            requirement = api_info.get("requirement", "")
            test_type = api_info.get("test_type", "API")
            
            self._report_progress(index + 1, total, f"处理中: {api_name}")
            
            for retry in range(self.config.max_retries + 1):
                try:
                    result = await asyncio.wait_for(
                        self.generator.generate(
                            requirement=requirement,
                            test_type=test_type,
                            max_iterations=self.config.max_iterations,
                        ),
                        timeout=self.config.per_api_timeout,
                    )
                    
                    self._report_progress(index + 1, total, f"✅ 完成: {api_name}")
                    return result
                    
                except asyncio.TimeoutError:
                    if retry < self.config.max_retries:
                        self._report_progress(
                            index + 1, total, 
                            f"⏱️ 超时，重试 {retry + 1}/{self.config.max_retries}: {api_name}"
                        )
                        await asyncio.sleep(self.config.retry_delay)
                    else:
                        self._report_progress(index + 1, total, f"❌ 超时失败: {api_name}")
                        return None
                        
                except Exception as e:
                    if retry < self.config.max_retries:
                        self._report_progress(
                            index + 1, total,
                            f"⚠️ 错误，重试 {retry + 1}/{self.config.max_retries}: {api_name} - {e}"
                        )
                        await asyncio.sleep(self.config.retry_delay)
                    else:
                        self._report_progress(index + 1, total, f"❌ 失败: {api_name} - {e}")
                        return None
            
            return None
    
    async def process_batch(
        self,
        api_list: List[Dict[str, Any]],
    ) -> BatchResult:
        """批量处理接口列表
        
        Args:
            api_list: 接口信息列表，每个元素包含:
                - requirement: 需求描述
                - name: 接口名称 (可选)
                - test_type: 测试类型 (可选，默认API)
                
        Returns:
            BatchResult 批量处理结果
        """
        result = BatchResult(
            total=len(api_list),
            start_time=time.time(),
        )
        
        if not api_list:
            result.end_time = time.time()
            return result
        
        print(f"\n🚀 开始批量处理 {len(api_list)} 个接口")
        print(f"   并发数: {self.config.max_concurrent}")
        print(f"   单接口超时: {self.config.per_api_timeout}秒")
        print(f"   最大迭代: {self.config.max_iterations}次\n")
        
        # 创建信号量控制并发
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        # 创建所有任务
        tasks = [
            self._process_single_api(api_info, i, len(api_list))
            for i, api_info in enumerate(api_list)
        ]
        
        # 并行执行所有任务
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.total_timeout,
            )
        except asyncio.TimeoutError:
            print(f"\n⚠️ 总超时 ({self.config.total_timeout}秒)，部分任务未完成")
            results = []
        
        # 统计结果
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                result.failed += 1
                result.errors.append({
                    "index": i,
                    "api": api_list[i].get("name", f"API-{i+1}"),
                    "error": str(res),
                })
            elif res is None:
                result.failed += 1
            else:
                result.success += 1
                result.results.append(res)
        
        result.end_time = time.time()
        
        # 打印统计
        print(f"\n📊 批量处理完成:")
        print(f"   总数: {result.total}")
        print(f"   成功: {result.success} ✅")
        print(f"   失败: {result.failed} ❌")
        print(f"   总耗时: {result.duration:.1f}秒")
        print(f"   平均每个: {result.avg_time_per_api:.1f}秒")
        
        return result
    
    async def process_swagger(
        self,
        swagger_url: str,
        max_apis: Optional[int] = None,
        filter_tags: Optional[List[str]] = None,
    ) -> BatchResult:
        """从 Swagger 文档批量生成测试用例
        
        Args:
            swagger_url: Swagger JSON URL
            max_apis: 最大处理接口数 (None表示全部)
            filter_tags: 只处理指定标签的接口
            
        Returns:
            BatchResult 批量处理结果
        """
        from .tools.requirement_tools import parse_swagger_doc
        
        print(f"\n📥 正在解析 Swagger 文档: {swagger_url}")
        
        # 解析 Swagger
        endpoints = parse_swagger_doc(swagger_url)
        
        if not endpoints:
            print("❌ 未找到任何接口")
            return BatchResult()
        
        print(f"   发现 {len(endpoints)} 个接口")
        
        # 过滤标签
        if filter_tags:
            endpoints = [
                ep for ep in endpoints 
                if any(tag in ep.tags for tag in filter_tags)
            ]
            print(f"   过滤后: {len(endpoints)} 个接口")
        
        # 限制数量
        if max_apis and len(endpoints) > max_apis:
            endpoints = endpoints[:max_apis]
            print(f"   限制为: {len(endpoints)} 个接口")
        
        # 转换为 api_list 格式
        api_list = [
            {
                "name": f"{ep.method} {ep.path}",
                "requirement": ep.to_requirement(),
                "test_type": "API",
            }
            for ep in endpoints
        ]
        
        return await self.process_batch(api_list)


# ============== 便捷函数 ==============

async def batch_generate(
    api_list: List[Dict[str, Any]],
    max_concurrent: int = 5,
    max_iterations: int = 1,
) -> BatchResult:
    """批量生成测试用例的便捷函数
    
    Args:
        api_list: 接口信息列表
        max_concurrent: 最大并发数
        max_iterations: 最大迭代次数
        
    Returns:
        BatchResult
    """
    from . import generator
    
    config = BatchConfig(
        max_concurrent=max_concurrent,
        max_iterations=max_iterations,
    )
    
    processor = BatchProcessor(generator, config)
    return await processor.process_batch(api_list)


async def batch_generate_from_swagger(
    swagger_url: str,
    max_apis: Optional[int] = None,
    max_concurrent: int = 5,
    max_iterations: int = 1,
) -> BatchResult:
    """从 Swagger 批量生成测试用例的便捷函数
    
    Args:
        swagger_url: Swagger JSON URL
        max_apis: 最大处理接口数
        max_concurrent: 最大并发数
        max_iterations: 最大迭代次数
        
    Returns:
        BatchResult
    """
    from . import generator
    
    config = BatchConfig(
        max_concurrent=max_concurrent,
        max_iterations=max_iterations,
    )
    
    processor = BatchProcessor(generator, config)
    return await processor.process_swagger(swagger_url, max_apis)
