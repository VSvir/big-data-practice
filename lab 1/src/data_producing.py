import json
import time
from pathlib import Path
from threading import Thread

import pandas as pd
from confluent_kafka import Producer


def read_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path).drop(columns='Unnamed: 0')


def produce_data(df: pd.DataFrame, producer: Producer, topic: str):
    for accident_id, row in df.iterrows():
        data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'accident_data': row.to_dict()
        }

        producer.produce(topic=topic, key=str(accident_id), value=json.dumps(data))
        producer.flush()

        print(f"""
              ID: {accident_id}
              SENT TO: {topic}""")
        time.sleep(0.1)
    

def produce_accidents_info(producer: Producer):
    path = Path(__file__).parent.parent / "data" / "accidents_info.csv"
    df = read_data(path)
    df = df.drop(columns='crash_date')
    produce_data(df, producer, 'accidents_info')


def produce_road_condition_data(producer: Producer):
    path = Path(__file__).parent.parent / "data" / "road_conditions.csv"
    df = read_data(path)
    produce_data(df, producer, 'road_conditions')


if __name__ == '__main__':
    config = {'bootstrap.servers': 'localhost:9095'}

    info_producer = Producer(config)
    conditions_producer = Producer(config)

    Thread(target=produce_accidents_info, args=(info_producer,)).start()
    Thread(target=produce_road_condition_data, args=(conditions_producer,)).start()
