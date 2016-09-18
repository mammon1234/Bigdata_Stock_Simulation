from googlefinance import getQuotes

from kafka import KafkaProducer

import argparse
import logging
import time
import json
import schedule
import atexit

topic_name ='stock-analyzer'
kafka_broker = '192.168.99.100:9092'
logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')
logger.setLevel(logging.DEBUG)
#- TRACE DEBUG INFO WARN ERROR

def fetch_price(producer,symbol):
	price = json.dumps(getQuotes(symbol));
	#print(price)
	logger.debug('Get stock price %s', price)
	try:
		producer.send(topic=topic_name, value=price, timestamp_ms=time.time())
	except Exception:
		logger.warn('Failed to send message to kafka')
		
	logger.debug('Successfully sent data to Kafaka')

def shutdown_hook(producer):
	logger.info('preparing to shutdown,waiting for producer to flush message')
	producer.flush(10)
	logger.info('producer flush finished')
	producer.close()
	logger.info('producer closed')

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
