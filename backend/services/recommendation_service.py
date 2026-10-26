"""
=============================================================
Recommendation Service — Real-Time Hybrid ML Engine
=============================================================
Combines:
  1. Apache Spark MLlib ALS Matrix Factorization (collaborative filtering)
  2. Real-Time Dynamic User Interaction Tracking (views, clicks, cart, wishlist, purchases, ratings)
  3. Category Affinity & Content Similarity
  4. Contextual Recommenders (Cart "Bought Together", Wishlist "Matches", Similar Products)
=============================================================
"""

import json
import os
from collections import defaultdict
from backend.models.db_models import (
    RecommendationModel,
    ProductModel,
    InteractionModel,
    INTERACTION_SCORES,
)

RECS_JSON = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "recommendations.json"
POPULAR_CACHE_PATH = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "popular_products.json"

# In-memory caches (loaded once at startup)
_recommendations_cache: dict = {}
_popular_products_cache: list = []


def load_recommendations_cache():
    """Load Spark-generated recommendations and popular products into memory."""
    global _recommendations_cache, _popular_products_cache
    if os.path.exists(RECS_JSON):
        try:
            with open(RECS_JSON, "r", encoding="utf-8") as f:
                _recommendations_cache = json.load(f)
            print(f"[RecService] Loaded recommendations for {len(_recommendations_cache):,} users")
        except Exception as e:
            print(f"[RecService] Warning loading recommendations.json: {e}")
            _recommendations_cache = {}
    else:
        _recommendations_cache = {}

    # Load popular products cache for cold-start
    if os.path.exists(POPULAR_CACHE_PATH):
        try:
            with open(POPULAR_CACHE_PATH, "r", encoding="utf-8") as f:
                _popular_products_cache = json.load(f)
            print(f"[RecService] Loaded {len(_popular_products_cache)} popular products for cold-start")
        except Exception as e:
            print(f"[RecService] Warning loading popular_products.json: {e}")
            _popular_products_cache = []
    else:
        _popular_products_cache = []


