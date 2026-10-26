"""
=============================================================
Spark Data Preprocessing
=============================================================
Performs all data cleaning and transformation using PySpark.

Operations demonstrated:
  • Removing duplicate records       (Spark deduplication)
  • Handling missing / null values   (Spark dropna / fillna)
  • Validating IDs                   (Spark filter)
  • Converting timestamps            (Spark to_timestamp)
  • Normalising ratings              (Spark withColumn)
  • Aggregating interaction scores   (Spark groupBy + agg)
  • Caching hot DataFrames           (Spark cache)
  • Partitioning for efficiency      (Spark repartition)

All operations use Spark DataFrames / Spark SQL — NO Pandas.
=============================================================
"""

import time
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


class SparkPreprocessor:
    """Cleans and prepares the raw interaction DataFrame."""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.stats: dict = {}

    # ──────────────────────────────────────────────────────
    # MAIN PIPELINE
    # ──────────────────────────────────────────────────────
    def preprocess(self, raw_df: DataFrame) -> DataFrame:
        """
        Full preprocessing pipeline.

        Steps:
          1. Record initial count
          2. Drop exact duplicate rows
          3. Drop rows with missing critical fields
          4. Validate user_id and product_id ranges
          5. Clamp/validate ratings to [1.0, 5.0]
          6. Parse timestamp column
          7. Aggregate interaction scores per user-product pair
          8. Cache the clean DataFrame

        Args:
            raw_df: Raw Spark DataFrame loaded from CSV

        Returns:
            Cleaned and transformed Spark DataFrame
        """
        start = time.time()
        initial_count = raw_df.count()
        self.stats["initial_count"] = initial_count
        print(f"[Preprocessor] Initial records : {initial_count:,}")

        # ── 1. Drop exact duplicates ─────────────────────
        df = raw_df.dropDuplicates()
        after_dedup = df.count()
        self.stats["removed_duplicates"] = initial_count - after_dedup
        print(f"[Preprocessor] After dedup     : {after_dedup:,} "
              f"(removed {initial_count - after_dedup:,})")

        # ── 2. Drop rows missing critical fields ─────────
        critical_cols = ["user_id", "product_id", "interaction_type", "interaction_score"]
        df = df.dropna(subset=critical_cols)
        after_dropna = df.count()
        self.stats["removed_null_rows"] = after_dedup - after_dropna
        print(f"[Preprocessor] After null drop : {after_dropna:,}")

        # ── 3. Validate IDs (must be positive integers) ──
        df = df.filter(
            (F.col("user_id") > 0) &
            (F.col("product_id") > 0)
        )

        # ── 4. Clamp ratings to valid range [1.0, 5.0] ───
        df = df.withColumn(
            "rating",
            F.when(F.col("rating").isNull(), 3.0)   # fill missing with neutral
             .when(F.col("rating") < 1.0, 1.0)
             .when(F.col("rating") > 5.0, 5.0)
             .otherwise(F.col("rating"))
        )

        # ── 5. Parse timestamp ────────────────────────────
        df = df.withColumn(
            "event_time",
            F.to_timestamp(F.col("timestamp"), "yyyy-MM-dd HH:mm:ss")
        )

        # ── 6. Normalise interaction_score (fill if null) ─
        score_map = {"view": 1, "click": 2, "wishlist": 2, "add_to_cart": 3, "purchase": 5}
        score_expr = F.when(F.col("interaction_score").isNull(),
            F.when(F.col("interaction_type") == "view", 1)
             .when(F.col("interaction_type") == "click", 2)
             .when(F.col("interaction_type") == "wishlist", 2)
             .when(F.col("interaction_type") == "add_to_cart", 3)
             .when(F.col("interaction_type") == "purchase", 5)
             .otherwise(1)
        ).otherwise(F.col("interaction_score"))
        df = df.withColumn("interaction_score", score_expr)

        # ── 7. Fill missing reviews ───────────────────────
        df = df.fillna({"review": "", "user_name": "Unknown"})

        clean_count = df.count()
        self.stats["clean_count"] = clean_count
        self.stats["total_removed"] = initial_count - clean_count

        # ── 8. Cache for downstream reuse ─────────────────
        df = df.cache()

        elapsed = time.time() - start
        self.stats["preprocessing_time_seconds"] = round(elapsed, 2)

        print(f"[Preprocessor] Clean records   : {clean_count:,}")
        print(f"[Preprocessor] Total removed   : {initial_count - clean_count:,}")
        print(f"[Preprocessor] Time taken      : {elapsed:.2f}s")
        return df

    # ──────────────────────────────────────────────────────
    # AGGREGATED USER–PRODUCT MATRIX
    # ──────────────────────────────────────────────────────
    def build_interaction_matrix(self, clean_df: DataFrame) -> DataFrame:
        """
        Aggregate multiple interactions of the same user–product pair
        into a single weighted score for the ALS model.

        ALS requires one (user_id, product_id, score) row per pair.
        We compute:
            score = min(sum(interaction_score * rating_weight), 10)

        This avoids inflated scores for extremely active users.

        Args:
            clean_df: Preprocessed interactions DataFrame

        Returns:
            DataFrame with columns: user_id, product_id, score
        """
        print("[Preprocessor] Building user-product interaction matrix...")

        # Weight the interaction score by the normalised rating
        weighted = clean_df.withColumn(
            "weighted_score",
            F.col("interaction_score") * (F.col("rating") / 5.0)
        )

        # Register temp view for Spark SQL demonstration
        weighted.createOrReplaceTempView("interactions")

        # Aggregate per user-product pair and cap score at 10
        # Two-step: sum first, then apply least() — Spark SQL doesn't allow
        # nested aggregates like MIN(SUM(...))
        matrix_df = (
            weighted
            .groupBy("user_id", "product_id")
            .agg(
                F.round(
                    F.least(F.sum("weighted_score"), F.lit(10.0)), 4
                ).alias("score")
            )
        )

        # Also expose via Spark SQL for demonstration
        matrix_df.createOrReplaceTempView("interaction_matrix")
        try:
            cnt = matrix_df.count()
        except Exception:
            cnt = 0

        print(f"[Preprocessor] Interaction matrix pairs: {cnt:,}")
        matrix_df = matrix_df.cache()
        return matrix_df

    def get_stats(self) -> dict:
        return self.stats
