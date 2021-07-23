from flask import Flask, render_template, Response
from kafka import KafkaConsumer, TopicPartition
import time
import json

class Consumer:
    def __init__(self):
        self.consumer = None

    def _get_kafka_consumer(self):
        return  KafkaConsumer('ny_tripdata',
                             bootstrap_servers=['nyc_tripdata_kafka_1:29092'],
                             auto_offset_reset='earliest',
                             group_id='flask_group') 

    def get_kafka_consumer(self):
        if self.consumer is not None:
            return self.consumer
        else:
            self.consumer = self._get_kafka_consumer()
            return self.consumer

consumerKafka = Consumer()


app = Flask(__name__)

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

def get_most_relevant_feature(msg):
    data = {}
    data['Start_Lon'] = msg['Start_Lon']
    data['Start_Lat'] = msg['Start_Lat']
    data['End_Lon'] = msg['End_Lon']
    data['End_Lat'] = msg['End_Lat']
    return data

@app.route('/')
def index():
    return(render_template('index.html'))

#Consumer API
@app.route('/taxi')
def get_messages():
    consumer = consumerKafka.get_kafka_consumer()

    def events():
            for message in consumer:
                msg = json.loads(message.value.decode("utf-8"))
                data =  get_most_relevant_feature(msg)
                data = json.dumps(data)
                time.sleep(2)
                yield 'data:{0}\n\n'.format(data)
    return Response(events(), mimetype="text/event-stream")

#Consumer API
@app.route('/taxi2')
def get_messages2():
    consumer = consumerKafka.get_kafka_consumer()
    topic = TopicPartition(topic='ny_tripdata', partition=0)
    def events():
            while True:
                res = consumer.poll(max_records=6)
                data = []
                for message in res[topic]:
                    msg  = json.loads(message.value.decode("utf-8"))
                    tmp =  get_most_relevant_feature(msg)
                    data.append(tmp)
                    # print(data)
                data = json.dumps(data)
                time.sleep(2)
                yield 'data:{0}\n\n'.format(data)
    return Response(events(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
    
    