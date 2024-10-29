import os

import uvicorn
from fastapi import FastAPI
from fastapi_socketio import SocketManager

app = FastAPI()

# Initialize Socket.IO with FastAPI
socket_manager = SocketManager(app=app, mount_location='/socket.io')

@app.get("/")
async def index():
    return {"message": "Socket.IO server running!"}

# Socket.IO event listener for "new-order" messages
@socket_manager.on('new-order')
async def handle_new_order(sid, data):
    await socket_manager.emit('new-order', data, broadcast=True, include_self=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    uvicorn.run(app, host="0.0.0.0", port=port)
