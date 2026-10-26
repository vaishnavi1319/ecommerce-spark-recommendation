"""
=============================================================
Spark ALS Recommendation Model
=============================================================
Implements Collaborative Filtering using Apache Spark MLlib
ALS (Alternating Least Squares) algorithm.

ALS Overview:
  • Matrix Factorisation technique
  • Decomposes user-product interaction matrix into latent factors
  • Handles implicit and explicit feedback
  • Scales to millions of users and products (distributed)

Spark MLlib ALS Parameters:
  • rank        : Number of latent factors (default 10)
  • maxIter     : Maximum iterations (default 10)
  • regParam    : Regularisation parameter to avoid overfitting
  • coldStartStrategy : "drop" or "nan" for unseen users/items

Cold Start Handling:
  • New users → Popular products + Top rated products
  • New products → Not shown in recommendations
=============================================================
"""

import os
import time
import json
import shutil
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.types import FloatType


MODEL_BASE_PATH = os.getenv("MODEL_PATH", "data/processed/als_model")
RECS_PATH       = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "recommendations.json"
STATS_PATH      = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "model_stats.json"
POPULAR_PATH    = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "popular_products.json"


class SparkRecommendationModel:
    """
    Trains and serves an ALS-based collaborative filtering model
    using Apache Spark MLlib.
    """

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.model: ALSModel = None
        self.training_stats: dict = {}
        self._all_products_cache: list = []
        self._popular_products_cache: list = []

    # ──────────────────────────────────────────────────────
    # MODEL TRAINING
    # ──────────────────────────────────────────────────────
    def train(
        self,
        interaction_matrix: DataFrame,
        rank: int = 10,
        max_iter: int = 10,
        reg_param: float = 0.1,
        test_fraction: float = 0.2,
    ) -> dict:
        """
        Train the ALS model on the user-product interaction matrix.

        Args:
            interaction_matrix : DataFrame with (user_id, product_id, score)
            rank               : Number of latent factors
            max_iter           : Number of ALS iterations
            reg_param          : L2 regularisation coefficient
            test_fraction      : Fraction held out for evaluation

        Returns:
            dict with training statistics
        """
        print(f"[ALS] Starting model training")
        print(f"[ALS]   Rank      : {rank}")
        print(f"[ALS]   MaxIter   : {max_iter}")
        print(f"[ALS]   RegParam  : {reg_param}")

        start = time.time()

        # Split into train / test sets
        train_df, test_df = interaction_matrix.randomSplit(
            [1.0 - test_fraction, test_fraction], seed=42
        )

        # Cache training set (used multiple times during ALS iterations)
        train_df = train_df.cache()

        # Build the ALS model
        als = ALS(
            rank=rank,
            maxIter=max_iter,
            regParam=reg_param,
            userCol="user_id",
            itemCol="product_id",
            ratingCol="score",
            coldStartStrategy="drop",   # drop NaN predictions for unseen pairs
            nonnegative=True,           # scores must be non-negative
            implicitPrefs=False,
        )

        # Train
        self.model = als.fit(train_df)

        # Evaluate on test set
        rmse = self._evaluate(test_df)

        elapsed = time.time() - start

        total_pairs = interaction_matrix.count()
        total_users = interaction_matrix.select("user_id").distinct().count()
        total_products = interaction_matrix.select("product_id").distinct().count()

        self.training_stats = {
            "status": "trained",
            "rank": rank,
            "max_iter": max_iter,
            "reg_param": reg_param,
            "total_pairs": int(total_pairs),
            "total_users": int(total_users),
            "total_products": int(total_products),
            "rmse": round(float(rmse), 4) if rmse else None,
            "training_time_seconds": round(elapsed, 2),
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(f"[ALS] Training complete in {elapsed:.2f}s")
        print(f"[ALS] RMSE on test set: {rmse:.4f}" if rmse else "[ALS] RMSE: N/A")
        self._save_stats()
        return self.training_stats

    def _evaluate(self, test_df: DataFrame) -> float:
        """Evaluate model RMSE on the test set."""
        try:
            predictions = self.model.transform(test_df)
            evaluator = RegressionEvaluator(
                metricName="rmse",
                labelCol="score",
                predictionCol="prediction"
            )
            predictions_clean = predictions.filter(F.col("prediction").isNotNull())
            if predictions_clean.count() == 0:
                return None
            return evaluator.evaluate(predictions_clean)
        except Exception as e:
            print(f"[ALS] Evaluation error: {e}")
            return None

    # ──────────────────────────────────────────────────────
    # RECOMMENDATION GENERATION
    # ──────────────────────────────────────────────────────
    def generate_recommendations(
        self,
        clean_df: DataFrame,
        top_n: int = 10,
        num_users: int = None,
    ) -> dict:
        """
        Generate top-N recommendations for all users.
        Stores results as a dictionary keyed by user_id.

        Args:
            clean_df  : Full cleaned interaction DataFrame (for product info lookup)
            top_n     : Number of recommendations per user
            num_users : Limit to this many users (None = all)

        Returns:
            dict { user_id: [list of recommended product_ids] }
        """
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        print(f"[ALS] Generating top-{top_n} recommendations for all users...")
        start = time.time()

        # recommendForAllUsers returns (user_id, recommendations[{product_id, rating}])
        recs_df = self.model.recommendForAllUsers(top_n)

        # Explode to flat format
        recs_flat = recs_df.select(
            F.col("user_id"),
            F.explode("recommendations").alias("rec")
        ).select(
            F.col("user_id"),
            F.col("rec.product_id").alias("product_id"),
            F.round(F.col("rec.rating"), 4).alias("rec_score"),
        )

        # Build product info lookup (product_id → name, category, price)
        product_info = (
            clean_df
            .select("product_id", "product_name", "category", "price")
            .dropDuplicates(["product_id"])
        )
        self._cache_all_products(product_info)

        # Join recommendations with product info
        recs_with_info = recs_flat.join(product_info, on="product_id", how="left")

        # Convert to Python dict
        rows = recs_with_info.collect()
        recommendations = {}
        for row in rows:
            uid = str(row["user_id"])
            if uid not in recommendations:
                recommendations[uid] = []
            recommendations[uid].append({
                "product_id": row["product_id"],
                "product_name": row["product_name"] or "Unknown",
                "category": row["category"] or "General",
                "price": float(row["price"] or 0),
                "rec_score": float(row["rec_score"] or 0),
            })

        elapsed = time.time() - start
        print(f"[ALS] Recommendations generated for {len(recommendations):,} users in {elapsed:.2f}s")

        # Cache popular products for cold-start
        self._cache_popular_products(clean_df)

        # Save recommendations to disk
        self._save_recommendations(recommendations)

        return recommendations

    def _cache_all_products(self, product_info_df: DataFrame):
        self._all_products_cache = [row.asDict() for row in product_info_df.collect()]

    def _cache_popular_products(self, df: DataFrame):
        """Cache popular products for cold-start new users and save to disk."""
        popular = (
            df.groupBy("product_id", "product_name", "category", "price")
            .agg(
                F.count("*").alias("interaction_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating"),
            )
            .orderBy(F.desc("interaction_count"))
            .limit(20)
        )
        self._popular_products_cache = [row.asDict() for row in popular.collect()]
        # Save to disk so the Flask backend can load it without a running SparkSession
        try:
            os.makedirs(os.path.dirname(POPULAR_PATH) if os.path.dirname(POPULAR_PATH) else ".", exist_ok=True)
            with open(POPULAR_PATH, "w", encoding="utf-8") as f:
                json.dump(self._popular_products_cache, f)
            print(f"[ALS] Popular products saved: {POPULAR_PATH}")
        except Exception as e:
            print(f"[ALS] Could not save popular products: {e}")

    # ──────────────────────────────────────────────────────
    # COLD-START HANDLER
    # ──────────────────────────────────────────────────────
    def get_cold_start_recommendations(self, category: str = None) -> list:
        """
        Return recommendations for a new user with no history.
        Falls back to popular/top-rated products.

        Args:
            category : If provided, filter by this category

        Returns:
            List of product dicts
        """
        products = self._popular_products_cache or []
        if category and products:
            filtered = [p for p in products if p.get("category") == category]
            if filtered:
                return filtered[:10]
        return products[:10]

    # ──────────────────────────────────────────────────────
    # MODEL PERSISTENCE
    # ──────────────────────────────────────────────────────
    def save_model(self, path: str = None):
        """Save the trained ALS model to disk."""
        if self.model is None:
            raise RuntimeError("No trained model to save.")
        path = path or MODEL_BASE_PATH
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            self.model.save(path)
            print(f"[ALS] Model saved to: {path}")
        except Exception as e:
            print(f"[ALS] Note: Spark model directory persistence skipped on Windows (HADOOP_HOME/winutils not required for serving recommendations): {e}")

    def load_model(self, path: str = None):
        """Load a previously saved ALS model from disk."""
        path = path or MODEL_BASE_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"No saved model at: {path}")
        self.model = ALSModel.load(path)
        print(f"[ALS] Model loaded from: {path}")

    def _save_recommendations(self, recs: dict):
        """Persist recommendations dict to JSON for the backend to read."""
        os.makedirs(os.path.dirname(RECS_PATH) if os.path.dirname(RECS_PATH) else ".", exist_ok=True)
        with open(RECS_PATH, "w", encoding="utf-8") as f:
            json.dump(recs, f)
        print(f"[ALS] Recommendations saved: {RECS_PATH}")

    def _save_stats(self):
        """Persist training stats to JSON."""
        os.makedirs(os.path.dirname(STATS_PATH) if os.path.dirname(STATS_PATH) else ".", exist_ok=True)
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.training_stats, f, indent=2)

    def load_recommendations(self) -> dict:
        """Load saved recommendations from JSON file."""
        if not os.path.exists(RECS_PATH):
            return {}
        with open(RECS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_stats(self) -> dict:
        """Load saved model stats from JSON file."""
        if not os.path.exists(STATS_PATH):
            return {"status": "not_trained"}
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_trained(self) -> bool:
        return self.model is not None or os.path.exists(MODEL_BASE_PATH) or os.path.exists(RECS_PATH)
