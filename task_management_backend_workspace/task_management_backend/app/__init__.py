from flask import Flask
from flask_cors import CORS
from .routes.health import blp as health_blp
from flask_smorest import Api
from .models import db
from .routes.auth import blp as auth_blp
from .routes.tasks import blp as tasks_blp


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Configuration for SQLite (in-memory for now, can be changed to file)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


db.init_app(app)
api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(tasks_blp)


@app.before_first_request
def create_tables():
    """Create database tables on first request."""
    db.create_all()
