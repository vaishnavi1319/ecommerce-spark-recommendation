"""
=============================================================
SparkStore — Local Execution Entry Point
=============================================================
Launches the full E-Commerce Product Recommendation application:
  1. Validates Java & Python runtime
  2. Auto-starts local MongoDB or connects to MongoDB Atlas
  3. Preloads Spark recommendation & popular cache
  4. Seeds default admin user and product catalogue
  5. Launches Flask HTTP server on host:port
=============================================================
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles to prevent cp1252 encoding crashes
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

from dotenv import load_dotenv
load_dotenv()


def check_java():
    """Verify Java runtime for Apache Spark."""
    java_home = os.getenv("JAVA_HOME")
    if not java_home:
        # Check standard paths
        candidates = [
            r"C:\Program Files\Java\jdk-19",
            r"C:\Program Files\Java\jdk-17",
            r"C:\Program Files\Eclipse Adoptium\jdk-17",
            "/usr/lib/jvm/java-17-openjdk-amd64",
            "/usr/lib/jvm/default-java",
        ]
        for c in candidates:
            if os.path.exists(c):
                os.environ["JAVA_HOME"] = c
                java_home = c
                break

    if java_home and os.path.exists(java_home):
        print(f"[Java] Detected JAVA_HOME: {java_home}")
    else:
        print("[Java] Note: JAVA_HOME not detected. Spark training may need JAVA_HOME set in .env")


def check_data():
    """Ensure raw dataset and processed cache files exist."""
    raw_csv = os.getenv("DATASET_PATH", "data/raw/ecommerce_interactions.csv")
    if not os.path.exists(raw_csv):
        print(f"[Data] Base dataset not found at {raw_csv}. Generating...")
        try:
            from scripts.generate_large_dataset import main as gen_main
            sys.argv = ["generate_large_dataset.py", "--interactions", "10000", "--output", raw_csv]
            gen_main()
            print("[Data] Dataset generated successfully.")
        except Exception as e:
            print(f"[Data] Could not auto-generate dataset: {e}")


def main():
    print("=" * 65)
    print("SparkStore -- E-Commerce Recommendation Using Apache Spark")
    print("BDA Framework : Apache Spark MLlib ALS")
    print("Cloud Platform: AWS S3 + AWS EC2")
    print("=" * 65)

    check_java()
    check_data()

    from backend.app import create_app, seed_admin, seed_products
    from backend.services.recommendation_service import load_recommendations_cache

    print("[App] Initializing application...")
    app = create_app()

    # Preload recommendations cache
    print("[RecService] Loading recommendation cache...")
    load_recommendations_cache()

    # Seed Admin & Products in MongoDB
    try:
        seed_admin()
        seed_products()
    except Exception as e:
        print(f"[DB] MongoDB note: {e}")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))

    print("\n" + "=" * 65)
    print(f"Application is running!")
    print(f"-> Storefront: http://localhost:{port}")
    print(f"-> Products  : http://localhost:{port}/products.html")
    print(f"-> For You   : http://localhost:{port}/recommendations.html")
    print(f"-> BI Metrics: http://localhost:{port}/dashboard.html")
    print(f"-> Admin Hub : http://localhost:{port}/admin.html")
    print("=" * 65 + "\n")

    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
