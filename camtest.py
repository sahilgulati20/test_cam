from flask import Flask, Response, request
from flask_socketio import SocketIO
import cv2, base64, threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

PUBLIC_RENDER = "https://test-cam-75ql.onrender.com/upload"

# ========== CLOUD SIDE ==========
@app.route("/")
def home():
    return """
    <h2>LIVE CAMERA</h2>
    <img id="v" width="720">
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
    var s = io();
    s.on("frame", d=>{
        document.getElementById("v").src="data:image/jpeg;base64,"+d;
    });
    </script>
    """

@app.route("/upload", methods=["POST"])
def upload():
    socketio.emit("frame", base64.b64encode(request.data).decode())
    return "OK"

# ========== LOCAL CAMERA PUSH ==========
def camera_sender():
    cam = cv2.VideoCapture(0)
    cam.set(3,640)
    cam.set(4,480)
    while True:
        ret, frame = cam.read()
        _, jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY),50])
        import requests
        requests.post(PUBLIC_RENDER, data=jpg.tobytes())

# ========== START ==========
if __name__ == "__main__":
    threading.Thread(target=camera_sender).start()
    socketio.run(app, host="0.0.0.0", port=10000)
