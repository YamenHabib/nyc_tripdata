# TLC Trip Record Data Pipline
In this project, we build a simple, powerfull and scalable data pipeline. we depends on [TLC Trip Record Data](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
The main goal of this project is to learn how to collaborate between different data science tools and FUN.
 
 
---------
### Flow Illustration

![](https://github.com/YamenHabib/nyc_tripdata/blob/main/images/flow.png)

1. First our bash script [download.sh](https://github.com/YamenHabib/nyc_tripdata/blob/main/data/download.sh) download the data as csv files. (uncomment years and months if you have good resources).
2. Using Apache NiFi we read these files, split them and publish them to the kafka topic. 
3. We have two kafka consumers:
   - Simple [Flask web application](https://github.com/YamenHabib/nyc_tripdata/tree/main/app), which just show a live map of 6 (limited by resources) trip each time
   - PySpark to visulaize and make some transformation operations on the data.
      -  Python [consumer](https://github.com/YamenHabib/nyc_tripdata/blob/main/analysis/load.py) to get the data and load most relevant features in PostgresSQL database.
      -  [Visualizing](https://github.com/YamenHabib/nyc_tripdata/blob/main/analysis/vis.ipynb) the data. 
 
 
---------
### Using:
 - Install docker.
 - Run docker compose.
  ```
  $ sudo docker-compose up
  ```
 - make kafka topic
 ```
  docker-compose exec kafka  \
    kafka-topics --create --topic ny_tripdata --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:2181
 ```
 - Upload nifi [template](https://github.com/YamenHabib/nyc_tripdata/blob/main/ny_tripdata_nifi_template.xml) and run it.
 - you need to build the database, run  ```sudo docker ps```, get the id of postgres running container then run:
    -  ``` sudo docker ecex -it $id bash ```
    -  ``` psql -U postgres ```
    -  then run the sql commands in [instructions file](https://github.com/YamenHabib/nyc_tripdata/blob/main/instructions)
 - To modify nifi workflow go to: localhost: http://localhost:8080/nifi/
 - To check the map go to: http://localhost:5000
 - To modify  PySpark notebooks go to:  http://localhost:8888/tree/work

##### Important Note: 
if you have problem with connecting the containers with each others, rememeber to chech the Name of containers' endpoint:
- List your networks:
- ``` $ sudo docker network list``` 
- Then inspect our network (its name something like this nyc_tripdata_net or nyc_tripdata_default.
- ``` $ sudo docker network inspect nyc_tripdata_default ```
- for each container you will find something like this:
```
"9abf0d8160cf9b5064c4ee08fdc977d89a45d928fb9f8076bac81e90a32a67dc": {
                "Name": "nyc_tripdata_kafka_1",
                "EndpointID": "bc3e1b32be192cdb21e4a119a195d0cf9b32b901bca3734dd9c4e16db660f4df",
                "MacAddress": "02:42:ac:14:00:09",
                "IPv4Address": "172.20.0.9/16",
                "IPv6Address": ""
            },
```
and nyc_tripdata_kafka_1 is the name that you need.
[Example](https://github.com/YamenHabib/nyc_tripdata/blob/acf206eeac957996eb5ff71ff589a66b6373e446/app/app.py#L12)

---------
### Our Nifi Workflow chart.
![NiFi Flow](https://github.com/YamenHabib/nyc_tripdata/blob/main/images/nifi%20chart.jpg)


---------
### A screenshot of the web app.
Each pair of color represents a start and end of a taxi trip.
![Map](https://github.com/YamenHabib/nyc_tripdata/blob/main/images/map.png)


