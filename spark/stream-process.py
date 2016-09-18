1# -read from kafka
2# - do average
3# - save data back

import atexit
import argparse
import logging
import time
import json
import sys

from kafka import KafkaProducer
from kafka.errors import KafkaError

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('stream-processing')
logger.setLevel(logging.INFO)

topic = None
target_topic = None
Brokers =None
kafka_producer = None

def shutdown_hook(producer):
	try:
		logger.info('Flushing pending messages to kafka, timeout is set to 10s')
		producer.flush(10)
		logger.info('Finish flushing pending messages to kafka')
	except KafkaError as kafka_error:
		logger.warn('Failed to flush pending messages to kafka, caused by: %s', kafka_error.message)
	finally:
	    try:
	        logger.info('Closing kafka connection')
	        producer.close(10)
	    except Exception as e:
	        logger.warn('Failed to close kafka connection, caused by: %s', e.message)

def process(timeobj,rdd):
	#do average
	num_of_records = rdd.count()
	if num_of_records == 0:
		return
	# - sum up all the price in this rdd
	# - for each rdd record, do sth[take out the LastTradingPrice,json] -> map
	# - for all the rdd record, sum up -> reduce
	price_sum = rdd.map(lambda record: float(json.loads(record[1].decode('utf-8'))[0].get('LastTradePrice'))).reduce(lambda a,b: a + b)

	average = price_sum / num_of_records
	logger.info('Received %d records from kafka, average price is %f' % (num_of_records, average))

	current_time = time.time()
	data = json.dumps({'timestamp':current_time,'average':average})
	try:
		kafka_producer.send(target_topic,value =data)
	except KafkaError as error:
		logger.warn('Failed to send average stock price to kafak, caused by %s', error.message)
    
if __name__=='__main__':
	#arguments = sys.argv
	#print arguments
	#-sys.argv is an array
	# - sys.argv[0] stream-process.py
	# -sys.argv[1] broker location
	# -sys.argv[2] topic
	if len(sys.argv)!=4:
		print ("Not enough argument [kafka broker location],[kafka topic location][target_topic]")
		exit(1)

	sc = SparkContext("local[2]","StockAveragePrice")
	sc.setLogLevel('ERROR')
	ssc = StreamingContext(sc,5)

	kafka_broker, kafka_topic, target_topic =sys.argv[1:]

	# - setup a kafka stream
	directKafkaStream = KafkaUtils.createDirectStream(ssc,[kafka_topic],{'metadata.broker.list': kafka_broker})
	directKafkaStream.foreachRDD(process)

	kafka_producer = KafkaProducer(
	    bootstrap_servers=kafka_broker
	)
	# - setup proper shutdown hook
	atexit.register(shutdown_hook, kafka_producer)
	ssc.start();
	ssc.awaitTermination()
