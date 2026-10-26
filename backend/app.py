"""
=============================================================
Main Flask Application
E-Commerce Product Recommendation Using Apache Spark
=============================================================
Entry point for the backend web server.

Architecture:
  Browser → Flask API → MongoDB  (for user/product data)
                     → Spark JSON Cache  (for recommendations)
                     → Spark Pipeline   (on-demand training)

Cloud Architecture:
  User → EC2 (Flask) → MongoDB Atlas / RDS
                    → S3 (raw dataset) → Spark on EC2
=============================================================
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

if "JAVA_HOME" not in os.environ and os.path.exists(r"C:\Program Files\Java\jdk-19"):
    os.environ["JAVA_HOME"] = r"C:\Program Files\Java\jdk-19"

# ── Import route blueprints ───────────────────────────────
from backend.routes.auth_routes import auth_bp, bcrypt
from backend.routes.product_routes import products_bp
from backend.routes.interaction_routes import interactions_bp
from backend.routes.recommendation_routes import recommendations_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.cloud_routes import cloud_bp


def create_app() -> Flask:
    """Application factory."""

    # Flask serves static frontend files from the project root
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"),
        static_url_path=None,
    )

    # ── Configuration ────────────────────────────────────
    app.config["SECRET_KEY"]             = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JWT_SECRET_KEY"]         = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # No expiry for demo

    # ── Extensions ───────────────────────────────────────
    CORS(app, origins="*", supports_credentials=True)
    bcrypt.init_app(app)
    JWTManager(app)

    # ── Register Blueprints ──────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cloud_bp)

    # ── Serve Frontend ───────────────────────────────────
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_page(path):
        """Serve any frontend HTML page or static asset."""
        if path.startswith("api/"):
            return jsonify({"error": "Endpoint not found"}), 404
        if not path:
            return send_from_directory(app.static_folder, "index.html")
        full_path = os.path.join(app.static_folder, path)
        if os.path.isfile(full_path):
            return send_from_directory(app.static_folder, path)
        if os.path.isfile(full_path + ".html"):
            return send_from_directory(app.static_folder, path + ".html")
        return send_from_directory(app.static_folder, "index.html")

    # ── Health Check ─────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "app": "E-Commerce Recommendation using Apache Spark",
            "version": "1.0.0",
        }), 200

    # ── Error Handlers ───────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    return app


def seed_admin():
    """Create default admin user if not present."""
    from backend.models.db_models import UserModel
    from flask_bcrypt import generate_password_hash

    user_model = UserModel()
    admin_email = os.getenv("ADMIN_EMAIL", "admin@sparkrec.com")
    admin_pwd   = os.getenv("ADMIN_PASSWORD", "Admin@123")

    existing = user_model.find_by_email(admin_email)
    if not existing:
        pw_hash = generate_password_hash(admin_pwd).decode("utf-8")
        user_model.create(
            name="System Administrator",
            email=admin_email,
            password_hash=pw_hash,
            role="admin",
        )
        print(f"[App] Admin user created: {admin_email}")
    else:
        print(f"[App] Admin user already exists: {admin_email}")


def seed_products():
    """Seed product catalogue into MongoDB from the dataset generator."""
    from backend.models.db_models import ProductModel
    product_model = ProductModel()
    if product_model.count() > 0:
        print(f"[App] Products already seeded ({product_model.count()} products)")
        return

    try:
        from scripts.generate_large_dataset import ALL_PRODUCTS, generate_products_csv
        generate_products_csv()
        products_to_insert = []
        for p in ALL_PRODUCTS:
            products_to_insert.append({
                "product_id": p["product_id"],
                "product_name": p["product_name"],
                "category": p["category"],
                "price": p["price"],
                "description": f"Premium quality {p['product_name']}. "
                               f"Trusted by thousands of customers across India.",
                "avg_rating": 4.1,
                "stock": 50,
            })
        product_model.upsert_many(products_to_insert)
        print(f"[App] Seeded {len(products_to_insert)} products into MongoDB")
    except Exception as e:
        print(f"[App] Could not seed products: {e}")


def load_recommendations_cache():
    """Pre-load Spark recommendations into memory cache and sync to MongoDB."""
    try:
        from backend.services.recommendation_service import load_recommendations_cache as load_cache, sync_recommendations_to_mongo
        load_cache()
        sync_recommendations_to_mongo()
    except Exception as e:
        print(f"[App] Could not load recommendations cache: {e}")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        seed_admin()
        seed_products()
        load_recommendations_cache()

    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"\n{'='*60}")
    print(f"  E-Commerce Recommendation System — Apache Spark")
    print(f"  Running at: http://{host}:{port}")
    print(f"  Admin: http://{host}:{port}/admin.html")
    print(f"{'='*60}\n")

    app.run(host=host, port=port, debug=os.getenv("FLASK_DEBUG", "True") == "True")
