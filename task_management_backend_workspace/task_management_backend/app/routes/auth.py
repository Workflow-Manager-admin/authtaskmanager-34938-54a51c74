from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..models import db, User
import jwt
import datetime
from functools import wraps
from marshmallow import Schema, fields

SECRET_KEY = "replace_this_with_env_var"

blp = Blueprint(
    "Auth",
    __name__,
    url_prefix="/auth",
    description="Authentication routes"
)


class UserRegisterSchema(Schema):
    username = fields.String(required=True, description="Username")
    password = fields.String(required=True, description="Password")


class UserLoginSchema(Schema):
    username = fields.String(required=True, description="Username")
    password = fields.String(required=True, description="Password")


class TokenResponseSchema(Schema):
    access_token = fields.String(description="JWT access token")


def token_required(f):
    """Decorator to require token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT passed in Authorization header as Bearer token
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            abort(401, message="Token is missing.")
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                abort(401, message="Invalid token user.")
        except Exception as e:
            abort(401, message="Token is invalid: " + str(e))
        return f(current_user, *args, **kwargs)
    return decorated


# PUBLIC_INTERFACE
@blp.route("/signup")
class Signup(MethodView):
    """Endpoint for user registration"""

    @blp.arguments(UserRegisterSchema)
    @blp.response(201, TokenResponseSchema)
    def post(self, user_data):
        """Register a new user"""
        if User.query.filter_by(username=user_data["username"]).first():
            abort(409, message="Username already exists.")
        user = User(username=user_data["username"])
        user.set_password(user_data["password"])
        db.session.add(user)
        db.session.commit()

        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return {"access_token": token}


# PUBLIC_INTERFACE
@blp.route("/login")
class Login(MethodView):
    """Endpoint for user login"""

    @blp.arguments(UserLoginSchema)
    @blp.response(200, TokenResponseSchema)
    def post(self, credentials):
        """Authenticate and log in a user"""
        user = User.query.filter_by(username=credentials["username"]).first()
        if user and user.check_password(credentials["password"]):
            token = jwt.encode({
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm="HS256")
            return {"access_token": token}
        abort(401, message="Invalid username or password.")
