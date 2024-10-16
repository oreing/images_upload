from flask import Flask, request, render_template, send_file, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime

app = Flask(__name__)

# Use home directory for upload path
UPLOAD_FOLDER = os.path.expanduser("/home/site/wwwroot/upload")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists during initialization
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("home.html", files=files, upload_folder=os.path.abspath(UPLOAD_FOLDER))


@app.route("/get_modified_time")
def get_modified_time():
    modified_time = datetime.fromtimestamp(os.path.getmtime(__file__))
    formatted_modified_time = modified_time.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"modified_time": formatted_modified_time})


@app.route("/get_current_time")
def get_current_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"current_time": current_time})


@app.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify(message="No file part"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(message="No selected file"), 400
    if file and allowed_file(file.filename):
        try:
            image = Image.open(file)
            image.verify()
            file.seek(0)  # Reset file pointer to beginning

            filename = secure_filename(f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            return jsonify(message="File successfully uploaded"), 200
        except (IOError, SyntaxError) as e:
            return jsonify(message="Invalid image file"), 400
    return jsonify(message="Invalid file type"), 400


@app.route("/show_images")
def show_images():
    images = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            images.append({"filename": filename, "creation_time": creation_time})
    return render_template("images.html", images=images)


@app.route("/delete_image", methods=["DELETE"])
def delete_image():
    data = request.get_json()
    filenames = data["filenames"]
    for filename in filenames:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    return jsonify(message="Image(s) deleted successfully"), 200


@app.route("/images/<filename>")
def send_image(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(os.path.abspath(file_path))
    else:
        return jsonify(message="File does not exist"), 404


if __name__ == "__main__":
    app.run(debug=True)
