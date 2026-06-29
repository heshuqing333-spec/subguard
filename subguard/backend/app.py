from flask import Flask, jsonify

from config import Config
from extensions import db
from routes.cancel_guides import cancel_guides_bp
from routes.imports import imports_bp
from routes.stats import stats_bp
from routes.subscriptions import subscriptions_bp
from services.database import init_database


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(cancel_guides_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(subscriptions_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "subguard-backend"})

    init_database(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
