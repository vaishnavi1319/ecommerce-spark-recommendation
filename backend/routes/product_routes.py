"""
=============================================================
Product Routes
GET  /api/products
GET  /api/products/<product_id>
GET  /api/categories
GET  /api/popular-products
=============================================================
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.db_models import ProductModel, InteractionModel

products_bp = Blueprint("products", __name__)


@products_bp.route("/api/products", methods=["GET"])
def get_products():
    query    = request.args.get("q", "")
    category = request.args.get("category", "")
    page     = int(request.args.get("page", 1))
    limit    = int(request.args.get("limit", 20))
    skip     = (page - 1) * limit

    product_model = ProductModel()
    products = product_model.search(query=query, category=category, limit=limit, skip=skip)
    total    = product_model.count(category=category)

    # Sanitize MongoDB _id
    for p in products:
        p.pop("_id", None)

    return jsonify({
        "products": products,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }), 200


@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    product = ProductModel().find_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    product.pop("_id", None)
    return jsonify(product), 200


@products_bp.route("/api/categories", methods=["GET"])
def get_categories():
    categories = ProductModel().get_categories()
    return jsonify({"categories": categories}), 200


@products_bp.route("/api/popular-products", methods=["GET"])
def get_popular():
    limit = int(request.args.get("limit", 10))
    from backend.services.recommendation_service import get_popular_products
    popular = get_popular_products(limit=limit)
    return jsonify({"products": popular}), 200
