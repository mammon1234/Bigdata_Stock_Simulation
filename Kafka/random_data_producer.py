from googlefinance import getQuotes
from kafka import KafkaProducer
from kafka.errors import KafkaError,KafkaTimeoutError
import argparse
import logging
import time
import json
import schedule
import atexit
import datetime
import random

topic_name ='stock-analyzer'
kafka_broker = '192.168.99.100:9092'

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')
logger.setLevel(logging.DEBUG)
#- TRACE DEBUG INFO WARN ERROR

def fetch_price(producer,symbol):
	
	#print(price)
	logger.debug('Start to fetch stock price for %s', symbol)
	try:
		price = random.randint(30,120);
		timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%MZ')
		payload = ('[{"StockSymbol":"APPL","LastTradePrice": %d,"LastTradeDateTime":"%s"}]' %(price,timestamp)).encode('utf-8')
		logger.debug('Retrieved stock info %s',price)
		producer.send(topic=topic_name,value = payload, timestamp_ms=time.time())
		logger.debug('Sent stock price for %s to Kafka', symbol)
	except KafkaTimeoutError as timeout_error:
		logger.warn('Failed to end stock proce for %s to kafka, caused by: %s',(symbol,timeout_error.message))
	except Exception:
		logger.warn('Failed to fetch stock price for %s', symbol)
		

def shutdown_hook(producer):
	logger.info('preparing to shutdown,waiting for producer to flush message')
	producer.flush(10)
	logger.info('producer flush finished')
	producer.close()
	logger.info('producer closed')
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
			logger.warn('Failed to close kafka connection, caused by: %s',e.message)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('symbol',help ='the stock symbol')
	parser.add_argument('topic_name',help='the kafka topic to push to')
	parser.add_argument('kafka_broker',help='location of kafka broker')

	args = parser.parse_args()
	symbol = args.symbol
	topic_name = args.topic_name
	kafka_broker =args.kafka_broker

	producer = KafkaProducer(bootstrap_servers=kafka_broker)
	#producer.send(topic=topic_name, value='Helloworld', timestamp_ms=time.time())
	#fetch_price(producer,symbol)
	
	# -schedule and run every second
	schedule.every(1).second.do(fetch_price,producer,symbol)

	# -register shutdown hook
	atexit.register(shutdown_hook,producer)
	# -kick start
	while True:
		schedule.run_pending()
		time.sleep(1)
