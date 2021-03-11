# publisher.py
import pika
import time
from random import randint
import os


class Publisher:
    def __init__(self, config, queue_name):
        self.config = config
        self.queue_name = queue_name

    def publish(self, routing_key, message):
        connection = self._create_connection()
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name)
        # Publishes message to the exchange with the given routing key
        channel.basic_publish(exchange=self.config['exchange'],
                              routing_key=routing_key, body=message)
        print("[x] Sent message %r for %r" % (message, routing_key))

    def _create_connection(self):
        credentials = pika.PlainCredentials(self.config['username'],
                                            self.config['password'])
        parameters = pika.ConnectionParameters(self.config['host'],
                                               self.config['port'],
                                               '/',
                                               credentials)
        return pika.BlockingConnection(parameters)


if __name__ == '__main__':
    host = os.environ.get('RABBIT_HOST', 'localhost')
    port = os.environ.get('RABBIT_PORT', '5672')
    username = os.environ.get('RABBIT_USER', 'guest')
    password = os.environ.get('RABBIT_PASS', 'guest')
    exchange = os.environ.get('RABBIT_CHANNEL', 'my_exchange')
    config = dict(host=host, port=port, exchange=exchange,
                  username=username, password=password)
    # waiting for rabbitmq service to be run
    time.sleep(10)
    publisher = Publisher(config, 'pv_simulator')
    while True:
        time.sleep(5)
        publisher.publish('meter_value', "%s" % randint(0, 9000))
