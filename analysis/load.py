import psycopg2
from kafka import KafkaConsumer, TopicPartition
from json import loads
import time
from pyspark.sql import SparkSession
from multiprocessing import Process, Manager
import json

def get_most_relevant_feature(msg):
    data = {}
    data['vendor_name'] = msg['vendor_name']
    data['Trip_Pickup_DateTime'] = msg['Trip_Pickup_DateTime']
    data['Trip_Dropoff_DateTime'] = msg['Trip_Dropoff_DateTime']
    data['Trip_Distance'] = msg['Trip_Distance']
    data['Start_Lon'] = msg['Start_Lon']
    data['Start_Lat'] = msg['Start_Lat']
    data['End_Lon'] = msg['End_Lon']
    data['End_Lat'] = msg['End_Lat']
    return data

def insert_trip(conn,
                cur,
                vendor_name, 
                Trip_Pickup_DateTime, 
                Trip_Dropoff_DateTime,
                Trip_Distance,
                Start_Lon,
                Start_Lat,
                End_Lon,
                End_Lat):

    sql = """INSERT INTO trips (vendor_name, 
                                Trip_Pickup_DateTime, 
                                Trip_Dropoff_DateTime, 
                                Trip_Distance, 
                                Start_Lon, 
                                Start_Lat, 
                                End_Lon, 
                                End_Lat)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"""
    
    # execute the INSERT statement
    cur.execute(sql, (vendor_name, 
                      Trip_Pickup_DateTime, 
                      Trip_Dropoff_DateTime,
                      Trip_Distance,
                      Start_Lon,
                      Start_Lat,
                      End_Lon,
                      End_Lat,))
    # get the generated id back
    # vendor_id = cur.fetchone()[0]
    # commit the changes to the database
    conn.commit()

def consumeData(consumer, data_queue):
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="docker-compose_db_1",
                                database="postgres",
                                user="postgres",
                                password="postgres1234")
        # create a new cursor
        cur = conn.cursor()
        
        for message in consumer:
            try:
                msg = json.loads(message.value.decode("utf-8"))
                data = get_most_relevant_feature(msg)
                insert_trip(conn, cur, *list(data.values()))
                data_queue.put(data)
                print("Progress: {}".format(data_queue.qsize()), end="\r", flush=True)
            except Exception as e:
                print(data)
                print(e)
                pass
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# using Process

def get_insert_parallel():
    consumer = KafkaConsumer('ny_tripdata',
                             bootstrap_servers=['nyc_tripdata_kafka_1:29092'],
                             auto_offset_reset='earliest',
                             group_id='group')

    manager = Manager()
    data_queue = manager.Queue()
    t1 = Process(target=consumeData, args=(consumer, data_queue, ))
    t1.start()


def get_insert():
    print("Starting Loading data into PostgresSQL")
    try:
        count = 0
        consumer = KafkaConsumer('ny_tripdata',
                                 bootstrap_servers=['nyc_tripdata_kafka_1:29092'],
                                 auto_offset_reset='earliest',
                                 group_id='group')

        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="nyc_tripdata_db_1",
                                database="postgres",
                                user="postgres",
                                password="postgres1234")
        # create a new cursor
        cur = conn.cursor()

        for message in consumer:
            try:
                msg = json.loads(message.value.decode("utf-8"))
                data = get_most_relevant_feature(msg)
                insert_trip(conn, cur, *list(data.values()))
                print("Number of inserted records: {}".format(count + 1), end="\r", flush=True)
                count += 1
            except Exception as e:
                print(data)
                print(e)
                pass

        # close communication with the database
        cur.close()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    get_insert()