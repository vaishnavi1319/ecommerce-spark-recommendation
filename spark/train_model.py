"""
=============================================================
Spark Training Pipeline — Full Orchestration
=============================================================
Orchestrates the complete Spark pipeline:

  1. Start SparkSession
  2. Load data (local or S3)
  3. Preprocess with Spark
  4. Run Spark SQL analytics
  5. Build interaction matrix
  6. Train ALS model with Spark MLlib
  7. Generate recommendations for all users
  8. Save model and results
  9. Stop SparkSession

This module is called from:
  • Admin dashboard "Train Model" button → via backend API
  • CLI: python spark/train_model.py
=============================================================
"""

import os
import sys
import time
import json
import argparse

# Ensure parent dir is on path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from spark.spark_session import get_spark_session, stop_spark
from spark.data_loader import SparkDataLoader
from spark.preprocessing import SparkPreprocessor
from spark.analytics import SparkAnalytics
from spark.recommendation_model import SparkRecommendationModel

ANALYTICS_CACHE_PATH = os.getenv("PROCESSED_DATA_PATH", "data/processed/") + "analytics.json"


def run_training_pipeline(
    use_large: bool = False,
    use_s3: bool = False,
    rank: int = 10,
    max_iter: int = 10,
    reg_param: float = 0.1,
    top_n_recs: int = 10,
) -> dict:
    """
    Execute the full Spark training pipeline and return a summary report.

    Args:
        use_large : If True, load the large (1M+) dataset
        use_s3    : If True, load data from Amazon S3
        rank      : ALS rank (latent factors)
        max_iter  : ALS iterations
        reg_param : ALS regularisation
        top_n_recs: Top-N recommendations per user

    Returns:
        dict with pipeline summary statistics
    """
    pipeline_start = time.time()
    pipeline_report = {
        "status": "running",
        "stages": {},
    }

    # ── STAGE 1: SparkSession ─────────────────────────────
    print("\n" + "="*60)
    print("  SPARK TRAINING PIPELINE")
    print("="*60)
    print("[Pipeline] Stage 1: Initialising SparkSession")

    spark = get_spark_session()
    pipeline_report["stages"]["spark_init"] = "success"

    try:
        # ── STAGE 2: Data Loading ─────────────────────────
        print("\n[Pipeline] Stage 2: Loading Data")
        loader = SparkDataLoader(spark)

        if use_s3:
            raw_df = loader.load_from_s3()
        else:
            data_path = os.getenv("DATASET_PATH", "data/raw/ecommerce_interactions.csv")
            raw_df = loader.load_from_local(data_path, use_large=use_large)

        load_stats = loader.get_load_stats()
        pipeline_report["stages"]["data_loading"] = load_stats
        print(f"[Pipeline] Loaded {load_stats.get('record_count', 0):,} records")

        # ── STAGE 3: Preprocessing ────────────────────────
        print("\n[Pipeline] Stage 3: Data Preprocessing (Spark Cleaning)")
        preprocessor = SparkPreprocessor(spark)
        clean_df = preprocessor.preprocess(raw_df)
        preprocess_stats = preprocessor.get_stats()
        pipeline_report["stages"]["preprocessing"] = preprocess_stats

        # ── STAGE 4: Analytics ────────────────────────────
        print("\n[Pipeline] Stage 4: Spark SQL Analytics")
        analytics = SparkAnalytics(spark)
        analytics_report = analytics.run_full_analytics(clean_df)
        pipeline_report["stages"]["analytics"] = {
            "completed": True,
            "time_seconds": analytics_report.get("analytics_time_seconds", 0),
        }

        # Save analytics to JSON for the backend
        os.makedirs(os.path.dirname(ANALYTICS_CACHE_PATH), exist_ok=True)
        with open(ANALYTICS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(analytics_report, f, default=str)
        print(f"[Pipeline] Analytics saved: {ANALYTICS_CACHE_PATH}")

        # ── STAGE 5: Interaction Matrix ───────────────────
        print("\n[Pipeline] Stage 5: Building Interaction Matrix")
        matrix_df = preprocessor.build_interaction_matrix(clean_df)

        # ── STAGE 6: ALS Model Training ───────────────────
        print("\n[Pipeline] Stage 6: Training ALS Recommendation Model")
        rec_model = SparkRecommendationModel(spark)
        training_stats = rec_model.train(
            interaction_matrix=matrix_df,
            rank=rank,
            max_iter=max_iter,
            reg_param=reg_param,
        )
        pipeline_report["stages"]["model_training"] = training_stats

        # ── STAGE 7: Generate Recommendations ────────────
        print("\n[Pipeline] Stage 7: Generating Recommendations")
        recommendations = rec_model.generate_recommendations(
            clean_df=clean_df,
            top_n=top_n_recs,
        )
        pipeline_report["stages"]["recommendation_generation"] = {
            "users_with_recommendations": len(recommendations),
            "top_n": top_n_recs,
        }

        # ── STAGE 8: Save Model ───────────────────────────
        print("\n[Pipeline] Stage 8: Saving Model")
        rec_model.save_model()
        pipeline_report["stages"]["model_save"] = "success"

        # ── FINAL REPORT ──────────────────────────────────
        pipeline_elapsed = time.time() - pipeline_start
        pipeline_report["status"] = "completed"
        pipeline_report["total_time_seconds"] = round(pipeline_elapsed, 2)
        pipeline_report["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        print("\n" + "="*60)
        print(f"  PIPELINE COMPLETE  ({pipeline_elapsed:.1f}s)")
        print("="*60)
        print(f"  Records loaded       : {load_stats.get('record_count', 0):,}")
        print(f"  Records after clean  : {preprocess_stats.get('clean_count', 0):,}")
        print(f"  ALS RMSE             : {training_stats.get('rmse', 'N/A')}")
        print(f"  Users with recs      : {len(recommendations):,}")
        print("="*60 + "\n")

    except Exception as e:
        pipeline_report["status"] = "failed"
        pipeline_report["error"] = str(e)
        print(f"[Pipeline] ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        stop_spark(spark)

    return pipeline_report


# ────────────────────────────────────────────────────────────
# CLI Entry Point
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Spark E-Commerce Recommendation Training Pipeline"
    )
    parser.add_argument("--large",     action="store_true", help="Use large dataset")
    parser.add_argument("--s3",        action="store_true", help="Load data from Amazon S3")
    parser.add_argument("--rank",      type=int,   default=10,  help="ALS rank (default: 10)")
    parser.add_argument("--max-iter",  type=int,   default=10,  help="ALS iterations (default: 10)")
    parser.add_argument("--reg-param", type=float, default=0.1, help="ALS regularisation (default: 0.1)")
    parser.add_argument("--top-n",     type=int,   default=10,  help="Top-N recommendations (default: 10)")
    args = parser.parse_args()

    report = run_training_pipeline(
        use_large=args.large,
        use_s3=args.s3,
        rank=args.rank,
        max_iter=args.max_iter,
        reg_param=args.reg_param,
        top_n_recs=args.top_n,
    )

    print(json.dumps(report, indent=2, default=str))
