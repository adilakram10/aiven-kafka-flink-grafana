import json
from kafka import KafkaConsumer

# Create a Kafka consumer
consumer = KafkaConsumer(
    bootstrap_servers="kafka-1deff92e-aiven-kafka-flink-grafana.g.aivencloud.com:23163",
    auto_offset_reset='earliest',  ## reading from beginning of the topic
    security_protocol="SSL",
    ssl_cafile="/Users/admin/staging/certs/ca.pem",
    ssl_certfile="/Users/admin/staging/certs/service.cert",
    ssl_keyfile="/Users/admin/staging/certs/service.key",
)

# Subscribe to the Kafka topic
consumer.subscribe(['sample_topic'])

# Consume messages from the Kafka topic
for message in consumer:
    # Get the key and value from the message
    key = message.key.decode('utf-8')
    value = message.value.decode('utf-8')

    # Parse the JSON object from the value
    output = json.loads(value)

    # Print the JSON object
    print(output)

# Close the consumer
#consumer.close()


