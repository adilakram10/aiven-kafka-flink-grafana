
# Integrate Kafka with Flink and Grafana | Aiven for Building Data Processing and Streaming pipeline application 

## **Summary**

Simplify the flow of your data from Aiven for Kafka to Flink to Grafana effortlessly to enhance application monitoring, analytics, search capabilities, and dashboard creation. This guide provides step-by-step instructions for building a streaming and data processing application with real-time ingestion using Kafka Connect and M3DB on the Aiven Platform, utilizing a straightforward Python client application on Aiven, and ultimately visualizing the data by integrating with Flink and Grafana.

## **Prerequisites**

1. **A running Aiven Kafka cluster.**
The easiest way to run a kafka cluster is on the Aiven platform. If you don’t have a cluster, please [sign up](https://console.aiven.io/signup) and receive credits to test your deployment. After logging into the console, create a project selecting a particular region.

2. **Aiven for Kafka service.** Create apache kafka service from the service page selecting a cloud provider, region, service plan which determines the number of servers, memory, CPU and disk resources allocated to your service. It might take a few minutes for the service to transition from rebuilding to running state, after which you can start using it.

3. Install Python3 on Mac using homebrew and update system’s PATH variable to use the installed binary.

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
export PATH=/Users/admin/Library/Python/3.9/bin:$PATH >> ~/.zshrc
mkdir aiven-kafka && cd aiven-kafka
```

4. Create a python virtual environment to separate the demo project

```
python3 -m venv test_env
source test_env/bin/activate
```


5. Install Apache kafka python client library

```
pip3 install kafka-python
```




## **Solution**

Welcome to the Aiven cloud demo environment where you’ll produce sample JSON data containing UUID as key and sample payload as value using Python to a Kafka topic. We will then bifurcate the data among 2 topics using Flink, and finally integrate it with Grafana to create dashboards for monitoring.


[![Application Data flow with Kafka connect](/Users/admin/repo/aiven-kafka-flink-grafana/Image1.png)](/Users/admin/repo/aiven-kafka-flink-grafana/Image1.png)



## **Steps to Implement**

1. ### **Produce messages to Aiven Kafka**
    
    1.1. Create a topic using Aiven client:In order to create a topic, you’ll need to install and login through aiven client CLI in your terminal. (Note: Replication factor must be set to at least two.)

    1.2. Update the certificates: Download the necessary root, client certificates and key from the console and update the python code with full path of the certificates.
    
    1.3. Execute the code to produce and consume messages to and from Kafka topic.
   
   ```
   python kafka_producer.py
   python kafka_consumer.py
   ```


2. ### **Aiven for Apache Flink - Data transformation using SQL**
 
    Here we will demonstrate how to filter the data into multiple topics using Aiven Flink. This is accomplished by implementing a data processing pipeline by creating SQL applications with source and sink tables, and transforming SQL to filter the data writing to multiple destination topics.

    2.1. **Go to the Aiven console and create service for Flink**

    ```
    python3 -m pip install aiven-client
    export PATH=/Users/admin/Library/Python/3.9/bin:$PATH >> ~/.zshrc
    avn user login
    avn service list
    avn service topic-create $KAFKA_SERVICE $TOPIC_NAME --partitions 1 --replication 2
    ```

    2.2. **Integrate Flink with Kafka using the console or CLI using the following commands**

    ```
    avn project list   # get the project name 
    avn service list   # get the kafka and flink service name
    avn project switch $PROJECTNAME
    avn service integration-create \
    --project $PROJECT_NAME \
    --source-service $KAFKA_SERVICE \
    --dest-service $FLINK_SERVICE \
    --integration-type flink \
    ```

    2.3. Create topics to write the filtered data from Flink 
    
    ```
    avn service list ## Get kafka service name
    avn service topic-create $KAFKA_SERVICE $TOPIC_NAME1 --partitions 1 --replication 2
    avn service topic-create $KAFKA_SERVICE $TOPIC_NAME2 --partitions 1 --replication 2
    ```


    2.4. **Create application data pipeline from the console or via CLI**

    ```
    avn project list # get project name
    avn service list  # get flink service name
    avn service flink create-application $FLINK_SERVICE \
    --project $PROJECT_NAME \
    "{\"name\":\"$APP_NAME\"}" \
    ```
    
    2.5. **Add source and sink tables to read and write the data from and to Kafka topic**

    ```
    # SQL Statements 
    CREATE TABLE source_data (
        temperature DECIMAL,
        humidity DECIMAL,
        record_time STRING
        )
    WITH (
        'connector' = 'kafka',
        'properties.bootstrap.servers' = '',
        'topic' = '$TOPIC_NAME',
        'value.format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
        )

    CREATE TABLE sink_data_1 (
        temperature DECIMAL,
        humidity DECIMAL,
        record_time STRING
        )
    WITH (
        'connector' = 'kafka',
        'properties.bootstrap.servers' = '',
        'topic' = '$TOPIC_NAME1',
        'value.format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
        )

    CREATE TABLE sink_data_2 (
        temperature DECIMAL,
        humidity DECIMAL,
        record_time STRING
        )
    WITH (
        'connector' = 'kafka',
        'properties.bootstrap.servers' = '',
        'topic' = '$TOPIC_NAME2',
        'value.format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
        )
    ```

    2.6. **Execute the SQL to run data transformations**
    
    create deployment to build the data pipeline application.
    Use **STATEMENT SET** to insert data into multiple tables/topics in a single transaction

    ```
    EXECUTE STATEMENT SET
    BEGIN
    INSERT into sink_data_1 SELECT temperature, humidity, record_time FROM source_data WHERE temperature = 40;
    INSERT into sink_data_2 SELECT temperature, humidity, record_time FROM source_data WHERE temperature = 50;
    END;
    ```

    2.7. **Create data pipeline SQL application using CLI(Optional).** 
    
    In the above step, we built and executed the data pipeline app using the web console. Here are the steps if you’d like to use the command line interface.


```
avn service flink create-application-version $FLINK_SERVICE     \
  --project aiven-$PROJECT_NAME                          \
  --application-id $APPLICATION_ID        \
  "{\"name\":\"$APP_NAME\"}" \
  """{
    \"sources\": [
      {
        \"create_table\":
          \"CREATE TABLE source_data (      \
                        temperature DECIMAL, \ 
                        humidity DECIMAL,    \
                        record_time STRING    \
                    )                        \
                    WITH (                   \
                     'connector' = 'kafka',  \
                    'properties.bootstrap.servers' = '',  \
                    'topic' = '$TOPIC_NAME',  \
                    'value.format' = 'json',   \
                    'scan.startup.mode' = 'earliest-offset' \
            )\"
      } ],
    \"sinks\": [
      {
        \"create_table\":  
          \"CREATE TABLE sink_data_1 (        \
                        temperature DECIMAL,  \
                        humidity DECIMAL,    \
                        record_time STRING  \
                        )                   \
                        WITH (               \
                        'connector' = 'kafka',   \
                        'properties.bootstrap.servers' = '',  \
                        'topic' = '$TOPIC_NAME1',     \
                        'value.format' = 'json',              \
                        'scan.startup.mode' = 'earliest-offset' \
            )\",
        \"create_table\":                
          \"CREATE TABLE sink_data_2 (                \
                  temperature DECIMAL,         \
                  humidity DECIMAL,            \
                  record_time STRING           \
                  )                            \
                  WITH (                       \
                  'connector' = 'kafka',       \
                  'properties.bootstrap.servers' = '',   \
                  'topic' = '$TOPIC_NAME2',      \
                  'value.format' = 'json',              \
                  'scan.startup.mode' = 'earliest-offset'  \
              )\"
      }
      ],
    \"statement\":
      \"EXECUTE STATEMENT SET \
        BEGIN \
        INSERT into sink_data_1 SELECT temperature, humidity, record_time FROM source_data WHERE temperature = 40; \
        INSERT into sink_data_2 SELECT temperature, humidity, record_time FROM source_data WHERE temperature = 50; \
        END;\"
  }"""
```


3. ### **Observability with Grafana using M3DB and Kafka connect**

    In this exercise, we will write data from a Kafka topic to the M3db time-series database using Kafka connect.

    3.1. **Kafka Connect service:**

    Navigate to the Kafka **service** on the Aiven console, click on **connectors**, then select **Integrate standalone service, create,** and **enable** in order to set up the Kafka Connect service.

    3.2. **M3 DB service:**

    Create Aiven for M3db service from the web console using **services** menu on the landing page or using CLI.

    3.3. **Send data to M3 db using Integrations:**

    Integrate Kafka with M3DB by navigating to **Kafka connect**, click on **Integrations**, **Store metrics**, **m3db service**, and **enable**.

    3.4. **Send data to Grafana from M3DB using Integrations:**

    Integrate M3DB with Grafana by selecting **M3 DB service**, **Integrations,** and **Grafana metrics dashboard** on the Integrations page.

    3.5. **Grafana:**

    Visualize metrics by logging to the Grafana dashboard using credentials and a link available on the **services** page. Navigate to **explore**, select **M3 service** as data source, then select **cpu_usage_system or user metric**, and click **run query** to view the Graph. 

    3.6. **Dashboard and Explore:**

    You can create new dashboards and add panels with your choice of **query, metrics** and **operations** or you can just visualize available metrics using the **explore** option before adding it to a dashboard and panel.
