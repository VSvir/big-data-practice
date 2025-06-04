from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

from config import Config


def create_spark_session(step_name):
    app_name = f"{Config.SPARK_APP_NAME}_{step_name}"

    builder = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.executor.memory", Config.SPARK_MEMORY) \
        .config("spark.driver.memory", Config.SPARK_MEMORY) \
        .master("local[*]")
    return configure_spark_with_delta_pip(builder).getOrCreate()