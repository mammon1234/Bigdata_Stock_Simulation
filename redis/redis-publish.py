from kafka import KafkaConsumer

import argparse
import atexit
import logging
import redis

# default kafka topic to write to
topic_name = 'stock-analyzer'
#default kafka croker location
kafka_broker = '127.0.0.1:9092'

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format = logger_format)
logger = logging.getLogger('redis-publisher')
logger.setLevel(logging.DEBUG)

def shutdown_hook(kafka_consumer):
	logger.info('Shurdown kafka consumer')
	kafka_consumer.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('topic_name',help='the kafka topic consume form')
	parser.add_argument('kafka_broker',help='the location of the kafka_broker')
	parser.add_argument('redis_channel',help='the redis redis_channel to publish to')
	parser.add_argument('redis_host',help='the location of the redis server')
	parser.add_argument('redis_port',help='the redis port')
	#parse arguments
	args = parser.parse_args()
	topic_name=args.topic_name
	kafka_broker=args.kafka_broker
	redis_channel=args.redis_channel
	redis_host=args.redis_host
	redis_port=args.redis_port
	#instantiate a simple kafka consumer
	kafak_consumer = KafkaConsumer(
		topic_name,
		bootstrap_servers=kafka_broker
	)
	#instantiate a redis client
	redis_client = redis.StrictRedis(host=redis_host,port=redis_port)
	atexit.register(shutdown_hook,kafak_consumer)
	for msg in kafak_consumer:
		logger.info('Received new data from kafka %s' %str(msg))
		redis_client.publish(redis_channel,msg.value)
