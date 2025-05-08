#!/bin/bash

HADOOP_1DN="docker-compose-1dn.yml"
HADOOP_3DN="docker-compose-3dn.yml"
SPARK_CONFIG="docker-compose-spark.yml"
INITIAL_DATA_PATH="/data/crimes_in_toronto.csv"
DATA_PATH="/data/crimes.csv"
MAIN_SCRIPT="src/main.py"
PLOTS_SCRIPT="src/plots.py"
METRICS_DIR="metrics"

mkdir -p $METRICS_DIR
chmod -R 777 $METRICS_DIR

run_experiment() {
    local hadoop_config=$1
    local exp_name=$2
    local optimized=$3

    echo "Запуск эксперимента: $exp_name"
    # Остановка контейнеров
    docker-compose -f $hadoop_config down
    docker-compose -f $SPARK_CONFIG down
    # Запуск Hadoop
    docker-compose -f $hadoop_config up -d
    # Инициализация HDFS
    echo "Ожидание инициализации HDFS..."
    sleep 30
    # Загрузка данных в HDFS
    docker exec namenode hadoop fs -mkdir -p /data
    docker exec namenode hadoop fs -put $INITIAL_DATA_PATH $DATA_PATH || {
        echo "Ошибка загрузки данных в HDFS";
        exit 1;
    }
    # Модификация main.py для оптимизаций
    if [ "$optimized" = true ]; then
        sed -i 's/# OPTIMIZED //g' $MAIN_SCRIPT
    else
        sed -i 's/df = df\.cache()\.repartition(16)/# OPTIMIZED df = df.cache().repartition(16)/g' $MAIN_SCRIPT
    fi
    # Запуск Spark
    docker-compose -f $SPARK_CONFIG up -d
    docker exec spark-master mkdir -p /app/src
    docker exec spark-master chmod -R 777 /app/src
    docker exec spark-master mkdir -p /app/metrics
    docker exec spark-master chmod -R 777 /app/metrics
    # Выполнение экспериментов
    docker exec spark-master pip install -r /app/requirements.txt
    docker exec -it spark-master bash -c "cd /app/src && python main.py" || {
        echo "Ошибка выполнения Spark-приложения";
        exit 1;
    }
    # Сохранение метрик
    docker cp spark-master:/app/metrics/metrics_ml.json $METRICS_DIR/metrics_$exp_name.json
    echo "Метрики сохранены: $METRICS_DIR/metrics_$exp_name.json"
}

run_experiment $HADOOP_1DN "1dn_raw" false
run_experiment $HADOOP_1DN "1dn_opt" true
run_experiment $HADOOP_3DN "3dn_raw" false
run_experiment $HADOOP_3DN "3dn_opt" true

echo "Генерация графиков..."
docker exec -it spark-master bash -c "cd /app/src && python plots.py"
docker cp spark-master:/app/metrics/time_comparison.png ./metrics/
docker cp spark-master:/app/metrics/memory_comparison.png ./metrics/

echo -e "\n\033[1;34m=== Эксперименты завершены ===\033[0m"
echo "Графики сохранены:"
ls metrics/*.png

echo "Контейнеры остаются запущенными для анализа:"
echo -e "  Spark UI: \033[4mhttp://localhost:8080\033[0m"
echo -e "  Hadoop UI: \033[4mhttp://localhost:9870\033[0m"

while true; do
    echo -e "\nВыберите действие:"
    echo "1) Остановить все контейнеры"
    echo "2) Выйти без остановки"
    read -p "Введите номер [1-2]: " choice

    case $choice in
        1)
            echo "Остановка контейнеров..."
            docker-compose -f $HADOOP_1DN down
            docker-compose -f $HADOOP_3DN down
            docker-compose -f $SPARK_CONFIG down
            echo "Все контейнеры остановлены"
            break
            ;;
        2)
            echo -e "\nКонтейнеры остаются запущенными. Команды для остановки:"
            echo "Hadoop: docker-compose -f $HADOOP_1DN down"
            echo "Hadoop: docker-compose -f $HADOOP_3DN down"
            echo "Spark:  docker-compose -f $SPARK_CONFIG down"
            break
            ;;
        *)
            echo "Неверный выбор."
            ;;
    esac
done