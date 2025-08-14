import io
import logging
import os

from PIL import Image
from flask import Flask, jsonify, request, send_file, render_template

from model.model import Model

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
app = Flask(__name__)
model = Model()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/v1/predict", methods=["POST"])
def predict():
    log.info("Received request")
    res = validate_request()
    if len(res) == 3:
        return res[1], res[2]
    file = resize(res[1])
    try:
        log.info("Starting prediction")
        prediction = model.predict(file)
    except:
        log.error("Error during prediction")
        return jsonify({'error': 'Error during prediction'}), 500

    log.info("Prediction done")
    return send_file(
        prediction,
        mimetype='image/jpeg',
        download_name='predicted_image.jpg'
    )

def validate_request():
    log.info("Validating request")

    if 'image' not in request.files:
        log.info("No image provided")
        return False, jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        log.info("No image provided")
        return False, jsonify({'error': 'No image provided'}), 400

    if file.mimetype != "image/jpeg":
        log.info("Invalid mimetype")
        log.info(f"Received mimetype: {file.mimetype}")
        return False, jsonify({'error': 'Invalid image format'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > 5 * 1024 * 1024:
        log.info(f"Image too large: {file_size} bytes")
        return False, jsonify({'error': 'Image too large'}), 400
    return True, file


def resize(file):
    log.info("Resizing image")
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes))

    if img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size
    quality = 95

    while True:
        temp_img = img.copy()

        if width > 1200 or height > 1200:
            temp_img.thumbnail((width, height), Image.Resampling.LANCZOS)

        img_io = io.BytesIO()
        temp_img.save(img_io, format='JPEG', quality=quality, optimize=True)

        img_size = img_io.tell()
        log.info(f"Image size: {img_size} bytes")

        if img_size <= 1024 * 1024:
            img_io.seek(0)
            return img_io

        if quality > 50:
            quality -= 10
        else:
            width = int(width * 0.9)
            height = int(height * 0.9)
            quality = 85

            if width < 100 or height < 100:
                img_io.seek(0)
                return img_io


def main():
    log.info("Starting flask server")
    app.run("0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
