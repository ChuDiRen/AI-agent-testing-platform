"""数据库管理"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import TestCaseRecord


class TestCaseDB:
    """测试用例数据库"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        # 确保 data 目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    requirement TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    analysis TEXT,
                    testcases TEXT NOT NULL,
                    review TEXT,
                    iteration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_thread_id ON test_cases(thread_id);
                CREATE INDEX IF NOT EXISTS idx_created_at ON test_cases(created_at DESC);
            """)
    
    @contextmanager
    def _connect(self):
        """数据库连接上下文"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def save(self, thread_id: str, requirement: str, test_type: str,
             analysis: str, testcases: str, review: str, iteration: int) -> int:
        """保存测试用例"""
        with self._connect() as conn:
            cursor = conn.execute("""
                INSERT INTO test_cases (thread_id, requirement, test_type, analysis, testcases, review, iteration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (thread_id, requirement, test_type, analysis, testcases, review, iteration))
            return cursor.lastrowid

    def save_testcase(self, state) -> int:
        """保存 TestCaseState 到数据库

        Args:
            state: TestCaseState 实例

        Returns:
            插入的记录ID
        """
        thread_id = getattr(state, 'thread_id', 'default')
        return self.save(
            thread_id=thread_id,
            requirement=state.requirement,
            test_type=state.test_type,
            analysis=state.analysis or "",
            testcases=state.testcases or "",
            review=state.review or "",
            iteration=state.iteration
        )
    
    def list_recent(self, limit: int = 10) -> List[TestCaseRecord]:
        """列出最近的记录"""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM test_cases ORDER BY created_at DESC LIMIT ?
            """, (limit,)).fetchall()
            return [TestCaseRecord(
                id=row['id'],
                thread_id=row['thread_id'],
                requirement=row['requirement'],
                test_type=row['test_type'],
                analysis=row['analysis'],
                testcases=row['testcases'],
                review=row['review'],
                iteration=row['iteration'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in rows]
    
    def get_by_id(self, testcase_id: int) -> Optional[TestCaseRecord]:
        """根据ID获取"""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM test_cases WHERE id = ?", (testcase_id,)).fetchone()
            if not row:
                return None
            return TestCaseRecord(
                id=row['id'],
                thread_id=row['thread_id'],
                requirement=row['requirement'],
                test_type=row['test_type'],
                analysis=row['analysis'],
                testcases=row['testcases'],
                review=row['review'],
                iteration=row['iteration'],
                created_at=datetime.fromisoformat(row['created_at'])
            )