def get_recommendations_for_user(user_id, limit: int = 10, context_pids: list = None) -> list:
    """
    Get real-time personalized recommendations for a user.

    Hybrid Strategy:
      1. Check user's live interaction history from MongoDB (views, searches, cart items, wishlist, ratings, purchases).
      2. If interactions exist:
         - Calculate category affinities (e.g. 70% Electronics, 30% Fashion).
         - Blend Spark ALS collaborative filtering recommendations with category-affinity boosted items.
         - Exclude already purchased items.
         - Rank by: 0.50 * ALS_Score + 0.35 * Category_Affinity + 0.15 * Normalized_Rating.
      3. If no live interactions but present in Spark ALS cache:
         - Return Spark ALS recommendations.
      4. If cold-start (new user):
         - Return popular and top-rated products across diverse categories.
    """
    user_str = str(user_id).strip()
    digits_only = "".join(ch for ch in user_str if ch.isdigit())
    uid_int = int(digits_only) if digits_only else None

    product_model = ProductModel()
    interaction_model = InteractionModel()

    # 1. Fetch live user interactions
    recent_interactions = []
    if uid_int:
        try:
            recent_interactions = interaction_model.get_user_interactions(uid_int, limit=40)
        except Exception:
            recent_interactions = []

    # 2. Extract user preferences and history
    interacted_pids = set()
    purchased_pids = set()
    category_weights = defaultdict(float)

    for item in recent_interactions:
        pid = item.get("product_id")
        if not pid:
            continue
        interacted_pids.add(pid)
        itype = item.get("interaction_type", "view")
        if itype == "purchase":
            purchased_pids.add(pid)

        base_score = float(item.get("interaction_score") or INTERACTION_SCORES.get(itype, 1.0))
        if item.get("rating"):
            base_score += float(item["rating"]) * 0.8

        prod = product_model.find_by_id(pid)
        if prod and prod.get("category"):
            category_weights[prod["category"]] += base_score

    # Factor in client context items (e.g., currently viewed or cart items)
    if context_pids:
        for cid in context_pids:
            try:
                prod = product_model.find_by_id(int(cid))
                if prod and prod.get("category"):
                    category_weights[prod["category"]] += 3.0
            except Exception:
                pass

    # 3. Fetch Spark ALS candidates
    als_candidates = []
    if user_str in _recommendations_cache:
        als_candidates = _recommendations_cache[user_str]
    elif digits_only and digits_only in _recommendations_cache:
        als_candidates = _recommendations_cache[digits_only]
    else:
        # Check MongoDB RecommendationModel
        try:
            rec_model = RecommendationModel()
            db_doc = rec_model.get(uid_int or user_id)
            if db_doc and db_doc.get("recommendations"):
                als_candidates = db_doc["recommendations"]
        except Exception:
            pass

    # 4. If user has category weights (active or returning user), generate dynamic personalized ranking
    if category_weights:
        max_weight = max(category_weights.values()) or 1.0
        candidate_map = {}

        # Add ALS candidates with affinity boost
        for rec in als_candidates:
            pid = rec.get("product_id")
            if pid in purchased_pids:
                continue
            cat = rec.get("category", "")
            cat_affinity = category_weights.get(cat, 0.0) / max_weight
            als_score = float(rec.get("rec_score", 3.0))
            blended_score = (0.50 * als_score) + (0.35 * (cat_affinity * 5.0)) + 0.5
            candidate_map[pid] = {
                "product_id": pid,
                "product_name": rec.get("product_name", "Product"),
                "category": cat,
                "price": float(rec.get("price", 0)),
                "avg_rating": float(rec.get("avg_rating", 4.2)),
                "rec_score": round(blended_score, 2),
                "rec_reason": f"Spark MLlib Pick for {cat}" if cat_affinity > 0.3 else "Spark ALS Match",
            }

        # Supplement with top items from user's favorite categories
        sorted_fav_cats = sorted(category_weights.keys(), key=lambda c: category_weights[c], reverse=True)
        for cat in sorted_fav_cats[:3]:
            cat_products = product_model.search(category=cat, limit=8)
            cat_affinity = category_weights[cat] / max_weight
            for p in cat_products:
                pid = p.get("product_id")
                if pid in purchased_pids or pid in candidate_map:
                    continue
                rating = float(p.get("avg_rating", 4.0))
                score = (0.60 * (cat_affinity * 5.0)) + (0.40 * rating)
                candidate_map[pid] = {
                    "product_id": pid,
                    "product_name": p.get("product_name", "Product"),
                    "category": cat,
                    "price": float(p.get("price", 0)),
                    "avg_rating": rating,
                    "rec_score": round(score, 2),
                    "rec_reason": f"Because you showed interest in {cat}",
                }

        # Sort all blended candidates by final recommendation score descending
        sorted_results = sorted(candidate_map.values(), key=lambda x: x["rec_score"], reverse=True)
        if sorted_results:
            return sorted_results[:limit]

    # 5. If user has ALS candidates but no real-time live interaction yet
    if als_candidates:
        results = []
        for r in als_candidates[:limit]:
            results.append({
                "product_id": r.get("product_id"),
                "product_name": r.get("product_name"),
                "category": r.get("category"),
                "price": float(r.get("price", 0)),
                "avg_rating": float(r.get("avg_rating", 4.2)),
                "rec_score": float(r.get("rec_score", 4.0)),
                "rec_reason": "Spark MLlib Collaborative Filtering",
            })
        return results

    # 6. Cold-start fallback (new user with no history yet)
    return get_popular_products(limit=limit)


def get_cart_recommendations(cart_product_ids: list, limit: int = 4) -> list:
    """
    Contextual Recommendations for the Shopping Cart Drawer:
    Recommends accessories and complementary items based on what's currently in the user's cart.
    """
    if not cart_product_ids:
        return get_popular_products(limit=limit)

    product_model = ProductModel()
    cart_pids_int = set()
    categories_in_cart = []

    for cid in cart_product_ids:
        try:
            c_int = int(cid)
            cart_pids_int.add(c_int)
            p = product_model.find_by_id(c_int)
            if p and p.get("category"):
                categories_in_cart.append(p["category"])
        except Exception:
            pass

    recommendations = []
    seen_pids = set(cart_pids_int)

    # Find complementary / category-aligned products
    for cat in set(categories_in_cart):
        prods = product_model.search(category=cat, limit=limit + 3)
        for p in prods:
            pid = p.get("product_id")
            if pid in seen_pids:
                continue
            seen_pids.add(pid)
            recommendations.append({
                "product_id": pid,
                "product_name": p.get("product_name"),
                "category": p.get("category"),
                "price": float(p.get("price", 0)),
                "avg_rating": float(p.get("avg_rating", 4.2)),
                "rec_score": 4.5,
                "rec_reason": f"Pairs well with items in your cart",
            })
            if len(recommendations) >= limit:
                break
        if len(recommendations) >= limit:
            break

    # If needed, fill remainder from popular products
    if len(recommendations) < limit:
        for p in get_popular_products(limit=limit * 2):
            if p.get("product_id") not in seen_pids:
                seen_pids.add(p.get("product_id"))
                p_copy = dict(p)
                p_copy["rec_reason"] = "Customer Favorite"
                recommendations.append(p_copy)
                if len(recommendations) >= limit:
                    break

    return recommendations[:limit]


