import json

from confluent_kafka import Consumer, Producer

from utils.cat_vals_dict import get_categorical_values_dict
from utils.data_aggregator import DataAggregator


def process_data(data, encoding_dict: dict):
    processed_data = {}
    print(data)
    for col_name, value in data.items():
        known_values = encoding_dict.get(col_name)
        if known_values is None:
            processed_data[col_name] = value
        else:
            processed_data[col_name] = known_values.index(value)
    return processed_data


def process_and_send(producer, aggregator, message, encoding_dict):
    try:
        data = json.loads(message.value().decode('utf-8'))
        accident_id = message.key().decode('utf-8')
        topic = message.topic()
        
        data_type = 'accident' if topic == 'accidents_info' else 'road'
        processed = process_data(data['accident_data'], encoding_dict)
        
        if aggregator.add_data(accident_id, data_type, processed):
            combined_data = aggregator.get_combined_data(accident_id)
            
            producer.produce(
                topic='processed_data',
                key=accident_id,
                value=json.dumps({
                    'features': combined_data,
                    'label': combined_data.pop('crash_type', None)
                })
            )
            producer.flush()
            print(f"Sent combined data for {accident_id}")
    except Exception as e:
        print(f"Error processing message: {str(e)}")


if __name__ == '__main__':
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9095',
        'group.id': 'data_processor',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    })
    producer = Producer({'bootstrap.servers': 'localhost:9096'})
    aggregator = DataAggregator()
    encoding_dict = get_categorical_values_dict()

    consumer.subscribe(['accidents_info', 'road_conditions'])

    while True:
        msg = consumer.poll(10)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        
        process_and_send(producer, aggregator, msg, encoding_dict)

