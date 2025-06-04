import mlflow

from config import Config
from data_loader import DataLoader
from model_trainer import ModelTrainer
from spark_session import create_spark_session


def run_ml():
    spark = create_spark_session("ML")

    mlflow.set_tracking_uri(Config.MLFLOW_URI)
    mlflow.set_experiment(Config.EXPERIMENT_NAME)

    silver_df = DataLoader.load_delta(spark, str(Config.SILVER_PATH))
    silver_df = silver_df.withColumnRenamed(Config.TARGET_COL, "label")
    train_df, test_df = silver_df.randomSplit(
        [1 - Config.TEST_SIZE, Config.TEST_SIZE], 
        seed=Config.RANDOM_STATE
    )

    with mlflow.start_run():
        cv_model = ModelTrainer.train_random_forest(train_df)

        metrics = ModelTrainer.evaluate_model(cv_model, test_df)
        print(f"Test F1: {metrics['f1']:.4f}, Accuracy: {metrics['accuracy']:.4f}")

        ModelTrainer.log_model_to_mlflow(cv_model, metrics)
    
    spark.stop()
    print("ML pipeline completed successfully")

if __name__ == "__main__":
    run_ml()