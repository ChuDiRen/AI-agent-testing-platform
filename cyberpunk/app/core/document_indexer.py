"""
Document Indexing Service

Automatically indexes uploaded documents into RAG knowledge base.
Supports multiple formats: OpenAPI, Swagger, GraphQL, PDF, JSON, YAML.
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
import logging
import hashlib
from datetime import datetime
import aiofiles
import asyncio

from api_agent.models import DocumentDB
from api_agent.db import get_session
from sqlmodel import select

logger = logging.getLogger(__name__)


class DocumentType(str):
    """Supported document types"""
    OPENAPI = "openapi"
    SWAGGER = "swagger"
    GRAPHQL = "graphql"
    POSTMAN = "postman"
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"


class DocumentParser:
    """Parse documents in various formats"""

    @staticmethod
    async def parse(file_path: str) -> Dict[str, Any]:
        """
        Parse document and extract content

        Args:
            file_path: Path to document file

        Returns:
            Parsed document content with metadata

        Raises:
            ValueError: If document type is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        logger.info(f"Parsing document: {file_path} (type: {extension})")

        try:
            if extension == '.json':
                return await DocumentParser._parse_json(file_path)
            elif extension in ['.yaml', '.yml']:
                return await DocumentParser._parse_yaml(file_path)
            elif extension == '.graphql' or extension == '.gql':
                return await DocumentParser._parse_graphql(file_path)
            elif extension == '.pdf':
                return await DocumentParser._parse_pdf(file_path)
            elif extension in ['.md', '.markdown']:
                return await DocumentParser._parse_markdown(file_path)
            else:
                # Try to auto-detect
                content = await aiofiles.open(file_path, 'r', encoding='utf-8').read()
                try:
                    return await DocumentParser._parse_json_content(content, file_path)
                except:
                    try:
                        return await DocumentParser._parse_yaml_content(content, file_path)
                    except:
                        return await DocumentParser._parse_text(content, file_path)

        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {e}")
            raise ValueError(f"Document parsing failed: {str(e)}")

    @staticmethod
    async def _parse_json(file_path: str) -> Dict[str, Any]:
        """Parse JSON document"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)

            # Detect document type
            doc_type = DocumentType.JSON
            if 'openapi' in data:
                doc_type = DocumentType.OPENAPI
            elif 'swagger' in data:
                doc_type = DocumentType.SWAGGER
            elif 'info' in data and 'item' in data:
                doc_type = DocumentType.POSTMAN

            return {
                "type": doc_type,
                "content": content,
                "data": data,
                "metadata": {
                    "file_path": file_path,
                    "file_size": Path(file_path).stat().st_size,
                    "parsed_at": datetime.utcnow().isoformat()
                }
            }

    @staticmethod
    async def _parse_yaml(file_path: str) -> Dict[str, Any]:
        """Parse YAML document"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = yaml.safe_load(content)

            # Detect document type
            doc_type = DocumentType.YAML
            if data and 'openapi' in data:
                doc_type = DocumentType.OPENAPI
            elif data and 'swagger' in data:
                doc_type = DocumentType.SWAGGER

            return {
                "type": doc_type,
                "content": content,
                "data": data,
                "metadata": {
                    "file_path": file_path,
                    "file_size": Path(file_path).stat().st_size,
                    "parsed_at": datetime.utcnow().isoformat()
                }
            }

    @staticmethod
    async def _parse_graphql(file_path: str) -> Dict[str, Any]:
        """Parse GraphQL schema"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()

        return {
            "type": DocumentType.GRAPHQL,
            "content": content,
            "data": {"schema": content},
            "metadata": {
                "file_path": file_path,
                "file_size": Path(file_path).stat().st_size,
                "parsed_at": datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    async def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF document (requires PyPDF2)"""
        try:
            import PyPDF2
        except ImportError:
            logger.warning("PyPDF2 not installed, treating PDF as text")
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            return {
                "type": DocumentType.PDF,
                "content": content,
                "data": {},
                "metadata": {
                    "file_path": file_path,
                    "file_size": Path(file_path).stat().st_size,
                    "parsed_at": datetime.utcnow().isoformat()
                }
            }

        content = ""
        reader = PyPDF2.PdfReader(file_path)
        for page in reader.pages:
            content += page.extract_text()

        return {
            "type": DocumentType.PDF,
            "content": content,
            "data": {},
            "metadata": {
                "file_path": file_path,
                "pages": len(reader.pages),
                "file_size": Path(file_path).stat().st_size,
                "parsed_at": datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    async def _parse_markdown(file_path: str) -> Dict[str, Any]:
        """Parse Markdown document"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()

        # Extract title from first heading
        title = Path(file_path).name
        for line in content.split('\n')[:20]:
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                break

        return {
            "type": DocumentType.MARKDOWN,
            "content": content,
            "data": {"title": title},
            "metadata": {
                "file_path": file_path,
                "title": title,
                "file_size": Path(file_path).stat().st_size,
                "parsed_at": datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    async def _parse_json_content(content: str, file_path: str) -> Dict[str, Any]:
        """Helper to parse JSON content string"""
        data = json.loads(content)
        return await DocumentParser._parse_json_data(data, file_path, content)

    @staticmethod
    async def _parse_json_data(data: Dict, file_path: str, content: str) -> Dict[str, Any]:
        """Helper to parse JSON data"""
        doc_type = DocumentType.JSON
        if 'openapi' in data:
            doc_type = DocumentType.OPENAPI
        elif 'swagger' in data:
            doc_type = DocumentType.SWAGGER

        return {
            "type": doc_type,
            "content": content,
            "data": data,
            "metadata": {
                "file_path": file_path,
                "file_size": len(content),
                "parsed_at": datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    async def _parse_yaml_content(content: str, file_path: str) -> Dict[str, Any]:
        """Helper to parse YAML content string"""
        data = yaml.safe_load(content)
        return await DocumentParser._parse_yaml_data(data, file_path, content)

    @staticmethod
    async def _parse_yaml_data(data: Any, file_path: str, content: str) -> Dict[str, Any]:
        """Helper to parse YAML data"""
        doc_type = DocumentType.YAML
        if data and 'openapi' in data:
            doc_type = DocumentType.OPENAPI
        elif data and 'swagger' in data:
            doc_type = DocumentType.SWAGGER

        return {
            "type": doc_type,
            "content": content,
            "data": data,
            "metadata": {
                "file_path": file_path,
                "file_size": len(content),
                "parsed_at": datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    async def _parse_text(content: str, file_path: str) -> Dict[str, Any]:
        """Helper to parse plain text"""
        return {
            "type": "markdown",
            "content": content,
            "data": {},
            "metadata": {
                "file_path": file_path,
                "file_size": len(content),
                "parsed_at": datetime.utcnow().isoformat()
            }
        }


class DocumentIndexer:
    """
    Document Indexer

    Automatically indexes uploaded documents into RAG knowledge base.
    """

    def __init__(self, mcp_client: Any = None):
        """
        Initialize document indexer

        Args:
            mcp_client: Optional MCP client for RAG operations
        """
        self.mcp_client = mcp_client
        self.parser = DocumentParser()

    async def index_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse and index a document

        Args:
            file_path: Path to document file

        Returns:
            Indexing result with document ID and status
        """
        logger.info(f"Indexing document: {file_path}")

        try:
            # Parse document
            parsed = await self.parser.parse(file_path)

            # Generate document ID
            doc_id = self._generate_doc_id(file_path)

            # Store in database
            await self._store_document(doc_id, parsed)

            # Index in RAG
            if self.mcp_client:
                await self._index_in_rag(doc_id, parsed)
            else:
                logger.warning("No MCP client available, skipping RAG indexing")

            return {
                "status": "success",
                "doc_id": doc_id,
                "type": parsed["type"],
                "indexed": True,
                "message": f"Successfully indexed {file_path}"
            }

        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            return {
                "status": "error",
                "doc_id": None,
                "indexed": False,
                "message": f"Failed to index: {str(e)}"
            }

    async def index_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Parse and index multiple documents

        Args:
            file_paths: List of document file paths

        Returns:
            List of indexing results
        """
        logger.info(f"Indexing {len(file_paths)} documents")

        results = []
        for file_path in file_paths:
            result = await self.index_document(file_path)
            results.append(result)

        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"Indexing complete: {success_count}/{len(file_paths)} documents indexed")

        return results

    async def _store_document(self, doc_id: str, parsed: Dict[str, Any]):
        """
        Store document in database

        Args:
            doc_id: Document ID
            parsed: Parsed document data
        """
        async with get_session() as session:
            # Check if document already exists
            existing = await session.execute(
                select(DocumentDB).where(DocumentDB.doc_id == doc_id)
            )
            if existing.first():
                # Update existing document
                existing_doc = existing.first()
                existing_doc.updated_at = datetime.utcnow()
                existing_doc.indexed = True
                existing_doc.meta_data = parsed["metadata"]
                session.add(existing_doc)
            else:
                # Create new document
                doc = DocumentDB(
                    doc_id=doc_id,
                    name=Path(parsed["metadata"]["file_path"]).name,
                    type=parsed["type"],
                    file_path=parsed["metadata"]["file_path"],
                    indexed=True,
                    meta_data=parsed["metadata"]
                )
                session.add(doc)

            await session.commit()
            logger.debug(f"Stored document {doc_id} in database")

    async def _index_in_rag(self, doc_id: str, parsed: Dict[str, Any]):
        """
        Index document in RAG knowledge base

        Args:
            doc_id: Document ID
            parsed: Parsed document data
        """
        try:
            # Call RAG MCP Server
            result = await self.mcp_client.call_tool(
                "rag-server",
                "rag_add_documents",
                {
                    "documents": [
                        {
                            "content": parsed["content"],
                            "metadata": {
                                "doc_id": doc_id,
                                "doc_type": parsed["type"],
                                **parsed["metadata"]
                            }
                        }
                    ]
                }
            )

            logger.info(f"Document {doc_id} indexed in RAG")
            return result

        except Exception as e:
            logger.error(f"Failed to index document {doc_id} in RAG: {e}")
            # Don't fail - document is still stored in database

    @staticmethod
    def _generate_doc_id(file_path: str) -> str:
        """Generate unique document ID"""
        content_hash = hashlib.sha256(file_path.encode()).hexdigest()[:16]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"doc_{content_hash}_{timestamp}"

    async def get_document(self, doc_id: str) -> Optional[DocumentDB]:
        """
        Get document by ID

        Args:
            doc_id: Document ID

        Returns:
            DocumentDB model or None
        """
        async with get_session() as session:
            result = await session.execute(
                select(DocumentDB).where(DocumentDB.doc_id == doc_id)
            )
            return result.first()

    async def list_documents(
        self,
        doc_type: Optional[str] = None,
        limit: int = 100
    ) -> List[DocumentDB]:
        """
        List documents with optional filtering

        Args:
            doc_type: Optional document type filter
            limit: Maximum number of results

        Returns:
            List of DocumentDB models
        """
        async with get_session() as session:
            query = select(DocumentDB)

            if doc_type:
                query = query.where(DocumentDB.type == doc_type)

            query = query.limit(limit)
            result = await session.execute(query)
            return result.all()

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False otherwise
        """
        async with get_session() as session:
            result = await session.execute(
                select(DocumentDB).where(DocumentDB.doc_id == doc_id)
            )
            doc = result.first()

            if doc:
                await session.delete(doc)
                await session.commit()
                logger.info(f"Deleted document {doc_id}")
                return True

            return False


async def index_uploaded_files(file_paths: List[str], mcp_client: Any = None) -> List[Dict]:
    """
    Convenience function to index uploaded files

    Args:
        file_paths: List of uploaded file paths
        mcp_client: Optional MCP client for RAG indexing

    Returns:
        List of indexing results

    Example:
        ```python
        results = await index_uploaded_files(
            file_paths=["swagger.yaml", "openapi.json"],
            mcp_client=mcp_client
        )
        for result in results:
            print(f"{result['doc_id']}: {result['status']}")
        ```
    """
    indexer = DocumentIndexer(mcp_client)
    return await indexer.index_documents(file_paths)
