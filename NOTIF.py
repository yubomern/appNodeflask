from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def connect():
    print("Client connected")

def notify_stock(data):
    socketio.emit("stock_update", data)

if __name__ == "__main__":
    socketio.run(app, port=5000)