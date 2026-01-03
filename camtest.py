from flask import Flask, Response, request
import cv2, threading, time, requests

PUBLIC_URL = "https://livecam.onrender.com/upload"   # we will change later

app = Flask(__name__)
latest = None

@app.route("/")
def home():
    return "<h2>LIVE CAMERA</h2><img src='/video' width='700'>"

@app.route("/upload", methods=["POST"])
def upload():
    global latest
    latest = request.data
    return "OK"

@app.route("/video")
def video():
    def gen():
        global latest
        while True:
            if latest:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + latest + b"\r\n")
            time.sleep(0.04)
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

def camera_sender():
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        _, img = cv2.imencode(".jpg", frame)
        requests.post(PUBLIC_URL, data=img.tobytes())

if __name__ == "__main__":
    threading.Thread(target=camera_sender).start()
    app.run(host="0.0.0.0", port=10000)
