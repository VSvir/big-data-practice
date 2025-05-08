import json
import os
import psutil

import matplotlib.pyplot as plt
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import (OneHotEncoder, StandardScaler, StringIndexer,
                                VectorAssembler)
import seaborn as sns


def prepare_pipeline():
    cat_cols = ["DIVISION", "PREMISES_TYPE", "HOOD_158", "OCC_DOW", "OCC_MONTH"]
    indexers = [StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep") 
                for c in cat_cols]
    
    encoder_cols = ["DIVISION_idx", "PREMISES_TYPE_idx", "HOOD_158_idx"]
    encoders = [OneHotEncoder(inputCol=c, outputCol=f"{c}_ohe") 
                for c in encoder_cols]
    
    assembler_inputs = [f"{c}_ohe" for c in encoder_cols] + ["OCC_DAY", "OCC_HOUR"]
    assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features")

    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

    label_indexer = StringIndexer(inputCol="MCI_CATEGORY", outputCol="label")

    lr = LogisticRegression(featuresCol="scaled_features", 
                           labelCol="label",
                           maxIter=10,
                           regParam=0.01)
    
    return Pipeline(stages=indexers + encoders + [assembler, scaler, label_indexer, lr])


def log_metrics(spark, duration, filename, extra_metrics=None):
    process = psutil.Process()
    memory_used = process.memory_info().rss / (1024 ** 2)

    metrics = {
        "time": round(duration, 2),
        "memory_used": memory_used,
        "jobs": spark.sparkContext.statusTracker().getJobIdsForGroup(),
        **extra_metrics
    }
    
    with open(f"/app/metrics/{filename}", "w") as f:
        json.dump(metrics, f)


def plot_results():
    for filename in ["time_comparison.png", "memory_comparison.png"]:
        try:
            os.remove(f"/app/metrics/{filename}")
        except FileNotFoundError:
            pass

    metrics = {
        "1DN (Raw)": json.load(open("/app/metrics/metrics_1dn_raw.json")),
        "1DN (Opt)": json.load(open("/app/metrics/metrics_1dn_opt.json")),
        "3DN (Raw)": json.load(open("/app/metrics/metrics_3dn_raw.json")),
        "3DN (Opt)": json.load(open("/app/metrics/metrics_3dn_opt.json")),
    }
    
    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(metrics.keys()), y=[m["time"] for m in metrics.values()])
    plt.title("Execution Time Comparison")
    plt.ylabel("Time (s)")
    plt.savefig("/app/metrics/time_comparison.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(metrics.keys()), y=[m["memory_used"] for m in metrics.values()])
    plt.title("Memory Usage Comparison")
    plt.ylabel("Memory (MB)")
    plt.savefig("/app/metrics/memory_comparison.png")
    plt.close()
