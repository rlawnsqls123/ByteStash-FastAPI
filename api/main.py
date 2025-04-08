from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from contextlib import contextmanager
import sqlite3, os
from dotenv import load_dotenv


# 환경 변수 불러오기
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "snippets.db")
API_KEY = os.getenv("API_KEY", "my-secret-api-key-1234")

app = FastAPI(
    title="ByteStash API",
    description="SQLite + API Key 기반 Snippet API",
    docs_url="/api/docs",               # Swagger UI URL
    openapi_url="/api/openapi.json"     # OpenAPI JSON 경로
)

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    return {"status": "정상"}

app.include_router(router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://bytestash.tripk.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key 인증
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="API 키가 유효하지 않습니다")

# 데이터 모델
class Snippet(BaseModel):
    id: int
    title: str
    description: str
    updated_at: str

class CodeBlock(BaseModel):
    language: str
    code: str

class SnippetDetail(BaseModel):
    id: int
    title: str
    description: str
    updated_at: str
    username: str
    code_blocks: List[CodeBlock]

@contextmanager
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB 연결 실패: {str(e)}")

@app.get("/snippets/", response_model=List[Snippet], dependencies=[Depends(verify_api_key)])
def get_snippets():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, updated_at FROM snippets ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

@app.get("/snippets/{snippet_id}", response_model=SnippetDetail, dependencies=[Depends(verify_api_key)])
def get_snippet_detail(snippet_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.title, s.description, s.updated_at,
                   u.username, f.code, f.language
            FROM snippets s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN fragments f ON f.snippet_id = s.id
            WHERE s.id = ?
            ORDER BY f.position
        """, (snippet_id,))
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="스니펫을 찾을 수 없습니다")
        first = rows[0]
        return {
            "id": first["id"],
            "title": first["title"],
            "description": first["description"] or "",
            "updated_at": first["updated_at"],
            "username": first["username"] or "익명",
            "code_blocks": [
                {"language": row["language"] or "unknown", "code": row["code"] or ""}
                for row in rows if row["code"]
            ]
        }

@app.get("/health")
def health_check():
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "정상", "database": "연결됨"}
    except:
        raise HTTPException(status_code=503, detail="DB 연결 실패")


