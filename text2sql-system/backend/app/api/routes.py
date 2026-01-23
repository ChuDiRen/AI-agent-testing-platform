"""
REST API路由
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

router = APIRouter()


@router.get("/status")
async def get_status():
    """获取API状态"""
    return {
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/api/text2sql/websocket",
            "health": "/health"
        }
    }


@router.get("/schema")
async def get_database_schema():
    """获取数据库schema信息"""
    # TODO: 从实际数据库获取schema
    return {
        "database_type": "sqlite",
        "tables": [
            "Customer",
            "Invoice",
            "InvoiceLine",
            "Track",
            "Album",
            "Artist",
            "Genre",
            "MediaType",
            "Playlist",
            "PlaylistTrack",
            "Employee"
        ]
    }
