"""
=============================================================
Spark Service — Backend bridge to Spark pipeline
=============================================================
Runs the Spark training pipeline in a background thread
so the Flask API doesn't block while training.
=============================================================
"""

import threading
import time
import json
import os
from datetime import datetime

# Global state
_training_status = {
    "status": "idle",          # idle | running | completed | failed
    "progress": 0,             # 0-100
    "message": "No training run yet",
    "started_at": None,
    "completed_at": None,
    "report": None,
}
_training_lock = threading.Lock()

ANALYTICS_CACHE = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "analytics.json"
MODEL_STATS     = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "model_stats.json"


def get_training_status() -> dict:
    with _training_lock:
        return dict(_training_status)


def _update_status(progress: int, message: str):
    """Thread-safe helper to update training status."""
    with _training_lock:
        _training_status["progress"] = progress
        _training_status["message"]  = message


def _run_pipeline(use_large: bool, rank: int, max_iter: int, reg_param: float):
    """Internal function executed in the training thread."""
    global _training_status

    with _training_lock:
        _training_status.update({
            "status":       "running",
            "progress":     3,
            "message":      "Initialising SparkSession...",
            "started_at":   datetime.utcnow().isoformat(),
            "completed_at": None,
            "report":       None,
        })

    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        _update_status(8,  "SparkSession initialised. Loading dataset...")

        # Import here so Spark starts inside the thread
        from spark.spark_session import get_spark_session, stop_spark
        from spark.data_loader    import SparkDataLoader
        from spark.preprocessing  import SparkPreprocessor
        from spark.analytics      import SparkAnalytics
        from spark.recommendation_model import SparkRecommendationModel
        import json

        # ── Stage 1: SparkSession ────────────────────────
        spark = get_spark_session()
        _update_status(12, "Loading dataset into Spark DataFrame...")

        # ── Stage 2: Data Loading ────────────────────────
        loader   = SparkDataLoader(spark)
        data_path = os.getenv("DATASET_PATH", "data/raw/ecommerce_interactions.csv")
        raw_df   = loader.load_from_local(data_path, use_large=use_large)
        load_stats = loader.get_load_stats()
        _update_status(25, f"Loaded {load_stats.get('record_count', 0):,} records. Preprocessing...")

        # ── Stage 3: Preprocessing ───────────────────────
        preprocessor  = SparkPreprocessor(spark)
        clean_df      = preprocessor.preprocess(raw_df)
        preprocess_stats = preprocessor.get_stats()
        _update_status(38, "Preprocessing complete. Running Spark SQL analytics...")

        # ── Stage 4: Analytics ───────────────────────────
        analytics        = SparkAnalytics(spark)
        analytics_report = analytics.run_full_analytics(clean_df)
        analytics_cache  = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "analytics.json"
        os.makedirs(os.path.dirname(analytics_cache), exist_ok=True)
        with open(analytics_cache, "w", encoding="utf-8") as f:
            json.dump(analytics_report, f, default=str)
        _update_status(52, "Analytics saved. Building user-product interaction matrix...")

        # ── Stage 5: Interaction Matrix ──────────────────
        matrix_df = preprocessor.build_interaction_matrix(clean_df)
        _update_status(62, "Matrix built. Training ALS recommendation model...")

        # ── Stage 6: ALS Training ────────────────────────
        rec_model      = SparkRecommendationModel(spark)
        training_stats = rec_model.train(
            interaction_matrix=matrix_df,
            rank=rank,
            max_iter=max_iter,
            reg_param=reg_param,
        )
        _update_status(78, f"ALS trained (RMSE: {training_stats.get('rmse','N/A')}). Generating recommendations...")

        # ── Stage 7: Generate Recommendations ───────────
        recommendations = rec_model.generate_recommendations(clean_df=clean_df, top_n=10)
        _update_status(88, f"Recommendations for {len(recommendations):,} users. Saving model...")

        # ── Stage 8: Save Model ──────────────────────────
        rec_model.save_model()

        stop_spark(spark)

        report = {
            "status":            "completed",
            "total_time_seconds": training_stats.get("training_time_seconds", 0),
            "completed_at":       datetime.utcnow().isoformat(),
            "stages": {
                "data_loading":              load_stats,
                "preprocessing":             preprocess_stats,
                "model_training":            training_stats,
                "recommendation_generation": {
                    "users_with_recommendations": len(recommendations),
                    "top_n": 10,
                },
            },
        }

        # ── Stage 9: Sync to MongoDB ─────────────────────
        _update_status(93, "Syncing recommendations to MongoDB...")
        from backend.services.recommendation_service import sync_recommendations_to_mongo
        sync_recommendations_to_mongo()

        with _training_lock:
            _training_status.update({
                "status":       "completed",
                "progress":     100,
                "message":      f"Training complete! {len(recommendations):,} users now have recommendations.",
                "completed_at": datetime.utcnow().isoformat(),
                "report":       report,
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        with _training_lock:
            _training_status.update({
                "status":       "failed",
                "progress":     0,
                "message":      str(e),
                "completed_at": datetime.utcnow().isoformat(),
            })


def start_training(
    use_large: bool = False,
    rank: int = 10,
    max_iter: int = 10,
    reg_param: float = 0.1,
) -> bool:
    """
    Start the Spark training pipeline in a background thread.

    Returns:
        True if started, False if already running
    """
    global _training_status
    with _training_lock:
        if _training_status["status"] == "running":
            return False

    thread = threading.Thread(
        target=_run_pipeline,
        args=(use_large, rank, max_iter, reg_param),
        daemon=True,
    )
    thread.start()
    return True


def get_analytics() -> dict:
    """Load the analytics report produced by Spark."""
    if os.path.exists(ANALYTICS_CACHE):
        with open(ANALYTICS_CACHE, "r") as f:
            return json.load(f)
    return {}


def get_model_stats() -> dict:
    """Load ALS model training statistics."""
    if os.path.exists(MODEL_STATS):
        with open(MODEL_STATS, "r") as f:
            return json.load(f)
    return {"status": "not_trained"}
