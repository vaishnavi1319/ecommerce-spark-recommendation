"""
=============================================================
Authentication Routes
POST /api/register
POST /api/login
POST /api/logout
GET  /api/me
=============================================================
"""

from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from backend.models.db_models import UserModel

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth_bp.route("/api/register", methods=["POST"])
@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    name  = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    pwd   = data.get("password", "")

    if not name or not email or not pwd:
        return jsonify({"error": "Name, email, and password are required"}), 400
    if len(pwd) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    pw_hash = bcrypt.generate_password_hash(pwd).decode("utf-8")
    try:
        user = UserModel().create(name, email, pw_hash)
        token = create_access_token(identity=str(user["user_id"]))
        return jsonify({
            "message": "Registration successful",
            "token": token,
            "access_token": token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            }
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@auth_bp.route("/api/login", methods=["POST"])
@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data  = request.get_json()
    email = data.get("email", "").strip().lower()
    pwd   = data.get("password", "")

    user = UserModel().find_by_email(email)
    if not user or not bcrypt.check_password_hash(user["password"], pwd):
        return jsonify({"error": "Invalid email or password"}), 401

    UserModel().update_last_login(user["user_id"])
    token = create_access_token(identity=str(user["user_id"]))
    return jsonify({
        "message": "Login successful",
        "token": token,
        "access_token": token,
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }
    }), 200


@auth_bp.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = UserModel().find_by_id(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.pop("password", None)
    user.pop("_id", None)
    return jsonify(user), 200
