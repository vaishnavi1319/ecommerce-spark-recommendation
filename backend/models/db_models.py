"""
=============================================================
Database Models — MongoDB Collections
=============================================================
Defines helper classes for each MongoDB collection.
Uses PyMongo directly (no ORM) for clarity in a B.Tech project.
=============================================================
"""

from datetime import datetime
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

load_dotenv()

_client: MongoClient = None
_db = None


import subprocess
import time

def _try_start_mongod():
    """Attempt to start mongod automatically if local instance isn't running."""
    mongod_candidates = [
        r"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe",
    ]
    for exe in mongod_candidates:
        if os.path.exists(exe):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_dir = os.path.join(base_dir, "data", "mongodb")
            os.makedirs(db_dir, exist_ok=True)
            try:
                flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
                subprocess.Popen(
                    [exe, "--dbpath", db_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=flags,
                )
                time.sleep(2)
                return True
            except Exception:
                pass
    return False


def get_db():
    """Return the MongoDB database instance (singleton) with auto-start."""
    global _client, _db
    if _db is None:
        uri     = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DB", "ecommerce_spark")
        try:
            _client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            _client.admin.command("ping")
        except Exception:
            if "localhost" in uri or "127.0.0.1" in uri:
                _try_start_mongod()
            _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _db = _client[db_name]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    """Create indexes for performance."""
    try:
        db.users.create_index("email", unique=True)
        db.users.create_index("user_id", unique=True)
        db.products.create_index("product_id", unique=True)
        db.interactions.create_index([("user_id", ASCENDING), ("product_id", ASCENDING)])
        db.interactions.create_index("timestamp", DESCENDING)
        db.recommendations.create_index("user_id", unique=True)
    except Exception:
        pass  # Indexes may already exist


# ────────────────────────────────────────────────────────────
# USER MODEL
# ────────────────────────────────────────────────────────────
class UserModel:
    def __init__(self):
        self.col: Collection = get_db().users

    def create(self, name: str, email: str, password_hash: str, role: str = "user") -> dict:
        existing = self.col.find_one({"email": email})
        if existing:
            raise ValueError("Email already registered")

        # Auto-increment user_id
        last = self.col.find_one(sort=[("user_id", DESCENDING)])
        new_id = (last["user_id"] + 1) if last else 2001

        doc = {
            "user_id": new_id,
            "name": name,
            "email": email,
            "password": password_hash,
            "role": role,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "category_preferences": [],
        }
        self.col.insert_one(doc)
        return doc

    def find_by_email(self, email: str) -> dict:
        return self.col.find_one({"email": email})

    def find_by_id(self, user_id: int) -> dict:
        return self.col.find_one({"user_id": user_id})

    def update_last_login(self, user_id: int):
        self.col.update_one(
            {"user_id": user_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    def update_preferences(self, user_id: int, categories: list):
        self.col.update_one(
            {"user_id": user_id},
            {"$set": {"category_preferences": categories}}
        )

    def count(self) -> int:
        return self.col.count_documents({})

    def list_all(self, limit: int = 100) -> list:
        return list(self.col.find({}, {"password": 0}).limit(limit))


# ────────────────────────────────────────────────────────────
# PRODUCT MODEL
# ────────────────────────────────────────────────────────────
class ProductModel:
    def __init__(self):
        self.col: Collection = get_db().products

    def upsert_many(self, products: list):
        """Bulk upsert product records from the dataset."""
        for p in products:
            self.col.update_one(
                {"product_id": p["product_id"]},
                {"$set": p},
                upsert=True,
            )

    def find_by_id(self, product_id: int) -> dict:
        return self.col.find_one({"product_id": product_id})

    def find_by_ids(self, product_ids: list) -> list:
        int_ids = []
        for pid in product_ids:
            try:
                int_ids.append(int(pid))
            except Exception:
                pass
        if not int_ids:
            return []
        return list(self.col.find({"product_id": {"$in": int_ids}}))

    def search(self, query: str = "", category: str = "", limit: int = 20, skip: int = 0) -> list:
        filters = {}
        if query:
            filters["product_name"] = {"$regex": query, "$options": "i"}
        if category:
            filters["category"] = category
        return list(self.col.find(filters).skip(skip).limit(limit))

    def count(self, category: str = "") -> int:
        filters = {"category": category} if category else {}
        return self.col.count_documents(filters)

    def get_categories(self) -> list:
        return self.col.distinct("category")

    def list_all(self, limit: int = 200) -> list:
        return list(self.col.find({}).limit(limit))


# ────────────────────────────────────────────────────────────
# INTERACTION MODEL
# ────────────────────────────────────────────────────────────
INTERACTION_SCORES = {
    "view": 1,
    "click": 2,
    "search": 2,
    "wishlist": 3,
    "add_to_cart": 4,
    "purchase": 5,
}


class InteractionModel:
    def __init__(self):
        self.col: Collection = get_db().interactions

    def record(self, user_id: int, product_id: int, interaction_type: str,
               rating: float = None) -> dict:
        score = INTERACTION_SCORES.get(interaction_type, 1)
        doc = {
            "user_id": user_id,
            "product_id": product_id,
            "interaction_type": interaction_type,
            "interaction_score": score,
            "rating": rating,
            "timestamp": datetime.utcnow(),
        }
        self.col.insert_one(doc)
        return doc

    def get_user_interactions(self, user_id: int, limit: int = 50) -> list:
        return list(
            self.col.find({"user_id": user_id})
            .sort("timestamp", DESCENDING)
            .limit(limit)
        )

    def get_user_product_ids(self, user_id: int) -> list:
        """Return list of product_ids this user has interacted with."""
        docs = self.col.find({"user_id": user_id}, {"product_id": 1})
        return list({d["product_id"] for d in docs})

    def count(self) -> int:
        return self.col.count_documents({})

    def get_popular_products(self, limit: int = 10) -> list:
        pipeline = [
            {"$group": {
                "_id": "$product_id",
                "interaction_count": {"$sum": 1},
                "avg_rating": {"$avg": "$rating"},
            }},
            {"$sort": {"interaction_count": -1}},
            {"$limit": limit},
        ]
        return list(self.col.aggregate(pipeline))


# ────────────────────────────────────────────────────────────
# RECOMMENDATION MODEL
# ────────────────────────────────────────────────────────────
class RecommendationModel:
    def __init__(self):
        self.col: Collection = get_db().recommendations

    def upsert(self, user_id: int, products: list):
        """Save/update recommendations for a user."""
        self.col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "recommendations": products,
                    "generated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

    def get(self, user_id: int) -> dict:
        return self.col.find_one({"user_id": user_id})

    def bulk_upsert_from_dict(self, recs_dict: dict):
        """Bulk save all recommendations from the ALS output dict."""
        from pymongo import UpdateOne
        ops = []
        for uid_str, products in recs_dict.items():
            ops.append(UpdateOne(
                {"user_id": int(uid_str)},
                {"$set": {
                    "user_id": int(uid_str),
                    "recommendations": products,
                    "generated_at": datetime.utcnow(),
                }},
                upsert=True,
            ))
        if ops:
            self.col.bulk_write(ops)
        print(f"[DB] Saved recommendations for {len(ops):,} users")

    def count(self) -> int:
        return self.col.count_documents({})
