# database.py
import os
import mysql.connector  # type: ignore
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
DB_NAME = os.getenv("MYSQL_DATABASE", "ecommerce_db")

# --- MySQL (low-level connector, used for listing schema) ---
def get_connection(database: str = None):
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database if database else DB_NAME,
    )

def list_databases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    dbs = [db[0] for db in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"databases": dbs}

def list_tables(database: str = DB_NAME):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"tables": tables}

def list_columns(database: str, table_name: str):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [col[0] for col in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"columns": columns}

# --- SQLAlchemy (used for queries & ORM models) ---
SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
