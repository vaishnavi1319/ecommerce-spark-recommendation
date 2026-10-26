"""
=============================================================
Spark Data Loader
=============================================================
Handles loading e-commerce datasets into Spark DataFrames
from local storage or Amazon S3 (cloud).

Demonstrates:
  • Spark DataFrame creation from CSV
  • Schema inference / explicit schema definition
  • S3 cloud data reading
  • Partition display for distributed processing awareness
=============================================================
"""

import os
import time
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, FloatType, TimestampType
)
from pyspark.sql import functions as F
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────────────────
# Explicit schema for the interaction CSV
# Using an explicit schema is faster than inferSchema=True
# because Spark doesn't need an extra pass over the data.
# ──────────────────────────────────────────────────────────
INTERACTION_SCHEMA = StructType([
    StructField("interaction_id",   IntegerType(), True),
    StructField("user_id",          IntegerType(), True),
    StructField("user_name",        StringType(),  True),
    StructField("user_email",       StringType(),  True),
    StructField("product_id",       IntegerType(), True),
    StructField("product_name",     StringType(),  True),
    StructField("category",         StringType(),  True),
    StructField("price",            FloatType(),   True),
    StructField("interaction_type", StringType(),  True),
    StructField("interaction_score",IntegerType(), True),
    StructField("rating",           FloatType(),   True),
    StructField("review",           StringType(),  True),
    StructField("timestamp",        StringType(),  True),
])


class SparkDataLoader:
    """
    Loads e-commerce data into Spark DataFrames.

    Supports:
      - Local CSV files
      - Amazon S3 files (cloud deployment)
    """

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self._load_stats: dict = {}

    # ──────────────────────────────────────────────────────
    # LOCAL  LOADING
    # ──────────────────────────────────────────────────────
    def load_from_local(self, file_path: str, use_large: bool = False) -> DataFrame:
        """
        Load interaction data from a local CSV file.

        Args:
            file_path : Absolute or relative path to the CSV
            use_large : If True, try the large dataset path first

        Returns:
            Spark DataFrame with interaction records
        """
        if use_large:
            large_path = os.getenv("LARGE_DATASET_PATH", "data/raw/ecommerce_large.csv")
            if os.path.exists(large_path):
                file_path = large_path
                print(f"[Spark Loader] Using LARGE dataset: {large_path}")
            else:
                print(f"[Spark Loader] Large dataset not found, using: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Dataset not found: {file_path}\n"
                "Run: python scripts/generate_large_dataset.py"
            )

        start = time.time()
        print(f"[Spark Loader] Loading data from local: {file_path}")

        df = (
            self.spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
            .option("mode", "DROPMALFORMED")
            .csv(file_path)
        )

        # Force Spark action to measure actual load time
        count = df.count()
        elapsed = time.time() - start

        self._load_stats = {
            "source": "local",
            "file_path": file_path,
            "record_count": count,
            "load_time_seconds": round(elapsed, 2),
            "num_partitions": df.rdd.getNumPartitions(),
            "file_size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
        }

        print(f"[Spark Loader] Loaded {count:,} records in {elapsed:.2f}s")
        print(f"[Spark Loader] Partitions: {df.rdd.getNumPartitions()}")
        return df

    # ──────────────────────────────────────────────────────
    # CLOUD / S3  LOADING
    # ──────────────────────────────────────────────────────
    def load_from_s3(self, s3_path: str = None) -> DataFrame:
        """
        Load interaction data from Amazon S3.

        The SparkSession must be configured with AWS credentials.
        This method demonstrates the cloud-storage integration.

        Example s3_path: s3a://ecommerce-spark-dataset/raw/interactions.csv

        Args:
            s3_path : Full S3 URI

        Returns:
            Spark DataFrame with interaction records
        """
        if s3_path is None:
            bucket = os.getenv("S3_BUCKET_NAME", "ecommerce-spark-dataset")
            s3_path = f"s3a://{bucket}/raw/ecommerce_interactions.csv"

        # Configure AWS credentials in Spark
        aws_key    = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        region     = os.getenv("AWS_REGION", "us-east-1")

        if aws_key and aws_secret:
            hadoop_conf = self.spark.sparkContext._jsc.hadoopConfiguration()
            hadoop_conf.set("fs.s3a.access.key", aws_key)
            hadoop_conf.set("fs.s3a.secret.key", aws_secret)
            hadoop_conf.set("fs.s3a.endpoint", f"s3.{region}.amazonaws.com")
            hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            hadoop_conf.set("com.amazonaws.services.s3.enableV4", "true")

        start = time.time()
        print(f"[Spark Loader] Loading data from S3: {s3_path}")

        df = (
            self.spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .option("mode", "DROPMALFORMED")
            .csv(s3_path)
        )

        count = df.count()
        elapsed = time.time() - start

        self._load_stats = {
            "source": "s3",
            "s3_path": s3_path,
            "record_count": count,
            "load_time_seconds": round(elapsed, 2),
            "num_partitions": df.rdd.getNumPartitions(),
        }

        print(f"[Spark Loader] Loaded {count:,} records from S3 in {elapsed:.2f}s")
        return df

    # ──────────────────────────────────────────────────────
    # PRODUCTS  CSV
    # ──────────────────────────────────────────────────────
    def load_products(self, file_path: str = "data/raw/products.csv") -> DataFrame:
        """Load the products catalogue CSV into a Spark DataFrame."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Products file not found: {file_path}")

        df = (
            self.spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(file_path)
        )
        print(f"[Spark Loader] Products loaded: {df.count():,} records")
        return df

    def get_load_stats(self) -> dict:
        """Return statistics from the last load operation."""
        return self._load_stats