def get_wishlist_recommendations(wishlist_product_ids: list, limit: int = 4) -> list:
    """
    Recommendations based on saved Wishlist items:
    Identifies similar and upgraded alternatives in wishlist categories.
    """
    if not wishlist_product_ids:
        return get_popular_products(limit=limit)

    product_model = ProductModel()
    wishlist_cats = []
    seen_pids = set()

    for wid in wishlist_product_ids:
        try:
            w_int = int(wid)
            seen_pids.add(w_int)
            p = product_model.find_by_id(w_int)
            if p and p.get("category"):
                wishlist_cats.append(p["category"])
        except Exception:
            pass

    recommendations = []
    for cat in set(wishlist_cats):
        prods = product_model.search(category=cat, limit=limit + 2)
        for p in prods:
            pid = p.get("product_id")
            if pid in seen_pids:
                continue
            seen_pids.add(pid)
            recommendations.append({
                "product_id": pid,
                "product_name": p.get("product_name"),
                "category": p.get("category"),
                "price": float(p.get("price", 0)),
                "avg_rating": float(p.get("avg_rating", 4.2)),
                "rec_score": 4.6,
                "rec_reason": f"Matches your wishlist interest in {cat}",
            })
            if len(recommendations) >= limit:
                break
        if len(recommendations) >= limit:
            break

    if len(recommendations) < limit:
        for p in get_popular_products(limit=limit * 2):
            if p.get("product_id") not in seen_pids:
                seen_pids.add(p.get("product_id"))
                recommendations.append(p)
                if len(recommendations) >= limit:
                    break

    return recommendations[:limit]


def get_similar_products(product_id, limit: int = 6) -> list:
    """Return similar products based on category, rating and price."""
    try:
        product_model = ProductModel()
        target = product_model.find_by_id(product_id)
        if not target:
            try:
                target = product_model.find_by_id(int(product_id))
            except Exception:
                pass

        if target and target.get("category"):
            category = target["category"]
            prods = product_model.search(category=category, limit=limit + 2)
            results = []
            for p in prods:
                if str(p.get("product_id")) == str(product_id):
                    continue
                results.append({
                    "product_id": p.get("product_id"),
                    "product_name": p.get("product_name"),
                    "category": p.get("category"),
                    "price": float(p.get("price", 0)),
                    "avg_rating": float(p.get("avg_rating", 4.0)),
                    "stock": p.get("stock", 50),
                    "description": p.get("description", ""),
                    "rec_score": 4.5,
                    "rec_reason": f"Similar product in {category}",
                })
            if results:
                return results[:limit]

        return get_popular_products(limit=limit)
    except Exception:
        return get_popular_products(limit=limit)


def get_popular_products(limit: int = 10) -> list:
    """
    Return popular products for cold-start / trending page.
    Uses the cached list from the Spark pipeline or live MongoDB aggregates.
    """
    if _popular_products_cache:
        results = []
        for p in _popular_products_cache[:limit]:
            p_copy = dict(p)
            p_copy.setdefault("rec_reason", "Trending Customer Favorite")
            results.append(p_copy)
        return results

    # Compute from MongoDB interactions if Spark cache not available
    try:
        interaction_model = InteractionModel()
        popular = interaction_model.get_popular_products(limit=limit)
        product_model = ProductModel()
        results = []
        for p in popular:
            product = product_model.find_by_id(p["_id"])
            if product:
                results.append({
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "price": float(product.get("price", 0)),
                    "interaction_count": p.get("interaction_count", 0),
                    "avg_rating": round(float(p.get("avg_rating") or 4.1), 2),
                    "rec_score": 4.0,
                    "rec_reason": "Popular Best Seller",
                })
        return results
    except Exception:
        return []


def get_category_recommendations(category: str, limit: int = 10) -> list:
    """Return top products in a specific category."""
    try:
        product_model = ProductModel()
        products = product_model.search(category=category, limit=limit)
        return [{
            "product_id": p["product_id"],
            "product_name": p["product_name"],
            "category": p["category"],
            "price": float(p.get("price", 0)),
            "avg_rating": float(p.get("avg_rating", 4.0)),
            "rec_score": 4.2,
            "rec_reason": f"Top pick in {category}",
        } for p in products]
    except Exception:
        return []


def sync_recommendations_to_mongo():
    """
    After Spark training, sync the JSON recommendations into MongoDB.
    This allows the backend to serve recs even from MongoDB queries.
    """
    load_recommendations_cache()
    if not _recommendations_cache:
        return 0

    rec_model = RecommendationModel()
    rec_model.bulk_upsert_from_dict(_recommendations_cache)
    return len(_recommendations_cache)
