"""
=============================================================
Recommendation Routes — Spark MLlib & Real-Time Personalization
=============================================================
GET  /api/recommendations/popular
GET  /api/recommendations/cart
GET  /api/recommendations/wishlist
GET  /api/recommendations/me
GET  /api/recommendations/<user_id>
GET  /api/recommendations/user/<user_id>
GET  /api/recommendations/similar/<product_id>
GET  /api/recommendations/category/<category>
=============================================================
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.recommendation_service import (
    get_recommendations_for_user,
    get_cart_recommendations,
    get_wishlist_recommendations,
    get_popular_products,
    get_category_recommendations,
    get_similar_products,
)
from backend.models.db_models import ProductModel

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/api/recommendations/popular", methods=["GET"])
def get_popular():
    limit = int(request.args.get("limit", 10))
    recs = get_popular_products(limit=limit)
    return jsonify({
        "popular": recs,
        "recommendations": recs,
        "products": recs,
        "count": len(recs),
        "source": "popular",
        "type": "cold_start",
    }), 200


@recommendations_bp.route("/api/recommendations/cart", methods=["GET", "POST"])
def get_cart_recs():
    """Contextual recommendations for the Cart Drawer & Checkout."""
    limit = int(request.args.get("limit", 4))
    ids_param = request.args.get("ids", "")
    cart_ids = [int(i.strip()) for i in ids_param.split(",") if i.strip().isdigit()]

    if request.method == "POST" and not cart_ids:
        data = request.get_json() or {}
        cart_ids = data.get("ids", []) or data.get("product_ids", [])

    recs = get_cart_recommendations(cart_ids, limit=limit)
    return jsonify({
        "recommendations": recs,
        "count": len(recs),
        "type": "cart_contextual",
        "source": "spark_hybrid",
    }), 200


@recommendations_bp.route("/api/recommendations/wishlist", methods=["GET", "POST"])
def get_wishlist_recs():
    """Contextual recommendations based on saved Wishlist items."""
    limit = int(request.args.get("limit", 4))
    ids_param = request.args.get("ids", "")
    wish_ids = [int(i.strip()) for i in ids_param.split(",") if i.strip().isdigit()]

    if request.method == "POST" and not wish_ids:
        data = request.get_json() or {}
        wish_ids = data.get("ids", []) or data.get("product_ids", [])

    recs = get_wishlist_recommendations(wish_ids, limit=limit)
    return jsonify({
        "recommendations": recs,
        "count": len(recs),
        "type": "wishlist_contextual",
        "source": "spark_hybrid",
    }), 200


@recommendations_bp.route("/api/recommendations/me", methods=["GET"])
@jwt_required(optional=True)
def get_my_recommendations():
    uid = get_jwt_identity()
    limit = int(request.args.get("limit", 12))
    recs = get_recommendations_for_user(uid or 1001, limit=limit)
    return jsonify({
        "user_id": uid or 1001,
        "recommendations": recs,
        "count": len(recs),
        "source": "personalized" if recs else "cold_start",
    }), 200


@recommendations_bp.route("/api/recommendations/category/<string:category>", methods=["GET"])
def get_by_category(category: str):
    limit = int(request.args.get("limit", 10))
    recs = get_category_recommendations(category, limit=limit)
    return jsonify({
        "category": category,
        "recommendations": recs,
        "count": len(recs),
    }), 200


@recommendations_bp.route("/api/recommendations/similar/<product_id>", methods=["GET"])
def get_similar(product_id):
    limit = int(request.args.get("limit", 6))
    recs = get_similar_products(product_id, limit=limit)
    return jsonify({
        "product_id": product_id,
        "similar_products": recs,
        "recommendations": recs,
        "count": len(recs),
    }), 200


@recommendations_bp.route("/api/recommendations/<user_id>", methods=["GET"])
@recommendations_bp.route("/api/recommendations/user/<user_id>", methods=["GET"])
@jwt_required(optional=True)
def get_user_recommendations(user_id):
    if str(user_id).lower() == "popular":
        return get_popular()
    if str(user_id).lower() == "cart":
        return get_cart_recs()
    if str(user_id).lower() == "wishlist":
        return get_wishlist_recs()
    if str(user_id).lower() == "me":
        try:
            uid = get_jwt_identity()
            if uid:
                user_id = uid
        except Exception:
            pass

    limit = int(request.args.get("limit", 10))
    recs = get_recommendations_for_user(user_id, limit=limit)
    return jsonify({
        "user_id": user_id,
        "recommendations": recs,
        "count": len(recs),
        "type": "personalized" if recs else "cold_start",
        "source": "personalized" if recs else "cold_start",
    }), 200
