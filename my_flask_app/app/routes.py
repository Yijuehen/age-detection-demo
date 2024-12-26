from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    send_from_directory,
)
import re
import os
from werkzeug.utils import secure_filename
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from test_age import predict_age
from test_video_age import predict_video_age

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            if filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg"}:
                result_filename = predict_age(file_path)
                result_type = "image"
            elif filename.rsplit(".", 1)[1].lower() == "mp4":
                result_filename = predict_video_age(file_path)
                result_type = "video"

            # print(result_filename.split("/app")[1])
            # print(re.split("/app", result_filename)[1])
            return render_template(
                "index.html",
                result=result_filename.split("/app")[1],
                result_type=result_type,
            )

    return render_template("index.html")


@main.route("/output/<filename>")
def output_file(filename):
    print("@" + filename)
    print(current_app.config["OUTPUT_FOLDER"])
    return send_from_directory(current_app.config["OUTPUT_FOLDER"], filename)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "mp4",
    }
