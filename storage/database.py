import sqlite3
import os
from typing import Optional
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'job_data.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT NOT NULL,
    company TEXT DEFAULT '',
    location TEXT DEFAULT '',
    location_tier TEXT DEFAULT '',
    salary_text TEXT DEFAULT '',
    salary_min REAL,
    salary_max REAL,
    salary_range TEXT DEFAULT '',
    education TEXT DEFAULT '',
    experience TEXT DEFAULT '',
    tech_stack TEXT DEFAULT '',
    description TEXT DEFAULT '',
    source TEXT DEFAULT '',
    post_date TEXT DEFAULT '',
    job_type TEXT DEFAULT '',
    scraped_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS scrape_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    keyword TEXT,
    location TEXT,
    items_found INTEGER DEFAULT 0,
    started_at TEXT DEFAULT (datetime('now', 'localtime')),
    finished_at TEXT,
    status TEXT DEFAULT 'running'
);
"""


class Database:
    """SQLite 数据库操作"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def init(self):
        """初始化数据库表（含迁移）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)
            # 迁移：添加新列（忽略已存在的列）
            migrations = [
                "ALTER TABLE jobs ADD COLUMN is_accept_graduate INTEGER DEFAULT 0",
                "ALTER TABLE jobs ADD COLUMN has_weekend_off INTEGER DEFAULT 0",
                "ALTER TABLE jobs ADD COLUMN has_insurance INTEGER DEFAULT 0",
            ]
            for sql in migrations:
                try:
                    conn.execute(sql)
                except sqlite3.OperationalError:
                    pass  # 列已存在
            conn.commit()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def upsert_jobs(self, jobs: list[dict]) -> int:
        """插入或更新职位（按URL去重），返回新增数量"""
        fields = [
            'url', 'title', 'company', 'location', 'location_tier',
            'salary_text', 'salary_min', 'salary_max', 'salary_range',
            'education', 'experience', 'tech_stack', 'description',
            'source', 'post_date', 'job_type',
            'is_accept_graduate', 'has_weekend_off', 'has_insurance',
        ]
        placeholders = ', '.join([':' + f for f in fields])
        sql = f"INSERT OR IGNORE INTO jobs ({', '.join(fields)}) VALUES ({placeholders})"
        count = 0
        with self._get_conn() as conn:
            for job in jobs:
                # 为缺失字段填充默认值
                safe_job = {}
                for f in fields:
                    val = job.get(f, job.get(f.lstrip('_'), ''))
                    if isinstance(val, bool):
                        val = 1 if val else 0
                    safe_job[f] = val if val is not None else ''
                try:
                    cursor = conn.execute(sql, safe_job)
                    if cursor.rowcount > 0:
                        count += 1
                except Exception:
                    continue
            conn.commit()
        return count

    def query_jobs(self, filters: Optional[dict] = None, limit: int = 500) -> pd.DataFrame:
        """查询职位，返回 DataFrame"""
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if filters:
            if filters.get('education'):
                placeholders = ','.join(['?' for _ in filters['education']])
                query += f" AND education IN ({placeholders})"
                params.extend(filters['education'])
            if filters.get('location_tier'):
                placeholders = ','.join(['?' for _ in filters['location_tier']])
                query += f" AND location_tier IN ({placeholders})"
                params.extend(filters['location_tier'])
            if filters.get('salary_range'):
                placeholders = ','.join(['?' for _ in filters['salary_range']])
                query += f" AND salary_range IN ({placeholders})"
                params.extend(filters['salary_range'])
            if filters.get('source'):
                placeholders = ','.join(['?' for _ in filters['source']])
                query += f" AND source IN ({placeholders})"
                params.extend(filters['source'])
            if filters.get('keyword'):
                kw = f"%{filters['keyword']}%"
                query += " AND (title LIKE ? OR description LIKE ? OR tech_stack LIKE ?)"
                params.extend([kw, kw, kw])
            if filters.get('tech_stack'):
                for tech in filters['tech_stack']:
                    query += " AND tech_stack LIKE ?"
                    params.append(f"%{tech}%")
            if filters.get('is_accept_graduate') is not None:
                query += " AND is_accept_graduate = ?"
                params.append(1 if filters['is_accept_graduate'] else 0)
            if filters.get('has_weekend_off') is not None:
                query += " AND has_weekend_off = ?"
                params.append(1 if filters['has_weekend_off'] else 0)
            if filters.get('has_insurance') is not None:
                query += " AND has_insurance = ?"
                params.append(1 if filters['has_insurance'] else 0)

        query += " ORDER BY scraped_at DESC LIMIT ?"
        params.append(limit)

        with self._get_conn() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_stats(self) -> dict:
        """获取数据统计"""
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
            sources = conn.execute(
                "SELECT source, COUNT(*) as cnt FROM jobs GROUP BY source ORDER BY cnt DESC"
            ).fetchall()
            education = conn.execute(
                "SELECT education, COUNT(*) as cnt FROM jobs WHERE education != '' GROUP BY education ORDER BY cnt DESC"
            ).fetchall()
            salary = conn.execute(
                "SELECT salary_range, COUNT(*) as cnt FROM jobs WHERE salary_range != '' GROUP BY salary_range ORDER BY cnt DESC"
            ).fetchall()
            location = conn.execute(
                "SELECT location_tier, COUNT(*) as cnt FROM jobs WHERE location_tier != '' GROUP BY location_tier ORDER BY cnt DESC"
            ).fetchall()
            tech = conn.execute(
                "SELECT tech_stack FROM jobs WHERE tech_stack != ''"
            ).fetchall()
            companies = conn.execute(
                "SELECT company, COUNT(*) as cnt FROM jobs WHERE company != '' GROUP BY company ORDER BY cnt DESC LIMIT 20"
            ).fetchall()

        tech_counts = {}
        for (ts,) in tech:
            for t in ts.split(','):
                t = t.strip()
                if t:
                    tech_counts[t] = tech_counts.get(t, 0) + 1
        tech_sorted = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            'total': total,
            'sources': [dict(r) for r in sources],
            'education': [dict(r) for r in education],
            'salary': [dict(r) for r in salary],
            'location': [dict(r) for r in location],
            'tech_stack': [{'name': k, 'cnt': v} for k, v in tech_sorted],
            'companies': [dict(r) for r in companies],
        }

    def log_scrape_start(self, source: str, keyword: str, location: str) -> int:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO scrape_logs (source, keyword, location) VALUES (?, ?, ?)",
                (source, keyword, location)
            )
            conn.commit()
            return cursor.lastrowid

    def log_scrape_end(self, log_id: int, items_found: int, status: str = 'success'):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE scrape_logs SET items_found=?, finished_at=datetime('now','localtime'), status=? WHERE id=?",
                (items_found, status, log_id)
            )
            conn.commit()

    def clear_all(self):
        """清空所有数据"""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM jobs")
            conn.execute("DELETE FROM scrape_logs")
            conn.commit()
