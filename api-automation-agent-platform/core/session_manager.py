"""
Session Management Service

Manages test sessions, authentication tokens, and execution context.
Provides persistent session storage with real MCP integration.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import logging

from api_agent.models import SessionDB
from api_agent.db import get_session
from sqlmodel import select
import uuid

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Session Manager

    Manages test sessions with:
    - Persistent storage
    - Authentication token management
    - Test execution tracking
    - State management
    """

    def __init__(self, mcp_client: Any = None):
        """
        Initialize session manager

        Args:
            mcp_client: Optional MCP client for session operations
        """
        self.mcp_client = mcp_client

    async def create_session(
        self,
        name: str,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new test session

        Args:
            name: Session name
            description: Optional session description
            user_id: Optional user ID
            metadata: Optional additional metadata

        Returns:
            Session information with ID
        """
        session_id = str(uuid.uuid4())

        # Store in database
        async with get_session() as session:
            db_session = SessionDB(
                session_id=session_id,
                user_id=user_id,
                name=name,
                description=description,
                active=True,
                meta_data=metadata or {}
            )
            session.add(db_session)
            await session.commit()

        logger.info(f"Created session {session_id}: {name}")

        # Create MCP session if client available
        if self.mcp_client:
            try:
                mcp_result = await self.mcp_client.call_tool(
                    "automation-quality",
                    "session_create",
                    {
                        "name": name,
                        "description": description,
                        "metadata": metadata or {}
                    }
                )
                logger.debug(f"MCP session created: {mcp_result}")
            except Exception as e:
                logger.warning(f"MCP session creation failed: {e}")

        return {
            "status": "success",
            "session_id": session_id,
            "name": name,
            "description": description,
            "active": True,
            "created_at": datetime.utcnow().isoformat()
        }

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        async with get_session() as session:
            result = await session.execute(
                select(SessionDB).where(SessionDB.session_id == session_id)
            )
            db_session = result.first()

            if not db_session:
                return None

            return {
                "session_id": db_session.session_id,
                "name": db_session.name,
                "description": db_session.description,
                "user_id": db_session.user_id,
                "active": db_session.active,
                "created_at": db_session.created_at.isoformat(),
                "updated_at": db_session.updated_at.isoformat(),
                "tasks": db_session.tasks,
                "meta_data": db_session.meta_data
            }

    async def update_session(
        self,
        session_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update session data

        Args:
            session_id: Session ID
            data: Data to update (merged with existing)

        Returns:
            Updated session data
        """
        async with get_session() as session:
            result = await session.execute(
                select(SessionDB).where(SessionDB.session_id == session_id)
            )
            db_session = result.first()

            if not db_session:
                return {
                    "status": "error",
                    "error": "Session not found"
                }

            # Update timestamp
            db_session.updated_at = datetime.utcnow()

            # Merge metadata
            if db_session.meta_data is None:
                db_session.meta_data = {}
            db_session.meta_data.update(data)

            # Update specific session fields
            if "tasks" in data:
                db_session.tasks = data["tasks"]
            if "active" in data:
                db_session.active = data["active"]

            session.add(db_session)
            await session.commit()

        # Update MCP session if client available
        if self.mcp_client:
            try:
                await self.mcp_client.call_tool(
                    "automation-quality",
                    "session_update",
                    {
                        "sessionId": session_id,
                        "data": data
                    }
                )
            except Exception as e:
                logger.warning(f"MCP session update failed: {e}")

        logger.info(f"Updated session {session_id}")

        # Return updated session
        return await self.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False otherwise
        """
        async with get_session() as session:
            result = await session.execute(
                select(SessionDB).where(SessionDB.session_id == session_id)
            )
            db_session = result.first()

            if not db_session:
                return False

            await session.delete(db_session)
            await session.commit()

        logger.info(f"Deleted session {session_id}")
        return True

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        active_only: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List sessions with optional filters

        Args:
            user_id: Optional filter by user ID
            active_only: Only return active sessions
            limit: Maximum number of results

        Returns:
            List of session data
        """
        async with get_session() as session:
            query = select(SessionDB)

            if user_id:
                query = query.where(SessionDB.user_id == user_id)
            if active_only:
                query = query.where(SessionDB.active == True)

            query = query.limit(limit)
            query = query.order_by(SessionDB.created_at.desc())

            result = await session.execute(query)
            db_sessions = result.all()

        sessions = []
        for db_session in db_sessions:
            sessions.append({
                "session_id": db_session.session_id,
                "name": db_session.name,
                "description": db_session.description,
                "user_id": db_session.user_id,
                "active": db_session.active,
                "created_at": db_session.created_at.isoformat(),
                "updated_at": db_session.updated_at.isoformat(),
                "tasks": db_session.tasks,
                "meta_data": db_session.meta_data
            })

        return sessions

    async def add_task_to_session(
        self,
        session_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Add a task to a session

        Args:
            session_id: Session ID
            task_id: Task ID to add

        Returns:
            Updated session data
        """
        async with get_session() as session:
            result = await session.execute(
                select(SessionDB).where(SessionDB.session_id == session_id)
            )
            db_session = result.first()

            if not db_session:
                return {
                    "status": "error",
                    "error": "Session not found"
                }

            # Add task to session
            if db_session.tasks is None:
                db_session.tasks = []
            if task_id not in db_session.tasks:
                db_session.tasks.append(task_id)

            db_session.updated_at = datetime.utcnow()
            session.add(db_session)
            await session.commit()

        logger.info(f"Added task {task_id} to session {session_id}")

        return await self.get_session(session_id)

    async def set_auth_token(
        self,
        session_id: str,
        token: str,
        token_type: str = "bearer"
    ) -> Dict[str, Any]:
        """
        Store authentication token in session

        Args:
            session_id: Session ID
            token: Authentication token
            token_type: Token type (bearer, api_key, etc.)

        Returns:
            Updated session data
        """
        return await self.update_session(
            session_id,
            {
                "auth_token": token,
                "auth_token_type": token_type
            }
        )

    async def get_auth_token(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Get authentication token from session

        Args:
            session_id: Session ID

        Returns:
            Token data or None if not found
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return None

        meta_data = session_data.get("meta_data", {})

        if "auth_token" in meta_data:
            return {
                "token": meta_data["auth_token"],
                "type": meta_data.get("auth_token_type", "bearer")
            }

        return None

    async def deactivate_session(self, session_id: str) -> Dict[str, Any]:
        """
        Deactivate a session (mark as inactive)

        Args:
            session_id: Session ID

        Returns:
            Updated session data
        """
        return await self.update_session(session_id, {"active": False})

    async def cleanup_old_sessions(
        self,
        days: int = 7,
        user_id: Optional[str] = None
    ) -> int:
        """
        Clean up old inactive sessions

        Args:
            days: Delete sessions older than this many days
            user_id: Optional filter by user ID

        Returns:
            Number of sessions deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        async with get_session() as session:
            query = select(SessionDB).where(
                (SessionDB.created_at < cutoff_date) &
                (SessionDB.active == False)
            )

            if user_id:
                query = query.where(SessionDB.user_id == user_id)

            result = await session.execute(query)
            old_sessions = result.all()

            deleted_count = 0
            for old_session in old_sessions:
                await session.delete(old_session)
                deleted_count += 1

            await session.commit()

        logger.info(f"Cleaned up {deleted_count} old sessions")
        return deleted_count


# Singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(mcp_client: Any = None) -> SessionManager:
    """
    Get or create session manager singleton

    Args:
        mcp_client: Optional MCP client

    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(mcp_client)
    return _session_manager


def reset_session_manager():
    """Reset session manager singleton (mainly for testing)"""
    global _session_manager
    _session_manager = None
