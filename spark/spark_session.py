"""
=============================================================
Spark Session Factory
Centralised SparkSession creation for the project.
=============================================================
"""

import os
import sys
from pyspark.sql import SparkSession
from dotenv import load_dotenv

load_dotenv()

# Automatically set JAVA_HOME if not already set
if "JAVA_HOME" not in os.environ:
    java_dirs = [
        r"C:\Program Files\Java\jdk-19",
        os.getenv("JAVA_HOME", ""),
    ]
    for jd in java_dirs:
        if jd and os.path.exists(jd):
            os.environ["JAVA_HOME"] = jd
            break


def get_spark_session(
    app_name: str = None,
    master: str = None,
    driver_memory: str = None,
    executor_memory: str = None,
    enable_hive: bool = False,
) -> SparkSession:
    """
    Create or retrieve the existing SparkSession.

    All Spark components in this project use this factory so that
    a single SparkSession is shared per process.

    Args:
        app_name       : Spark application name
        master         : Spark master URL  (default from env: local[*])
        driver_memory  : Driver JVM heap   (default from env: 2g)
        executor_memory: Executor JVM heap (default from env: 2g)
        enable_hive    : Whether to enable Hive support

    Returns:
        SparkSession instance
    """
    app_name = app_name or os.getenv("SPARK_APP_NAME", "EcommerceRecommendation")
    master = master or os.getenv("SPARK_MASTER", "local[*]")
    driver_memory = driver_memory or os.getenv("SPARK_DRIVER_MEMORY", "2g")
    executor_memory = executor_memory or os.getenv("SPARK_EXECUTOR_MEMORY", "2g")

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.driver.memory", driver_memory)
        .config("spark.executor.memory", executor_memory)
        # Reduce Spark UI port conflicts in dev
        .config("spark.ui.port", "4041")
        # Better serialisation
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        # Shuffle partitions (lower for local mode)
        .config("spark.sql.shuffle.partitions", "8")
        # Log level
        .config("spark.driver.extraJavaOptions", "-Dlog4j.logLevel=WARN")
    )

    if enable_hive:
        builder = builder.enableHiveSupport()

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def stop_spark(spark: SparkSession):
    """Safely stop the SparkSession."""
    try:
        if spark and not spark._sc._jvm.SparkContext.getOrCreate().isStopped():
            spark.stop()
    except Exception:
        pass
