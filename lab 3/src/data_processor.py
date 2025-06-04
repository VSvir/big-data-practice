from pyspark.sql import DataFrame
from pyspark.sql import functions as F


class DataProcessor:
    @staticmethod
    def handle_missing_values(df: DataFrame) -> DataFrame:
        return df.fillna({
            'StudyHours': 0,
            'AttendanceRate': 0.0,
            'FreeTime': 3,
            'GoOut': 3
        })
    
    @staticmethod
    def cast_target_column(df: DataFrame, target_col: str) -> DataFrame:
        return df.withColumn(target_col, F.col(target_col).cast("integer"))
    