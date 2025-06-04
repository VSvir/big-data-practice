import mlflow
from mlflow import spark
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder


class ModelTrainer:
    @staticmethod
    def train_random_forest(train_df, features_col="features", label_col="label"):
        rf = RandomForestClassifier(featuresCol=features_col, labelCol=label_col)
        
        param_grid = (ParamGridBuilder()
                     .addGrid(rf.numTrees, [50, 100])
                     .addGrid(rf.maxDepth, [5, 10])
                     .build())
        
        evaluator = MulticlassClassificationEvaluator(metricName="f1")
        
        return CrossValidator(
            estimator=rf,
            estimatorParamMaps=param_grid,
            evaluator=evaluator,
            numFolds=3
        ).fit(train_df)
    
    @staticmethod
    def evaluate_model(model, test_df, features_col="features", label_col="label"):
        predictions = model.transform(test_df)
        evaluator = MulticlassClassificationEvaluator(labelCol=label_col)
        
        return {
            "f1": evaluator.setMetricName("f1").evaluate(predictions),
            "accuracy": evaluator.setMetricName("accuracy").evaluate(predictions)
        }
    
    @staticmethod
    def log_model_to_mlflow(model, metrics, run_name="RandomForest"):
        spark.log_model(model.bestModel, "model")
        mlflow.log_params({
            "numTrees": model.bestModel.getNumTrees,
            "maxDepth": model.bestModel.getMaxDepth()
        })
        mlflow.log_metrics(metrics)
        mlflow.set_tag("model", run_name)