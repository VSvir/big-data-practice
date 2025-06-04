from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    RAW_DATA_PATH = DATA_DIR / "student_performance.csv"
    BRONZE_PATH = DATA_DIR / "bronze" / "student_performance"
    SILVER_PATH = DATA_DIR / "silver" / "student_performance"

    MLFLOW_URI = "http://mlflow:5000"
    EXPERIMENT_NAME = "Student_GPA_Prediction"
    MODEL_NAME = "gpa_prediction_rf"

    SPARK_MEMORY = "4g"
    SPARK_APP_NAME = "StudentPerformance"

    CATEGORICAL_COLS = ['Grade', 'Gender', 'Race', 'ParentalEducation', 'SchoolType', 'Locale']
    NUMERICAL_COLS = ['SES_Quartile', 'AttendanceRate', 'StudyHours', 'FreeTime', 'GoOut']
    BINARY_COLS = ['InternetAccess', 'Extracurricular', 'PartTimeJob', 'ParentSupport', 'Romantic']
    TARGET_COL = 'GPA'

    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    CROSS_VALIDATION_FOLDS = 3
    RF_PARAMS = {
        'num_trees': [50, 100],
        'max_depth': [5, 10]
    }

    @classmethod
    def setup_directories(cls):
        cls.BRONZE_PATH.mkdir(parents=True, exist_ok=True)
        cls.SILVER_PATH.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)


Config.setup_directories()