import os
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import logging
from app_shopify.views import shopify_bp
from config import DefaultConfig
from flask_migrate import Migrate
from common.extensions import db

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s:%(lineno)d %(threadName)s : %(message)s")

log_level = {
    'DEBUG': logging.DEBUG,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO
}

logging.getLogger('werkzeug').setLevel(log_level[os.getenv('LOG_LEVEL',
                                                           'INFO')])

app = Flask(__name__, instance_relative_config=False)
app.config.from_object(DefaultConfig)
CORS(app)

# Blueprints
app.register_blueprint(shopify_bp)

# Liveness probe
@app.route('/health')
def health():
    return jsonify({"status": 200, "message": "It's alive!"})


# Database
db.init_app(app)
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
