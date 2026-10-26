"""
=============================================================
Admin Routes
GET  /api/analytics
POST /api/train-model
GET  /api/model-status
GET  /api/admin/users
=============================================================
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.db_models import UserModel, InteractionModel, ProductModel, RecommendationModel
from backend.services.spark_service import (
    start_training,
    get_training_status,
    get_analytics,
    get_model_stats,
)
import os

admin_bp = Blueprint("admin", __name__)


def require_admin():
    """Helper: verify JWT and that user has admin role."""
    uid = int(get_jwt_identity())
    user = UserModel().find_by_id(uid)
    if not user or user.get("role") != "admin":
        return None, jsonify({"error": "Admin access required"}), 403
    return user, None, 200


@admin_bp.route("/api/analytics", methods=["GET"])
@jwt_required()
def get_analytics_route():
    analytics = get_analytics()

    # Merge live DB counts
    try:
        analytics["live_users"]        = UserModel().count()
        analytics["live_products"]     = ProductModel().count()
        analytics["live_interactions"] = InteractionModel().count()
        analytics["live_recommendations"] = RecommendationModel().count()
    except Exception:
        pass

    return jsonify(analytics), 200


@admin_bp.route("/api/analytics/public", methods=["GET"])
@admin_bp.route("/api/analytics/summary", methods=["GET"])
def get_analytics_public():
    """Public analytics endpoint — no JWT required.
    Returns Spark analytics for the dashboard page.
    Live DB counts are included when available.
    """
    analytics = get_analytics()

    # Merge live DB counts when available
    try:
        analytics["live_users"]        = UserModel().count()
        analytics["live_products"]     = ProductModel().count()
        analytics["live_interactions"] = InteractionModel().count()
        analytics["live_recommendations"] = RecommendationModel().count()
    except Exception:
        pass

    # Include model stats
    try:
        analytics["model_stats"] = get_model_stats()
    except Exception:
        pass

    return jsonify(analytics), 200


@admin_bp.route("/api/train-model", methods=["POST"])
@jwt_required()
def train_model():
    _, err, code = require_admin()
    if err:
        return err, code

    data      = request.get_json() or {}
    use_large = data.get("use_large", False)
    rank      = int(data.get("rank", 10))
    max_iter  = int(data.get("max_iter", 10))
    reg_param = float(data.get("reg_param", 0.1))

    started = start_training(
        use_large=use_large,
        rank=rank,
        max_iter=max_iter,
        reg_param=reg_param,
    )

    if not started:
        return jsonify({"message": "Training already in progress", "status": "running"}), 200

    return jsonify({"message": "Training started", "status": "running"}), 202


@admin_bp.route("/api/model-status", methods=["GET"])
@admin_bp.route("/api/model-stats", methods=["GET"])
@jwt_required(optional=True)
def model_status():
    status = get_training_status()
    stats  = get_model_stats()
    return jsonify({
        "training": status,
        "model": stats,
    }), 200


@admin_bp.route("/api/admin/users", methods=["GET"])
@jwt_required()
def list_users():
    _, err, code = require_admin()
    if err:
        return err, code

    users = UserModel().list_all(limit=100)
    for u in users:
        u.pop("_id", None)
        u.pop("password", None)
        u["created_at"] = str(u.get("created_at", ""))
        u["last_login"]  = str(u.get("last_login", ""))
    return jsonify({"users": users, "total": len(users)}), 200


@admin_bp.route("/api/admin/generate-dataset", methods=["POST"])
@jwt_required()
def generate_dataset():
    """Generate the dataset and seed MongoDB products."""
    _, err, code = require_admin()
    if err:
        return err, code

    import threading

    def _generate():
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from scripts.generate_large_dataset import generate_dataset as gen, generate_products_csv, ALL_PRODUCTS
        generate_products_csv()
        gen(num_users=5000, num_interactions=100_000, verbose=True)

        # Seed products into MongoDB
        product_model = ProductModel()
        products_to_insert = []
        for p in ALL_PRODUCTS:
            products_to_insert.append({
                "product_id": p["product_id"],
                "product_name": p["product_name"],
                "category": p["category"],
                "price": p["price"],
                "description": f"Premium {p['product_name']} — quality assured.",
                "avg_rating": 4.0,
                "stock": 100,
            })
        product_model.upsert_many(products_to_insert)

    thread = threading.Thread(target=_generate, daemon=True)
    thread.start()

    return jsonify({"message": "Dataset generation started in background"}), 202
