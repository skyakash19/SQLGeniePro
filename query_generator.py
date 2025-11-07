# query_generator.py
from asyncio.log import logger
from logging import config
import os
import json
import re
import logging
from functools import lru_cache
from typing import Tuple, Optional, Dict, Any
from sqlalchemy import text # type: ignore
from dotenv import load_dotenv # type: ignore
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from database import engine, list_tables, list_columns

import google.generativeai as genai  # type: ignore # ✅ Correct Gemini import
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Gemini model setup
def get_model(prefer_speed=False):
    model_name = "gemini-2.5-flash" if prefer_speed else "gemini-2.5-pro"
    return genai.GenerativeModel(model_name)


model = get_model(prefer_speed=False)


# Limits
MAX_TABLES = 10
MAX_COLUMNS_PER_TABLE = 10

# ----------------------------
# Gemini Cost Estimation (Placeholder)
# ----------------------------
def estimate_cost(usage: Any, model: str = "Gemini-2.5-Pro") -> Dict[str, Any]:
    # Gemini SDK does not expose token usage directly.
    # This function is retained for future compatibility or logging.
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "input_cost_usd": 0.0,
        "output_cost_usd": 0.0,
        "total_cost_usd": 0.0,
    }

# ----------------------------
# SQL Output Cleaning
# ----------------------------
def clean_sql_output(raw: str) -> str:
    if not isinstance(raw, str):
        return ""
    cleaned = re.sub(r"```(?:sql)?\s*", "", raw, flags=re.IGNORECASE).replace("```", "").strip()

    lines = cleaned.splitlines()
    while lines and re.match(r'^\s*(--|/\*).*', lines[0]):
        lines.pop(0)
    while lines and re.match(r'^\s*(--|/\*).*', lines[-1]):
        lines.pop(-1)

    cleaned = "\n".join(lines).strip()
    return cleaned


# ----------------------------
# Cached Schema Retrieval
# ----------------------------
@lru_cache(maxsize=128)
def get_cached_schema(db_name: Optional[str]) -> dict:
    if not db_name:
        logger.debug("No db_name provided to get_cached_schema(); returning empty schema.")
        return {}

    schema = {}
    try:
        tables_resp = list_tables(db_name)
        tables = tables_resp.get("tables", []) if isinstance(tables_resp, dict) else tables_resp
        if not tables:
            logger.warning("list_tables returned no tables for db '%s'", db_name)
            return {}
        tables = tables[:MAX_TABLES]
    except Exception as e:
        logger.warning("Could not list tables for %s: %s", db_name, e)
        return {}

    for table in tables:
        try:
            cols_resp = list_columns(db_name, table)
            cols = cols_resp.get("columns", []) if isinstance(cols_resp, dict) else cols_resp
            schema[table] = cols[:MAX_COLUMNS_PER_TABLE] if cols else []
        except Exception as e:
            logger.warning("Could not list columns for %s.%s: %s", db_name, table, e)
            schema[table] = []

    return schema


# ----------------------------
# SQL Validation
# ----------------------------
def validate_sql_query(query: str) -> Tuple[bool, Optional[str]]:
    if not query or not isinstance(query, str):
        return False, "Empty or invalid SQL"

    try:
        cleaned = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
        cleaned_no_inline = re.sub(r"--.*", "", cleaned)
    except Exception:
        cleaned_no_inline = query

    cleaned_no_inline = cleaned_no_inline.strip()
    if ";" in cleaned_no_inline.strip().rstrip(";"):
        return False, "Multiple statements not allowed"

    low = cleaned_no_inline.lower().lstrip()
    #if not low.startswith("select"):
        #return False, "Only SELECT queries are permitted"

    forbidden = ["drop", "truncate", "alter", "create", "grant", "revoke", "shutdown", "insert", "update", "delete"]
    for kw in forbidden:
        if re.search(rf"\b{kw}\b", low):
            return False, f"Forbidden SQL keyword detected: {kw}"

    return True, None

