import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import gc
import cv2
import glob
import time
import uuid
import shutil
import subprocess

import torch
from flask import Flask, render_template, request
from ultralytics import YOLO

# -----------------------------
# Torch Settings
# -----------------------------
torch.set_num_threads(1)

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024   # 100 MB upload

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# -----------------------------
# Load YOLO Model
# -----------------------------
MODEL_PATH = "best.pt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

model = YOLO(MODEL_PATH)
model.to("cpu")

IMG_SIZE = 640
CONFIDENCE = 0.50

# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# Prediction
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:

        return render_template(
            "index.html",
            error="Please select a file."
        )

    file = request.files["image"]

    if file.filename == "":

        return render_template(
            "index.html",
            error="No file selected."
        )

    extension = os.path.splitext(file.filename)[1].lower()

    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    ]

    video_extensions = [
        ".mp4",
        ".avi",
        ".mov",
        ".mkv"
    ]

    filename = (
        str(uuid.uuid4()) + extension
    )

    input_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(input_path)

    # =====================================
    # IMAGE DETECTION
    # =====================================

    if extension in image_extensions:

        start_time = time.time()

        with torch.no_grad():

            results = model.predict(
                source=input_path,
                imgsz=IMG_SIZE,
                conf=CONFIDENCE,
                verbose=False
            )

        result = results[0]

        annotated_image = result.plot()

        pothole_count = len(result.boxes)

        confidence = 0

        if pothole_count > 0:

            confidence = max(

                float(box.conf[0])

                for box in result.boxes

            ) * 100

        processing_time = round(

            time.time() - start_time,

            2

        )

        output_name = "result_" + filename

        output_path = os.path.join(

            RESULT_FOLDER,

            output_name

        )

        saved = cv2.imwrite(output_path, annotated_image)

        if not saved:
            return render_template(
                "index.html",
                error="Unable to save output image."
            )

        try:

            os.remove(input_path)

        except Exception as e:
            print(e)

        del annotated_image
        del result
        del results

        gc.collect()

        return render_template(
    "index.html",
    image="results/" + output_name,
    potholes=pothole_count,
    confidence=round(confidence,2),
    time=processing_time,
    scroll_to_results=True
)

    # =====================================
    # VIDEO DETECTION
    # =====================================

    elif extension in video_extensions:
        start_time = time.time()

        with torch.no_grad():

            results = model.predict(
                source=input_path,
                imgsz=IMG_SIZE,
                conf=CONFIDENCE,
                save=True,
                project="runs/detect",
                name="output",
                exist_ok=True,
                verbose=False
            )

        # Automatically find YOLO output folder
        output_folders = glob.glob("**/output", recursive=True)

        if not output_folders:
            return render_template(
                "index.html",
                error="YOLO output folder not found."
            )

        latest_predict = max(output_folders, key=os.path.getmtime)

        print("YOLO Output Folder:", latest_predict)

        video_files = []

        for ext in ("*.mp4", "*.avi", "*.mov", "*.mkv"):

            video_files.extend(
                glob.glob(os.path.join(latest_predict, ext))
            )

        print("Detected Videos:", video_files)

        if not video_files:

            try:
                os.remove(input_path)
            except Exception as e:
                print(e)

            return render_template(

                "index.html",

                error="Video detection failed."

            )

        detected_video = max(video_files, key=os.path.getmtime)

        temp_video = os.path.join(

            RESULT_FOLDER,

            "temp_video.mp4"

        )

        shutil.copy2(

            detected_video,

            temp_video

        )

        final_video = os.path.join(

            RESULT_FOLDER,

            "result_video.mp4"

        )

        ffmpeg = subprocess.run(

            [

                "ffmpeg",

                "-y",

                "-i",

                temp_video,

                "-c:v",

                "libx264",

                "-pix_fmt",

                "yuv420p",

                "-c:a",

                "aac",

                final_video

            ],

            capture_output=True,

            text=True

        )

        if ffmpeg.returncode != 0:
            print(ffmpeg.stderr)
            return render_template(
                "index.html",
                error="Video conversion failed."
            )

        if not os.path.exists(final_video):
            return render_template(
                "index.html",
                error="Converted video not found."
            )

        processing_time = round(

            time.time() - start_time,

            2

        )

        try:

            os.remove(temp_video)

        except Exception as e:
            print(e)
        try:

            os.remove(input_path)

        except Exception as e:
            print(e)

        try:

            shutil.rmtree(

                latest_predict,

                ignore_errors=True

            )

        except Exception as e:
            print(e)

        gc.collect()

        return render_template(
    "index.html",
    video="results/" + output_name,
    potholes=pothole_count,
    confidence=round(confidence,2),
    time=processing_time,
    scroll_to_results=True
)

    # =====================================
    # UNSUPPORTED FILE
    # =====================================

    else:

        try:
            os.remove(input_path)
        except Exception as e:
            print(e)

        return render_template(

            "index.html",

            error="Unsupported file type."

        )


# =====================================
# RUN APP
# =====================================

if __name__ == "__main__":

    port = int(

        os.environ.get(

            "PORT",

            7860

        )

    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=True

    )