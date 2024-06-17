import json
import uuid
import datetime
import kafka
from kafka import KafkaProducer

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers="kafka-1deff92e-aiven-kafka-flink-grafana.g.aivencloud.com:23163",
    security_protocol="SSL",
    ssl_cafile="/Users/admin/staging/certs/ca.pem",
    ssl_certfile="/Users/admin/staging/certs/service.cert",
    ssl_keyfile="/Users/admin/staging/certs/service.key",
)

# Define the topic name
topic_name = 'sample_topic'

# Define the timestamp
timestamp = datetime.datetime.now().isoformat()

# Define the JSON payload
sample_data = {
    "temperature": 40,
    "humidity": 40,
    "record_time": timestamp
}

# Generate a random UUID as the key and convert the string into a bytes object
key = str(uuid.uuid4()).encode('utf-8')

# Convert the JSON payload to a bytes object
payload = json.dumps(sample_data).encode('utf-8')

# Produce the message to the Kafka topic
producer.send(topic_name, key=key, value=payload)

# Close the producer
producer.close()





