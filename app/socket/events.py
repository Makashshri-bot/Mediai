from flask_socketio import emit
from app import socketio


@socketio.on("connect")
def handle_connect():
    emit("status", {"message": "Connected to MediAI live updates"})


@socketio.on("join_room")
def handle_join_room(data):
    emit("status", {"message": f"Joined {data.get('room', 'general')}"})
