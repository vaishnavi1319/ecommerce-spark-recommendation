"""
=============================================================
Spark Analytics Module
=============================================================
Performs Big Data analytics using Spark DataFrames and
Spark SQL to extract business insights.

Analyses:
  • Total users / products / interactions
  • Most popular products (by interaction count)
  • Most purchased products
  • Category distribution
  • Most active users
  • Average ratings per category and product
  • Interaction type distribution
  • Daily/monthly activity trends
  • Price range distribution
  • Top-rated products

All operations use Spark DataFrames / Spark SQL.
=============================================================
"""

import time
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


class SparkAnalytics:
    """Extracts analytics insights from the clean interaction DataFrame."""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    # ──────────────────────────────────────────────────────
    # OVERVIEW STATISTICS
    # ──────────────────────────────────────────────────────
    def get_overview_stats(self, df: DataFrame) -> dict:
        """
        Compute high-level statistics about the dataset.

        Uses a single Spark action with multiple aggregations
        to minimise the number of passes over the data.
        """
        start = time.time()

        stats_row = df.agg(
            F.countDistinct("user_id").alias("total_users"),
            F.countDistinct("product_id").alias("total_products"),
            F.count("interaction_id").alias("total_interactions"),
            F.countDistinct("category").alias("total_categories"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
            F.round(F.avg("price"), 2).alias("avg_price"),
        ).collect()[0]

        elapsed = time.time() - start
        return {
            "total_users": int(stats_row["total_users"]),
            "total_products": int(stats_row["total_products"]),
            "total_interactions": int(stats_row["total_interactions"]),
            "total_categories": int(stats_row["total_categories"]),
            "avg_rating": float(stats_row["avg_rating"] or 0),
            "avg_price": float(stats_row["avg_price"] or 0),
            "computation_time_seconds": round(elapsed, 2),
        }

    # ──────────────────────────────────────────────────────
    # POPULAR PRODUCTS
    # ──────────────────────────────────────────────────────
    def get_popular_products(self, df: DataFrame, top_n: int = 10) -> list:
        """
        Rank products by total interaction count.
        Uses Spark SQL window functions for ranking.
        """
        df.createOrReplaceTempView("interactions_v")

        result = self.spark.sql(f"""
            SELECT
                product_id,
                product_name,
                category,
                price,
                COUNT(*) AS interaction_count,
                ROUND(AVG(rating), 2) AS avg_rating,
                SUM(CASE WHEN interaction_type='purchase' THEN 1 ELSE 0 END) AS purchase_count,
                SUM(CASE WHEN interaction_type='add_to_cart' THEN 1 ELSE 0 END) AS cart_count,
                SUM(CASE WHEN interaction_type='view' THEN 1 ELSE 0 END) AS view_count
            FROM interactions_v
            GROUP BY product_id, product_name, category, price
            ORDER BY interaction_count DESC
            LIMIT {top_n}
        """)

        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # MOST PURCHASED PRODUCTS
    # ──────────────────────────────────────────────────────
    def get_most_purchased(self, df: DataFrame, top_n: int = 10) -> list:
        """Products ranked by purchase count using Spark groupBy."""
        result = (
            df.filter(F.col("interaction_type") == "purchase")
            .groupBy("product_id", "product_name", "category", "price")
            .agg(
                F.count("*").alias("purchase_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating"),
            )
            .orderBy(F.desc("purchase_count"))
            .limit(top_n)
        )
        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # CATEGORY DISTRIBUTION
    # ──────────────────────────────────────────────────────
    def get_category_distribution(self, df: DataFrame) -> list:
        """
        Category-level interaction and revenue analytics.
        Demonstrates Spark aggregation on multiple metrics.
        """
        result = self.spark.sql("""
            SELECT
                category,
                COUNT(*) AS interaction_count,
                COUNT(DISTINCT user_id) AS unique_users,
                COUNT(DISTINCT product_id) AS unique_products,
                ROUND(AVG(rating), 2) AS avg_rating,
                ROUND(AVG(price), 2) AS avg_price,
                SUM(CASE WHEN interaction_type='purchase' THEN price ELSE 0 END) AS estimated_revenue
            FROM interactions_v
            GROUP BY category
            ORDER BY interaction_count DESC
        """)
        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # MOST ACTIVE USERS
    # ──────────────────────────────────────────────────────
    def get_most_active_users(self, df: DataFrame, top_n: int = 10) -> list:
        """Users ranked by interaction count using Spark DataFrames."""
        result = (
            df.groupBy("user_id", "user_name", "user_email")
            .agg(
                F.count("*").alias("interaction_count"),
                F.countDistinct("product_id").alias("unique_products"),
                F.sum(
                    F.when(F.col("interaction_type") == "purchase", 1).otherwise(0)
                ).alias("purchase_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating"),
            )
            .orderBy(F.desc("interaction_count"))
            .limit(top_n)
        )
        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # INTERACTION TYPE DISTRIBUTION
    # ──────────────────────────────────────────────────────
    def get_interaction_distribution(self, df: DataFrame) -> list:
        """Breakdown of interaction types across the dataset."""
        total = df.count()
        result = (
            df.groupBy("interaction_type")
            .agg(F.count("*").alias("count"))
            .withColumn("percentage", F.round(F.col("count") / total * 100, 2))
            .orderBy(F.desc("count"))
        )
        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # RATING DISTRIBUTION
    # ──────────────────────────────────────────────────────
    def get_rating_distribution(self, df: DataFrame) -> list:
        """Distribution of ratings across all interactions."""
        result = (
            df.withColumn("rating_bucket", F.floor(F.col("rating")).cast("int"))
            .groupBy("rating_bucket")
            .agg(F.count("*").alias("count"))
            .orderBy("rating_bucket")
        )
        rows = result.collect()
        return [{"rating": row["rating_bucket"], "count": row["count"]} for row in rows]

    # ──────────────────────────────────────────────────────
    # MONTHLY TRENDS
    # ──────────────────────────────────────────────────────
    def get_monthly_trends(self, df: DataFrame) -> list:
        """Monthly interaction counts to show activity velocity."""
        result = (
            df.withColumn(
                "month", F.date_format(
                    F.to_timestamp(F.col("timestamp"), "yyyy-MM-dd HH:mm:ss"), "yyyy-MM"
                )
            )
            .groupBy("month")
            .agg(
                F.count("*").alias("interactions"),
                F.countDistinct("user_id").alias("active_users"),
                F.sum(
                    F.when(F.col("interaction_type") == "purchase", 1).otherwise(0)
                ).alias("purchases"),
            )
            .orderBy("month")
        )
        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # TOP RATED PRODUCTS
    # ──────────────────────────────────────────────────────
    def get_top_rated_products(self, df: DataFrame, min_reviews: int = 10, top_n: int = 10) -> list:
        """
        Products with the highest average rating,
        filtered to have at least `min_reviews` reviews.
        Uses Spark HAVING equivalent via filter after groupBy.
        """
        result = (
            df.groupBy("product_id", "product_name", "category", "price")
            .agg(
                F.round(F.avg("rating"), 2).alias("avg_rating"),
                F.count("*").alias("review_count"),
            )
            .filter(F.col("review_count") >= min_reviews)
            .orderBy(F.desc("avg_rating"), F.desc("review_count"))
            .limit(top_n)
        )
        return [row.asDict() for row in result.collect()]

    # ──────────────────────────────────────────────────────
    # FULL ANALYTICS REPORT
    # ──────────────────────────────────────────────────────
    def run_full_analytics(self, df: DataFrame) -> dict:
        """
        Execute all analytics in sequence and return
        a comprehensive report dictionary.
        """
        print("[Analytics] Running full Spark analytics pipeline...")
        start = time.time()

        # Register the view once for all SQL queries
        df.createOrReplaceTempView("interactions_v")

        report = {
            "overview": self.get_overview_stats(df),
            "popular_products": self.get_popular_products(df),
            "most_purchased": self.get_most_purchased(df),
            "category_distribution": self.get_category_distribution(df),
            "most_active_users": self.get_most_active_users(df),
            "interaction_distribution": self.get_interaction_distribution(df),
            "rating_distribution": self.get_rating_distribution(df),
            "monthly_trends": self.get_monthly_trends(df),
            "top_rated_products": self.get_top_rated_products(df),
        }

        elapsed = time.time() - start
        report["analytics_time_seconds"] = round(elapsed, 2)
        print(f"[Analytics] Full analytics completed in {elapsed:.2f}s")
        return report
