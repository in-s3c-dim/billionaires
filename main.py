from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()

# --- Setup an in-memory DB for demo ---
conn = sqlite3.connect(":memory:", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
cur.execute("INSERT INTO users (username, password) VALUES ('admin', 'secret')")
cur.execute("INSERT INTO users (username, password) VALUES ('alice', 'wonderland')")
conn.commit()


# 1. CODE INJECTION (using eval) --------------------------------
@app.get("/code_injection")
def code_injection(expr: str = Query(..., description="Python expression to eval")):
    # ⚠️ Very unsafe: directly evaluates user input
    try:
        result = eval(expr)  # <-- Code injection vulnerability
    except Exception as e:
        result = f"Error: {e}"
    return {"expr": expr, "result": result}


# 2. XSS (reflected) --------------------------------------------
@app.get("/xss", response_class=HTMLResponse)
def xss(request: Request, name: str = "guest"):
    # ⚠️ Vulnerable: directly injects user input into HTML
    html = f"""
    <html>
        <body>
            <h1>Hello {name}!</h1>
            <p>Try adding ?name=<script>alert('XSS')</script></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


# 3. SQL INJECTION ----------------------------------------------
@app.get("/login")
def login(username: str, password: str):
    # ⚠️ Vulnerable: unsafely builds SQL query with user input
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    try:
        result = cur.execute(query).fetchall()
    except Exception as e:
        return {"error": str(e), "query": query}
    return {"query": query, "result": result}