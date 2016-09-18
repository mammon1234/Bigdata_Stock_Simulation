# Bigdata_Stock_Simulation


Based on Docker Environment.

Use Kafka, Cassandra, Zookeeper,Spark,Redis and NodeJS to constuct the whole system.

Kafka can be use to produce data stream
One data source is fetch from yahoo finance, get certain stock every 1 sec.
The other data is random value to get large data stream source.

the cassandra will store a copy for the data.

zookeeper will store the metadata of kafka (like broker host)

spark is used to get the average of data stream and return the average result to the kafka.

Redis is get the data from kafka and send it to nodejs

And the result can be visulized on localhost:3000.

