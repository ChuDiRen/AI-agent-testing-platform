# Copyright (c) 2025 左岚. All rights reserved.
"""
数据管理API路由
提供数据备份、恢复、清理等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import json
import os
from pathlib import Path

from app.core.database import get_db, engine
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter()

# 备份目录
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


@router.get("/backup/list", response_model=APIResponse[list])
async def list_backups(
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[list]:
    """获取备份文件列表"""
    try:
        backups = []
        for file in BACKUP_DIR.glob("*.sql"):
            stat = file.stat()
            backups.append({
                "filename": file.name,
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "path": str(file)
            })
        
        # 按创建时间倒序排列
        backups.sort(key=lambda x: x["created_time"], reverse=True)
        
        return APIResponse(
            success=True,
            message=f"获取备份列表成功,共{len(backups)}个备份",
            data=backups
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取备份列表失败: {str(e)}"
        )


@router.post("/backup/create", response_model=APIResponse[dict])
async def create_backup(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """创建数据库备份"""
    try:
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"backup_{timestamp}.sql"
        
        # 获取所有表名
        result = await db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        tables = [row[0] for row in result.fetchall()]
        
        # 导出数据
        backup_content = []
        backup_content.append(f"-- Database Backup Created at {datetime.now().isoformat()}\n")
        backup_content.append(f"-- User: {current_user.username}\n\n")
        
        for table in tables:
            # 获取表结构
            result = await db.execute(text(f"SELECT sql FROM sqlite_master WHERE name='{table}'"))
            create_sql = result.scalar()
            if create_sql:
                backup_content.append(f"-- Table: {table}\n")
                backup_content.append(f"{create_sql};\n\n")
            
            # 获取表数据
            result = await db.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                backup_content.append(f"-- Data for table: {table}\n")
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append("NULL")
                        elif isinstance(val, str):
                            values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")  # 转义单引号
                        else:
                            values.append(str(val))
                    backup_content.append(
                        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(values)});\n"
                    )
                backup_content.append("\n")
        
        # 写入备份文件
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(backup_content)
        
        return APIResponse(
            success=True,
            message="数据库备份成功",
            data={
                "filename": backup_file.name,
                "size": backup_file.stat().st_size,
                "tables": len(tables),
                "created_time": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"数据库备份失败: {str(e)}"
        )


@router.delete("/backup/{filename}", response_model=APIResponse[None])
async def delete_backup(
    filename: str,
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除备份文件"""
    try:
        backup_file = BACKUP_DIR / filename
        if not backup_file.exists():
            return APIResponse(
                success=False,
                message="备份文件不存在"
            )
        
        backup_file.unlink()
        
        return APIResponse(
            success=True,
            message="备份文件删除成功"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"删除备份文件失败: {str(e)}"
        )


@router.get("/stats", response_model=APIResponse[dict])
async def get_database_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """获取数据库统计信息"""
    try:
        # 获取所有表名和记录数
        result = await db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        tables = [row[0] for row in result.fetchall()]
        
        table_stats = []
        total_records = 0
        
        for table in tables:
            result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            total_records += count
            table_stats.append({
                "table": table,
                "records": count
            })
        
        # 获取数据库文件大小
        db_file = Path("app.db")
        db_size = db_file.stat().st_size if db_file.exists() else 0
        
        # 获取备份数量
        backup_count = len(list(BACKUP_DIR.glob("*.sql")))
        
        return APIResponse(
            success=True,
            data={
                "total_tables": len(tables),
                "total_records": total_records,
                "database_size": db_size,
                "backup_count": backup_count,
                "table_stats": table_stats
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取数据库统计失败: {str(e)}"
        )


@router.post("/cleanup", response_model=APIResponse[dict])
async def cleanup_data(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """清理旧数据"""
    try:
        # 清理通知数据
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        result = await db.execute(text(
            f"DELETE FROM t_notification WHERE is_read = 1 AND read_time < datetime({cutoff_date}, 'unixepoch')"
        ))
        notification_deleted = result.rowcount
        
        await db.commit()
        
        return APIResponse(
            success=True,
            message=f"数据清理成功",
            data={
                "notification_deleted": notification_deleted,
                "days": days
            }
        )
    except Exception as e:
        await db.rollback()
        return APIResponse(
            success=False,
            message=f"数据清理失败: {str(e)}"
        )


@router.post("/optimize", response_model=APIResponse[dict])
async def optimize_database(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """优化数据库"""
    try:
        # SQLite VACUUM命令
        await db.execute(text("VACUUM"))
        await db.commit()
        
        # 获取优化后的数据库大小
        db_file = Path("app.db")
        db_size = db_file.stat().st_size if db_file.exists() else 0
        
        return APIResponse(
            success=True,
            message="数据库优化成功",
            data={
                "database_size": db_size
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"数据库优化失败: {str(e)}"
        )

