from pyspark.ml import Pipeline
from pyspark.ml.feature import (OneHotEncoder, StandardScaler, StringIndexer,
                                VectorAssembler)


class FeatureEngineer:
    @staticmethod
    def build_feature_pipeline(categorical_cols, numerical_cols, binary_cols):
        indexers = [
            StringIndexer(inputCol=c, outputCol=f"{c}_index", handleInvalid="keep")
            for c in categorical_cols
        ]

        encoder = OneHotEncoder(
            inputCols=[f"{c}_index" for c in categorical_cols],
            outputCols=[f"{c}_ohe" for c in categorical_cols]
        )

        assembler = VectorAssembler(
            inputCols=[f"{c}_ohe" for c in categorical_cols] + numerical_cols + binary_cols,
            outputCol="features_unscaled"
        )

        scaler = StandardScaler(
            inputCol="features_unscaled",
            outputCol="features",
            withStd=True,
            withMean=True
        )

        return Pipeline(stages=indexers + [encoder, assembler, scaler]) #type: ignore