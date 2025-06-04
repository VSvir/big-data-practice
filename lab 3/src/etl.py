from config import Config
from data_loader import DataLoader
from data_processor import DataProcessor
from feature_engineer import FeatureEngineer
from spark_session import create_spark_session


def run_etl():
    spark = create_spark_session("ETL")
    
    raw_df = DataLoader.load_csv(spark, str(Config.RAW_DATA_PATH))

    DataLoader.save_as_delta(raw_df, str(Config.BRONZE_PATH))
    DataLoader.create_delta_table(spark, "bronze_student_performance", str(Config.BRONZE_PATH))

    bronze_df = DataLoader.load_delta(spark, str(Config.BRONZE_PATH))
    processed_df = DataProcessor.handle_missing_values(bronze_df)
    processed_df = DataProcessor.cast_target_column(processed_df, Config.TARGET_COL)

    pipeline = FeatureEngineer.build_feature_pipeline(
        Config.CATEGORICAL_COLS,
        Config.NUMERICAL_COLS,
        Config.BINARY_COLS
    )
    model = pipeline.fit(processed_df)
    transformed_df = model.transform(processed_df)
    silver_df = transformed_df.select(Config.TARGET_COL, "features")

    DataLoader.save_as_delta(silver_df, str(Config.SILVER_PATH))
    DataLoader.create_delta_table(spark, "silver_student_performance", str(Config.SILVER_PATH))

    DataLoader.optimize_table(spark, "silver_student_performance", Config.TARGET_COL)

    spark.stop()
    print("ETL pipeline completed successfully")

if __name__ == "__main__":
    run_etl()