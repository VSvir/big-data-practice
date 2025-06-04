from pyspark.sql import DataFrame


class DataLoader:
    @staticmethod
    def load_csv(spark, path: str) -> DataFrame:
        return spark.read.csv(path, header=True, inferSchema=True)
    
    @staticmethod
    def load_delta(spark, path: str) -> DataFrame:
        return spark.read.format("delta").load(path)
    
    @staticmethod
    def save_as_delta(df: DataFrame, path: str, mode: str = "overwrite", partition_by=None):
        writer = df.write.format("delta").mode(mode)
        if partition_by:
            writer = writer.partitionBy(partition_by)
        writer.save(path)

    @staticmethod
    def create_delta_table(spark, table_name: str, path: str):
        spark.sql(f"CREATE TABLE IF NOT EXISTS {table_name} USING DELTA LOCATION '{path}'")

    @staticmethod
    def optimize_table(spark, table_name: str, zorder_col: str):
        spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({zorder_col})")