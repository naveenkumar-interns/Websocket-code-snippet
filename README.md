# 📦 FastAPI WebSocket + SQLite Live DB Updates

This project demonstrates how to use **FastAPI** and **WebSockets** to broadcast **real-time database changes** to connected clients.

It uses:
- **FastAPI** as the backend web framework
- **SQLite** as a temporary database
- **WebSockets** for pushing updates to all connected clients
- A **background polling task** to detect manual database edits (e.g., through an external DB editor)

---

## 🚀 Features

- Add new items via HTTP API
- Update existing items via HTTP API
- Automatically broadcast all changes to connected WebSocket clients
- Detect manual DB edits (via lightweight polling) and notify clients
- Simple HTML frontend for viewing live updates

---

## 🛠 Requirements

- Python 3.9+ recommended
- Dependencies:
  ```bash
  pip install fastapi uvicorn
  ```

---

## ▶️ Running the App

1. **Start the server**:

   ```bash
   python main.py
   ```

   The app runs by default at `http://localhost:8000`.

2. **Open the frontend**:

   In your browser, go to:

   ```
   http://localhost:8000
   ```

   You should see **"Waiting for DB updates..."**.

3. **Add a new item** (via HTTP GET request):

   ```
   http://localhost:8000/add/ItemName/ItemValue
   ```

   Example:

   ```
   http://localhost:8000/add/Test/123
   ```

4. **Update an item**:

   ```
   http://localhost:8000/update/{item_id}/{new_value}
   ```

   Example:

   ```
   http://localhost:8000/update/1/456
   ```

5. **Manual DB edits**:

   If you open `test.db` in a DB editor and manually change a row, all connected clients will be updated automatically within \~2 seconds (due to polling).

---

## 🧠 How It Works

1. **Clients** connect via a WebSocket (`/ws`).
2. **HTTP endpoints** (`/add` and `/update`) modify the database.
3. After every DB change, the server **broadcasts** the latest data to all WebSocket clients.
4. A **background polling task** (`poll_db_changes`) periodically checks for manual DB changes and broadcasts if differences are detected.

---

## 🧪 Example Output (Browser)

```
DB Changed: [(1, 'Test', '123')]
DB Changed: [(1, 'Test', '456')]
```

---
