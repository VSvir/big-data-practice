import time

from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

from utils import log_metrics, prepare_pipeline


def run_ml_pipeline(spark, hdfs_path):
    df = spark.read.csv(hdfs_path, header=True, inferSchema=True)
    df = df.select(
        "OCC_MONTH", "OCC_DAY", "OCC_DOW", "OCC_HOUR",
        "DIVISION", "PREMISES_TYPE", "HOOD_158", "MCI_CATEGORY"
    )
    df = df.cache().repartition(16)

    df = df.withColumn(
        "OCC_DAY", when(col("OCC_DAY") == "None", None).otherwise(col("OCC_DAY").cast("int"))
        ).withColumn(
            "OCC_HOUR", when(col("OCC_HOUR") == "None", None).otherwise(col("OCC_HOUR").cast("int"))
            )
    df = df.na.drop(subset=["OCC_DAY", "OCC_HOUR"])

    train, test = df.randomSplit([0.8, 0.2], seed=42)
    pipeline = prepare_pipeline()
    model = pipeline.fit(train)
    predictions = model.transform(test)

    evaluator = MulticlassClassificationEvaluator(
        labelCol="label", 
        predictionCol="prediction",
        metricName="accuracy"
    )
    accuracy = evaluator.evaluate(predictions)
    print(f"Accuracy: {accuracy:.2f}")

    return model, accuracy

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("CrimePrediction") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    start_time = time.time()
    model, accuracy = run_ml_pipeline(spark, "hdfs://namenode:8020/data/crimes.csv")
    duration = time.time() - start_time
    
    log_metrics(spark, duration, "metrics_ml.json", extra_metrics={"accuracy": accuracy})
    
    spark.stop()
