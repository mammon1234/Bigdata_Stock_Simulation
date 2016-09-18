Make sure the spark in system path

Use command like this 
spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.0.0.jar stream-process.py 192.168.99.100:9092 stock-analyzer average-stock-price
