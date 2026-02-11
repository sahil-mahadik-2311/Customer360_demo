# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import random
import time

app = FastAPI()

# Simple in-memory list of connected clients
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"Client connected. Total: {len(connected_clients)}")
    
    try:
        # Optional: receive messages from client (subscription, auth, etc.)
        while True:
            data = await websocket.receive_text()
            print("Received from client:", data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"Client disconnected. Total: {len(connected_clients)}")

# Background task that pushes data to all clients
async def broadcast_loop():
    while True:
        if connected_clients:
            payload = {
                "timestamp": time.strftime("%H:%M:%S"),
                "price": round(random.uniform(50000, 70000), 2),
                "symbol": "BTCUSDT"
            }
            
            # Send to all connected clients
            for client in list(connected_clients):
                try:
                    await client.send_json(payload)
                except Exception:
                    connected_clients.remove(client)
                    
        await asyncio.sleep(2)  # broadcast every 2 seconds

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_loop())

# Optional: simple HTML test page
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>Live Data</h1>
        <div id="messages"></div>
        <script>
            const ws = new WebSocket(`ws://${location.host}/ws`);
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const msg = `${data.timestamp} | ${data.symbol}: $${data.price}`;
                document.getElementById('messages').innerHTML += `<p>${msg}</p>`;
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)