# Lab Work 1 - Kafka

## Запуск
Поднять контейнер: `docker-compose up -d`
Запустите по порядку скрипты в отдельных терминалах:
* python src/data_producing.py
* python src/data_processing.py
* python3 src/pml_training.py
* streamlit run app/app.py

Выключение
Во всех консолях остановите работу скриптов через Ctrl+C
* Выполните `docker-compose down`