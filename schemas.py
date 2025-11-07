from pydantic import BaseModel, Field # type: ignore
from typing import Optional

# -------------------- USER AUTH SCHEMAS --------------------

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # ✅ Pydantic v2 replacement for orm_mode

class Token(BaseModel):
    access_token: str
    token_type: str

# -------------------- SQL GENERATION SCHEMA --------------------
class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    db_name: str = Field(..., description="Database name to query against")

# --- Add this class to your schemas.py file ---

class SQLRequest(BaseModel):
    query: str = Field(..., min_length=1, description="SQL query to execute")
    db_name: str