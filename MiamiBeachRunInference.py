import cv2
import numpy as np
from flask import Flask, Response
from rfdetr import RFDETRMedium
from rfdetr.util.coco_classes import COCO_CLASSES
import supervision as sv
import subprocess

# ---------------------------
# Flask app
# ---------------------------
app = Flask(__name__)

model = RFDETRMedium(
    checkpoint_path="data/vehicle_dataset_training_output/checkpoint_best_ema.pth",
    device="cuda"  # or "cpu"
)
name_to_id = {v: k for k, v in COCO_CLASSES.items()}
target_classes = ["car", "truck", "bus", "motorcycle"]
valid_ids = [name_to_id[c] for c in target_classes]

# ---------------------------
# Open Stream
# ---------------------------
yt_url = "https://www.youtube.com/watch?v=kGn_MI-CZTk"
stream_url = subprocess.check_output(
    ["yt-dlp", "-f", "best", "-g", yt_url],
    text=True
).strip()
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    raise RuntimeError("Cannot open YouTube stream")

# ---------------------------
# Video generator
# ---------------------------
def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB for model
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run inference
        detections = model.predict(frame_rgb, threshold=0.5)

        # Filter detections
        mask = np.isin(detections.class_id, valid_ids)
        detections = detections[mask]

        # Labels
        labels = [
            f"{COCO_CLASSES[cid]} {conf:.2f}"
            for cid, conf in zip(detections.class_id, detections.confidence)
        ]

        # Annotate
        annotated = frame.copy()
        annotated = sv.BoxAnnotator().annotate(annotated, detections)
        annotated = sv.LabelAnnotator(text_color=sv.Color.BLACK).annotate(annotated, detections, labels)

        # Encode to JPEG
        ret, buffer = cv2.imencode(".jpg", annotated)
        frame = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# ---------------------------
# Flask route
# ---------------------------
@app.route("/video")
def video():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
    return """
    <html>
    <head><title>RFDETR Live Stream</title></head>
    <body>
        <h1>RFDETR Inference on YouTube Stream</h1>
        <img src="/video" width="800">
    </body>
    </html>
    """

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
