import json
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class StreamTestCaseParser:
    """流式测试用例解析器 - 实时解析AI输出的JSON片段"""
    
    def __init__(self):
        self.buffer = ""  # 缓冲区
        self.in_json_block = False
        self.bracket_count = 0
        self.brace_count = 0
        self.extracted_cases = []
    
    def parse_chunk(self, chunk: str) -> Optional[Dict]:
        """
        解析单个chunk，如果检测到完整的测试用例JSON则返回
        
        Args:
            chunk: 新增的文本块
            
        Returns:
            如果完成了一个完整的测试用例，返回该测试用例；否则返回None
        """
        self.buffer += chunk
        
        # 如果还没进入JSON块，查找开始位置
        if not self.in_json_block:
            brace_pos = self.buffer.find('{')
            if brace_pos >= 0:
                self.in_json_block = True
                self.buffer = self.buffer[brace_pos:]  # 移除{之前的内容
                self.brace_count = 1
        
        # 在JSON块中，计算括号
        if self.in_json_block:
            # 计算新增chunk中的括号
            for char in chunk:
                if char == '{':
                    self.brace_count += 1
                elif char == '}':
                    self.brace_count -= 1
            
            # 当括号平衡时，我们有了一个完整的JSON对象
            if self.brace_count == 0:
                return self._extract_and_reset()
        
        return None
    
    def _extract_and_reset(self) -> Optional[Dict]:
        """提取当前buffer中的测试用例并重置状态"""
        try:
            test_case = json.loads(self.buffer)
            
            # 验证必要字段
            if self._validate_test_case(test_case):
                logger.info(f"Successfully extracted test case: {test_case.get('case_name', 'unknown')}")
                self.extracted_cases.append(test_case)
                
                # 重置状态
                self.buffer = ""
                self.in_json_block = False
                self.brace_count = 0
                
                return test_case
            else:
                logger.warning(f"Invalid test case structure: {self.buffer}")
                # 重置以继续查找下一个
                self.buffer = ""
                self.in_json_block = False
                self.brace_count = 0
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            return None
    
    @staticmethod
    def _validate_test_case(test_case: Dict) -> bool:
        """
        验证测试用例的必要字段
        
        Args:
            test_case: 测试用例字典
            
        Returns:
            是否有效
        """
        required_fields = ["case_name", "priority", "test_steps", "expected_result"]
        
        # 检查所有必要字段
        for field in required_fields:
            if field not in test_case:
                return False
        
        # 验证字段类型
        if not isinstance(test_case.get("case_name"), str):
            return False
        
        if not isinstance(test_case.get("test_steps"), (list, str)):
            return False
        
        # 优先级验证
        priority = test_case.get("priority", "").upper()
        if priority not in ["P0", "P1", "P2", "P3"]:
            return False
        
        return True
    
    def flush(self) -> Optional[Dict]:
        """
        刷新缓冲区，返回任何剩余的测试用例
        
        Returns:
            最后的测试用例或None
        """
        if self.buffer and self.in_json_block:
            try:
                # 尝试作为不完整的JSON解析
                test_case = json.loads(self.buffer)
                if self._validate_test_case(test_case):
                    logger.info(f"Flushed test case: {test_case.get('case_name', 'unknown')}")
                    self.extracted_cases.append(test_case)
                    self.buffer = ""
                    self.in_json_block = False
                    self.brace_count = 0
                    return test_case
            except json.JSONDecodeError:
                logger.warning(f"Could not parse remaining buffer: {self.buffer}")
        
        return None
    
    def get_all_cases(self) -> List[Dict]:
        """获取所有提取的测试用例"""
        return self.extracted_cases.copy()
    
    def reset(self):
        """重置解析器状态"""
        self.buffer = ""
        self.in_json_block = False
        self.bracket_count = 0
        self.brace_count = 0
        self.extracted_cases = []


# 全局解析器实例（可选）
_global_parser = StreamTestCaseParser()


def parse_test_cases_from_stream(chunks: List[str]) -> List[Dict]:
    """
    从一列文本块中解析测试用例
    
    Args:
        chunks: 文本块列表
        
    Returns:
        提取到的所有测试用例
    """
    parser = StreamTestCaseParser()
    
    for chunk in chunks:
        parser.parse_chunk(chunk)
    
    # 刷新最后的缓冲区
    parser.flush()
    
    return parser.get_all_cases()