# ----------------------------
# Main SQL Generator (Gemini)
# ----------------------------
def generate_sql_query(nl_query: str, db_name: Optional[str]) -> str:
    if not db_name:
        return "❌ Error: db_name is required for schema-aware generation."

    schema = get_cached_schema(db_name)
    if not schema:
        return f"❌ Error: Could not load schema for database '{db_name}'."

    schema_text = json.dumps(schema, indent=2)

    prompt = f"""
    You are an exceptionally precise and security-conscious **MySQL Expert**. Your sole task is to convert a user's request into a valid, optimized SQL SELECT statement.

    ## Instructions:
    1. **Security:** NEVER generate DELETE, DROP, UPDATE, or INSERT statements. Only SELECT is permitted.
    2. **Optimization:** Write the most efficient query possible, prioritizing explicit JOINs over subqueries when applicable.
    3. **Format:** Return ONLY the SQL query. Do not include markdown code fences (```sql) or any explanatory text.

    ## Database Schema and Context:
    {schema_text}  # MUST include relationships and data types here

    ## User Query:
    {nl_query}

    SQL Query: 
    """
    try:
        logger.info("Sending query to Gemini for DB '%s'...", db_name)
        response = model.generate_content(prompt)
        raw_sql_query = response.text.strip()
        cleaned_query = clean_sql_output(raw_sql_query)

        logger.info(f"Raw Gemini Output:\n{raw_sql_query}\n")
        logger.info(f"Cleaned SQL Query:\n{cleaned_query}\n")

        return cleaned_query

    except Exception as e:
        logger.exception("Gemini request failed")
        return f"❌ Error generating SQL query: {e}"
# NOTE: The 'engine' variable and 'validate_sql_query' function 
# are assumed to be defined and imported globally.
from sqlalchemy import text # type: ignore
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from typing import Optional # type: ignore
import logging
# logging.getLogger() must be configured earlier in your app
# Assuming 'engine' and 'validate_sql_query' are available

def execute_query(sql_query: str, db_name: Optional[str]) -> dict:
    if not db_name:
        return {"error": "Database name is required for query execution."}

    # Assuming validate_sql_query is available and returns (bool, str)
    ok, reason = validate_sql_query(sql_query)
    if not ok:
        return {"error": f"SQL validation failed: {reason}"}

    # Determine if the query is a Data Manipulation Language (DML) or Data Definition Language (DDL)
    # This is a critical simplification for transaction handling.
    query_type = sql_query.strip().split(maxsplit=1)[0].upper()
    is_write_operation = query_type in ["INSERT", "UPDATE", "DELETE", "TRUNCATE", "DROP", "CREATE", "ALTER"]
    
    try:
        # NOTE: 'engine' must be available globally or passed here
        engine_instance = engine 
        
        # Use begin() to handle transactions implicitly, ensuring atomicity
        with engine_instance.begin() as conn: # begin() manages commit/rollback
            conn.execute(text(f"USE {db_name}"))

            # Execute the query
            result = conn.execute(text(sql_query))

            if is_write_operation:
                # For DML/DDL, return the number of affected rows instead of data
                return {
                    "results": [{"message": f"Query executed successfully.", "rows_affected": result.rowcount}],
                    "optimization_tips": "N/A (Write Operation)"
                }
            else:
                # For SELECT queries
                rows = result.fetchall()
                columns = result.keys()

                # 🧠 Detect empty result and suggest alternatives
                if not rows:
                    suggestions = suggest_similar_values(sql_query, db_name)
                    return {
                        "results": [],
                        "message": "No results found. Did you mean one of these?",
                        "suggestions": suggestions,
                        "optimization_tips": "Consider using LIKE or fuzzy matching."
                    }

                # If results exist, format and return
                formatted = [dict(zip(columns, row)) for row in rows]

                optimization_suggestion = "Run EXPLAIN to find slow operations."

                return {
                    "results": formatted,
                    "optimization_tips": optimization_suggestion
                }

                
    except SQLAlchemyError as e:
        logging.exception("SQLAlchemy execution error")
        return {"error": f"Database Execution Error: {e}"}
    except Exception as e:
        logging.exception("General execution error")
        return {"error": f"Execution Error: {e}"}
    
def suggest_similar_values(sql_query: str, db_name: str) -> list:
    # Very basic example: extract string literal from WHERE clause
    match = re.search(r"WHERE\s+\w+\.\w+\s*=\s*'([^']+)'", sql_query, re.IGNORECASE)
    if not match:
        return []

    target_value = match.group(1)
    table_match = re.search(r"FROM\s+(\w+)", sql_query, re.IGNORECASE)
    if not table_match:
        return []

    table_name = table_match.group(1)

    # Search for similar values using LIKE
    try:
        with engine.begin() as conn:
            conn.execute(text(f"USE {db_name}"))
            query = text(f"""
                SELECT DISTINCT name FROM {table_name}
                WHERE name LIKE :pattern
                LIMIT 5
            """)
            result = conn.execute(query, {"pattern": f"%{target_value.split()[0]}%"})
            return [row[0] for row in result.fetchall()]
    except Exception as e:
        logging.warning(f"Suggestion generation failed: {e}")
        return []
