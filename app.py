from flask import Flask, request, render_template, send_file, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv(".env.Azure")

# Azure Blob Storage configuration
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# Use home directory for upload path
UPLOAD_FOLDER = os.path.expanduser("/home/site/wwwroot/upload_file_share")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists during initialization
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    blobs_list = container_client.list_blobs()
    files = [blob.name for blob in blobs_list]
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

            # Upload to Azure Blob Storage
            blob_client = container_client.get_blob_client(filename)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data)

            return jsonify(message="File successfully uploaded"), 200
        except (IOError, SyntaxError) as e:
            return jsonify(message="Invalid image file"), 400
    return jsonify(message="Invalid file type"), 400


@app.route("/show_images")
def show_images():
    blobs_list = container_client.list_blobs()
    images = [
        {
            "filename": blob.name,
            "creation_time": blob.creation_time.strftime("%Y-%m-%d %H:%M:%S"),
            "size": f"{blob.size / (1024 * 1024):.2f} MiB",
        }
        for blob in blobs_list
    ]
    return render_template("images.html", images=images)


@app.route("/delete_image", methods=["DELETE"])
def delete_image():
    data = request.get_json()
    filenames = data["filenames"]
    for filename in filenames:
        blob_client = container_client.get_blob_client(filename)
        blob_client.delete_blob()
    return jsonify(message="Image(s) deleted successfully"), 200


@app.route("/images/<filename>")
def send_image(filename):
    blob_client = container_client.get_blob_client(filename)
    download_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    return send_file(download_file_path)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
