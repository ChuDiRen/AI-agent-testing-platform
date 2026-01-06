"""
API Automation Agent Platform - Document API Routes

This module handles document-related endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
import uuid
import hashlib
import os

from api_agent import settings
from api_agent.db import get_session
from api_agent.models import (
    DocumentDB, DocumentUpload, DocumentResponse
)

router = APIRouter()


@router.post("/", response_model=DocumentResponse)
async def create_document(
    doc: DocumentUpload,
    session: Session = Depends(get_session)
):
    """Create a new document metadata record"""
    doc_id = str(uuid.uuid4())
    db_doc = DocumentDB(
        doc_id=doc_id,
        name=doc.name,
        type=doc.type,
        url=str(doc.url) if doc.url else None
    )

    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)

    return DocumentResponse(
        doc_id=db_doc.doc_id,
        name=db_doc.name,
        type=db_doc.type,
        indexed=db_doc.indexed,
        created_at=db_doc.created_at.isoformat(),
        updated_at=db_doc.updated_at.isoformat()
    )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = "unknown",
    session: Session = Depends(get_session)
):
    """Upload a document file"""
    doc_id = str(uuid.uuid4())

    # Create upload directory if not exists
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()

    with open(file_path, "wb") as f:
        f.write(content)

    db_doc = DocumentDB(
        doc_id=doc_id,
        name=file.filename,
        type=doc_type,
        file_path=file_path,
        content_hash=content_hash
    )

    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)

    return DocumentResponse(
        doc_id=db_doc.doc_id,
        name=db_doc.name,
        type=db_doc.type,
        indexed=db_doc.indexed,
        created_at=db_doc.created_at.isoformat(),
        updated_at=db_doc.updated_at.isoformat()
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    session: Session = Depends(get_session)
):
    """Get document by ID"""
    db_doc = session.get(DocumentDB, doc_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        doc_id=db_doc.doc_id,
        name=db_doc.name,
        type=db_doc.type,
        indexed=db_doc.indexed,
        created_at=db_doc.created_at.isoformat(),
        updated_at=db_doc.updated_at.isoformat()
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all documents"""
    statement = select(DocumentDB).offset(skip).limit(limit)
    results = session.exec(statement).all()

    return [
        DocumentResponse(
            doc_id=doc.doc_id,
            name=doc.name,
            type=doc.type,
            indexed=doc.indexed,
            created_at=doc.created_at.isoformat(),
            updated_at=doc.updated_at.isoformat()
        )
        for doc in results
    ]


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    session: Session = Depends(get_session)
):
    """Delete document by ID"""
    db_doc = session.get(DocumentDB, doc_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file if exists
    if db_doc.file_path and os.path.exists(db_doc.file_path):
        os.remove(db_doc.file_path)

    session.delete(db_doc)
    session.commit()

    return {"message": "Document deleted successfully"}
