# app.py
from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import Dict
import uvicorn # type: ignore

# --- Database, Models, Schemas, Security Imports ---
from database import get_db, list_databases, list_tables, list_columns, engine
from models import Base, User
# 🚩 FIX 1: Import ALL your required Pydantic models
from schemas import UserCreate, Token, QueryRequest, SQLRequest 
from security import verify_password, get_password_hash, create_access_token, decode_access_token
from query_generator import generate_sql_query, execute_query, validate_sql_query

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SQLGenie API", version="2.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- User Registration (Correct) ---
@app.post("/register/", response_model=Dict[str, str], status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

# --- Login & JWT (Correct) ---
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- Auth Helper (Correct) ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Schema Explorer (Correct) ---
@app.get("/list_databases/")
def api_list_databases(current_user: User = Depends(get_current_user)):
    return list_databases()

@app.get("/list_tables/{db_name}")
def api_list_tables(db_name: str, current_user: User = Depends(get_current_user)):
    return list_tables(db_name)

@app.get("/list_columns/{db_name}/{table_name}")
def api_list_columns(db_name: str, table_name: str, current_user: User = Depends(get_current_user)):
    return list_columns(db_name, table_name)

# --- SQL Generation (Correct) ---
@app.post("/generate_sql/")
def api_generate_sql(request: QueryRequest, current_user: User = Depends(get_current_user)):
    sql = generate_sql_query(request.query, request.db_name)
    query_type = sql.strip().split()[0].lower()
    return {
        "sql_query": sql,
        "query_type": query_type
    }

# --- SQL Execution (🚩 FIX 2: Corrected Endpoint) ---
@app.post("/execute_sql/")
def api_execute_sql(request: SQLRequest, current_user: User = Depends(get_current_user)):
    """
    This now correctly receives the SQLRequest Pydantic model from the JSON body,
    matching the Streamlit frontend's request.
    """
    # Access the query and db_name from the request model
    return execute_query(request.query, request.db_name)

# --- Root (Correct) ---
@app.get("/")
def root():
    return {"message": "Welcome to SQLGenie API"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)