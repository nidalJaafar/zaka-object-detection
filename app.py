import logging
import os

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
    file = res[1]
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
        return False ,jsonify({'error': 'No image provided'}), 400

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

    if file_size > 1024 * 1024:
        log.info(f"Image too large: {file_size} bytes")
        return False, jsonify({'error': 'Image too large'}), 400
    return True, file


def main():
    log.info("Starting flask server")
    app.run("0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
