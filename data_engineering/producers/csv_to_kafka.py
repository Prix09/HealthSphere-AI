import os
import time
import json
import pandas as pd
from kafka import KafkaProducer

# Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# We can run this from the client container where KAFKA_BROKER would be "kafka:29092"
print(f"Connecting to Kafka at {KAFKA_BROKER}")
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def stream_csv_to_kafka(file_name, topic):
    file_path = os.path.join(DATA_DIR, file_name)
    print(f"Streaming {file_path} to topic {topic}")
    try:
        df = pd.read_csv(file_path)
        # Replacing NaNs with None for JSON serialization
        df = df.where(pd.notnull(df), None)
        for index, row in df.iterrows():
            message = row.to_dict()
            producer.send(topic, value=message)
            # Sleep briefly to simulate streaming
            time.sleep(0.01)
        producer.flush()
        print(f"Finished streaming {file_name}")
    except Exception as e:
        print(f"Failed to stream {file_name}: {e}")

if __name__ == "__main__":
    # Wait for Kafka to be ready
    time.sleep(10)
    stream_csv_to_kafka("Air_Quality_1000.csv", "air_quality")
    stream_csv_to_kafka("Fitbit_Activity_1000.csv", "fitness_activity")
    stream_csv_to_kafka("Health_Indicators_1000.csv", "health_indicators")
