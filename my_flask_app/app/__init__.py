from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config/config.py')  # 配置路径

    # 延迟导入，防止循环导入
    from .routes import main
    app.register_blueprint(main)

    return app
