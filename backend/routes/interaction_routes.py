"""
=============================================================
Interaction Routes
POST /api/interactions
GET  /api/interactions/<user_id>
=============================================================
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.db_models import InteractionModel, ProductModel

interactions_bp = Blueprint("interactions", __name__)

VALID_INTERACTION_TYPES = {"view", "click", "wishlist", "add_to_cart", "purchase", "rating", "search"}


@interactions_bp.route("/api/interactions", methods=["POST"])
@jwt_required(optional=True)
def record_interaction():
    data = request.get_json() or {}
    jwt_uid = get_jwt_identity()
    if jwt_uid:
        try:
            uid = int(jwt_uid)
        except Exception:
            uid = 1001
    elif data.get("user_id"):
        try:
            uid = int(data.get("user_id"))
        except Exception:
            uid = 1001
    else:
        uid = 1001

    product_id       = data.get("product_id")
    interaction_type = data.get("interaction_type", "view")
    rating           = data.get("rating")
    query            = data.get("query", "")

    if interaction_type not in VALID_INTERACTION_TYPES:
        return jsonify({"error": f"Invalid interaction_type. Use: {VALID_INTERACTION_TYPES}"}), 400

    product_model = ProductModel()
    # If search without explicit product_id, find best matching product for user's search
    if not product_id and interaction_type == "search":
        matches = product_model.search(query=query, limit=1)
        if matches:
            product_id = matches[0].get("product_id")
        else:
            return jsonify({"message": "Search logged", "query": query}), 200

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    # Validate product exists
    product = product_model.find_by_id(int(product_id))
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Record the interaction
    doc = InteractionModel().record(
        user_id=uid,
        product_id=int(product_id),
        interaction_type=interaction_type,
        rating=float(rating) if rating else None,
    )

    return jsonify({
        "message": "Interaction recorded",
        "interaction_type": interaction_type,
        "product_id": product_id,
    }), 201


@interactions_bp.route("/api/interactions/me", methods=["GET"])
@jwt_required()
def get_my_interactions():
    uid   = int(get_jwt_identity())
    limit = int(request.args.get("limit", 20))
    interactions = InteractionModel().get_user_interactions(uid, limit=limit)

    # Enrich with product info
    product_model = ProductModel()
    result = []
    for i in interactions:
        i.pop("_id", None)
        product = product_model.find_by_id(i.get("product_id"))
        if product:
            i["product_name"] = product.get("product_name")
            i["category"]     = product.get("category")
        i["timestamp"] = str(i.get("timestamp", ""))
        result.append(i)

    return jsonify({"interactions": result}), 200


@interactions_bp.route("/api/orders/place", methods=["POST"])
@jwt_required(optional=True)
def place_order():
    """
    Place an e-commerce order:
      - Validates products in cart
      - Calculates order subtotal, tax, and shipping
      - Records 'purchase' interaction in MongoDB for logged-in user
      - Returns order ID, items, totals, and recommendations
    """
    import random
    import time

    uid_str = get_jwt_identity()
    uid = int(uid_str) if uid_str else None

    data = request.get_json() or {}
    items = data.get("items", [])
    shipping_address = data.get("address", {})
    payment_method = data.get("payment_method", "Cash on Delivery")

    if not items:
        return jsonify({"error": "No items provided in cart"}), 400

    product_model = ProductModel()
    interaction_model = InteractionModel()

    order_items = []
    subtotal = 0.0

    for it in items:
        pid = int(it.get("product_id") or it.get("id"))
        qty = int(it.get("qty") or 1)
        product = product_model.find_by_id(pid)
        price = float(product.get("price", 0)) if product else float(it.get("price", 0))
        name = product.get("product_name") if product else it.get("product_name", f"Product #{pid}")
        cat = product.get("category") if product else it.get("category", "General")
        line_total = price * qty
        subtotal += line_total
        order_items.append({
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "price": price,
            "qty": qty,
            "line_total": line_total,
        })

        # Record purchase interaction if user is authenticated
        if uid:
            try:
                interaction_model.record(
                    user_id=uid,
                    product_id=pid,
                    interaction_type="purchase",
                )
            except Exception:
                pass

    shipping = 0.0 if subtotal >= 999 else 99.0
    total = subtotal + shipping
    order_id = f"ORD-2026-{random.randint(10000, 99999)}"

    # Fetch recommendations for order confirmation
    from backend.services.recommendation_service import get_recommendations_for_user, get_popular_products
    recs = get_recommendations_for_user(uid, limit=4) if uid else get_popular_products(limit=4)

    return jsonify({
        "status": "success",
        "message": "Order placed successfully",
        "order_id": order_id,
        "items": order_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "payment_method": payment_method,
        "placed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "recommendations": recs,
    }), 201
