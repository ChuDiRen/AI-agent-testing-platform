"""
文档分块器
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass

from rag.parsers.document_parser import ParsedDocument
from core.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class TextChunk:
    """文本块"""
    chunk_id: str
    text: str
    chunk_index: int
    page_number: int = None
    metadata: Dict[str, Any] = None


class TextChunker:
    """文本分块器"""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: List[str] = None,
        keep_separator: bool = True
    ):
        """
        初始化文本分块器

        Args:
            chunk_size: 每个块的大小（字符数）
            chunk_overlap: 块之间的重叠字符数
            separators: 分隔符列表，按优先级排序
            keep_separator: 是否保留分隔符
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        self.keep_separator = keep_separator
        logger.info(f"文本分块器初始化: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def chunk_document(self, parsed_doc: ParsedDocument, doc_id: str) -> List[TextChunk]:
        """
        将解析后的文档分块

        Args:
            parsed_doc: 解析后的文档
            doc_id: 文档ID

        Returns:
            文本块列表
        """
        logger.info(f"开始分块文档: {doc_id}, 原文长度: {len(parsed_doc.text)}")

        # 如果文档有页面信息，按页面分块
        if parsed_doc.pages and len(parsed_doc.pages) > 1:
            chunks = self._chunk_by_pages(parsed_doc, doc_id)
        else:
            chunks = self._chunk_by_separator(parsed_doc.text, doc_id, parsed_doc.metadata)

        logger.info(f"文档分块完成: {doc_id}, 生成 {len(chunks)} 个块")
        return chunks

    def _chunk_by_pages(self, parsed_doc: ParsedDocument, doc_id: str) -> List[TextChunk]:
        """按页面分块"""
        chunks = []
        chunk_index = 0

        for page_num, page_text in enumerate(parsed_doc.pages, start=1):
            if not page_text.strip():
                continue

            # 对每一页进行进一步分块
            page_chunks = self._chunk_by_separator(
                page_text,
                doc_id,
                {
                    **parsed_doc.metadata,
                    "page_number": page_num
                }
            )

            # 更新页码
            for chunk in page_chunks:
                chunk.page_number = page_num
                chunk.chunk_index = chunk_index
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _chunk_by_separator(self, text: str, doc_id: str, base_metadata: Dict[str, Any]) -> List[TextChunk]:
        """
        使用分隔符进行分块

        Args:
            text: 要分块的文本
            doc_id: 文档ID
            base_metadata: 基础元数据

        Returns:
            文本块列表
        """
        chunks = []
        chunk_index = 0

        # 清理文本
        text = self._clean_text(text)

        # 递归分块
        split_texts = self._split_text(text, self.separators)

        # 合并过小的块
        chunks = self._merge_small_chunks(split_texts, self.chunk_size)

        # 生成TextChunk对象
        text_chunks = []
        for chunk_text in chunks:
            if not chunk_text.strip():
                continue

            chunk_id = f"{doc_id}_chunk_{chunk_index}"
            metadata = {
                **base_metadata,
                "chunk_id": chunk_id,
                "chunk_size": len(chunk_text),
            }

            text_chunks.append(TextChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                chunk_index=chunk_index,
                metadata=metadata
            ))

            chunk_index += 1

        return text_chunks

    def _split_text(self, text: str, separators: List[str], is_last: bool = False) -> List[str]:
        """
        递归分割文本

        Args:
            text: 要分割的文本
            separators: 分隔符列表
            is_last: 是否是最后一个分隔符

        Returns:
            分割后的文本列表
        """
        if not separators:
            # 没有更多分隔符，按固定大小分割
            return self._split_by_size(text)

        separator = separators[0]

        if separator == "":
            # 最后的备用分隔符，按固定大小分割
            return self._split_by_size(text)

        # 分割文本
        splits = text.split(separator)

        # 如果只有一个部分且不是最后一个分隔符，尝试下一个分隔符
        if len(splits) == 1 and not is_last:
            return self._split_text(text, separators[1:], False)

        # 检查是否所有块都超过目标大小
        all_large = all(len(split) > self.chunk_size for split in splits if split.strip())

        if all_large and not is_last:
            # 如果所有块都太大，使用下一个分隔符
            return self._split_text(text, separators[1:], False)
        elif all_large and is_last:
            # 所有块都太大且是最后一个分隔符，按大小分割
            return self._split_by_size(text)

        # 如果有分隔符，保留或移除
        if self.keep_separator and separator:
            # 保留分隔符（在每个块的末尾）
            splits = [split + separator for split in splits[:-1]] + [splits[-1]]

        return [split.strip() for split in splits if split.strip()]

    def _split_by_size(self, text: str) -> List[str]:
        """
        按固定大小分割文本

        Args:
            text: 要分割的文本

        Returns:
            分割后的文本列表
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 如果不是最后一块，尝试在最近的分隔符处断开
            if end < len(text):
                # 查找最近的分隔符
                for sep in ["。", "！", "？", ".", "!", "?", "\n", " ", ","]:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep != -1:
                        end = last_sep + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # 处理重叠
            if end < len(text):
                start = max(end - self.chunk_overlap, start + len(chunk))
            else:
                break

        return chunks

    def _merge_small_chunks(self, chunks: List[str], target_size: int) -> List[str]:
        """
        合并过小的块

        Args:
            chunks: 原始块列表
            target_size: 目标大小

        Returns:
            合并后的块列表
        """
        if not chunks:
            return []

        merged = []
        current_chunk = chunks[0]

        for next_chunk in chunks[1:]:
            # 如果当前块太小，与下一个块合并
            if len(current_chunk) < target_size * 0.5:
                current_chunk += "\n" + next_chunk
            else:
                merged.append(current_chunk)
                current_chunk = next_chunk

        # 添加最后一个块
        if current_chunk:
            merged.append(current_chunk)

        return merged

    def _clean_text(self, text: str) -> str:
        """
        清理文本

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除控制字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        # 移除多余的换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
