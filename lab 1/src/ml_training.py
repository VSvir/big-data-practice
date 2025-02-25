import json

from confluent_kafka import Consumer

from utils.trainer import ModelTrainer

if __name__ == '__main__':
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9096',
        'group.id': 'ml_trainer',
        'auto.offset.reset': 'earliest'
    })

    trainer = ModelTrainer()
    consumer.subscribe(['processed_data'])

    while True:
        msg = consumer.poll(10)
        if msg is None:
            continue
            
        try:
            data = json.loads(msg.value().decode('utf-8'))
            features = data['features']
            label = data['label']
            
            trainer.add_data(features, label)
                
        except Exception as e:
            print(f"Training error: {str(e)}")
