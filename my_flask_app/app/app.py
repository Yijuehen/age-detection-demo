from flask import Flask
import os


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config/config.py")

    from .routes import main

    app.register_blueprint(main)

    return app


if __name__ == "__main__":
    app = create_app()
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    if not os.path.exists(app.config["OUTPUT_FOLDER"]):
        os.makedirs(app.config["OUTPUT_FOLDER"])
    app.run(debug=True)
