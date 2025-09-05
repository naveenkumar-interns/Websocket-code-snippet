import asyncio
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- Database setup (SQLite) ---
DB_FILE = "test.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        value TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_all_items():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, value FROM items")
    rows = c.fetchall()
    conn.close()
    return rows

def update_item(item_id: int, new_value: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE items SET value=? WHERE id=?", (new_value, item_id))
    conn.commit()
    conn.close()

def insert_item(name: str, value: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO items (name, value) VALUES (?, ?)", (name, value))
    conn.commit()
    conn.close()
    return c.lastrowid

# --- WebSocket clients ---
clients = []

@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>Live DB Updates</title></head>
    <body>
        <h1>📦 DB Live Updates</h1>
        <pre id="output">Waiting for DB updates...</pre>
        <script>
            const ws = new WebSocket(`ws://${location.host}/ws`);
            ws.onmessage = (event) => {
                document.getElementById("output").innerText = event.data;
            };
        </script>
    </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # not used, but keeps connection open
    except WebSocketDisconnect:
        clients.remove(websocket)


@app.get("/add/{name}/{value}")
async def add_item(name: str, value: str):
    item_id = insert_item(name, value)
    # Immediately push the latest state
    rows = get_all_items()
    message = f"DB Changed: {rows}"
    await broadcast(message)
    return {"status": "added", "id": item_id, "rows": rows}

@app.get("/update/{item_id}/{new_value}")
async def update_item_api(item_id: int, new_value: str):
    update_item(item_id, new_value)
    # Immediately push the latest state
    rows = get_all_items()
    message = f"DB Changed: {rows}"
    await broadcast(message)
    return {"status": "updated", "rows": rows}

async def broadcast(message: str):
    to_remove = []
    for ws in clients:
        try:
            await ws.send_text(message)
        except:
            to_remove.append(ws)
    for ws in to_remove:
        clients.remove(ws)

# --- Background task to detect manual DB changes ---
last_snapshot = None
async def poll_db_changes():
    global last_snapshot
    while True:
        rows = get_all_items()
        snapshot = tuple(rows)
        if snapshot != last_snapshot:
            last_snapshot = snapshot
            await broadcast(f"DB Changed: {rows}")
        await asyncio.sleep(2)  # check every 2 seconds

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(poll_db_changes())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
