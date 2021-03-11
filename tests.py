import unittest
from meter.publisher import Publisher
from pv_simulator.consumer import Subscriber
import time
import logging
import pika
import os


class TestPVSimulator(unittest.TestCase):

    def test_after_publishing_one_message_in_q(self):
        # publishing
        host = os.environ.get('RABBIT_HOST', 'localhost')
        port = os.environ.get('RABBIT_PORT', '5672')
        username = os.environ.get('RABBIT_USER', 'guest')
        password = os.environ.get('RABBIT_PASS', 'guest')
        exchange = os.environ.get('RABBIT_CHANNEL', 'test_exchange')
        config = dict(host=host, port=port, exchange=exchange,
                      username=username, password=password)

        publisher = Publisher(config, 'pv_simulator')

        subscriber = Subscriber('pv_simulator', 'test_value', config)
        channel = subscriber.connection.channel()
        channel.queue_bind(queue='pv_simulator', exchange=config['exchange'], routing_key='test_value')
        channel.queue_purge('pv_simulator')
        publisher.publish('test_value', '1200')
        res = channel.queue_declare(
            queue="pv_simulator",
            durable=True,
            exclusive=False,
            auto_delete=False,
            passive=True
        )
        self.assertEqual(res.method.message_count, 1)
        channel.queue_purge('pv_simulator')

    def test_after_publishing_the_value(self):
        host = os.environ.get('RABBIT_HOST', 'localhost')
        port = os.environ.get('RABBIT_PORT', '5672')
        username = os.environ.get('RABBIT_USER', 'guest')
        password = os.environ.get('RABBIT_PASS', 'guest')
        exchange = os.environ.get('RABBIT_CHANNEL', 'test_exchange')
        config = dict(host=host, port=port, exchange=exchange,
                      username=username, password=password)

        publisher = Publisher(config, 'pv_simulator')
        subscriber = Subscriber('pv_simulator', 'test_value', config)
        channel = subscriber.connection.channel()
        channel.queue_bind(queue='pv_simulator', exchange=config['exchange'], routing_key='test_value')
        channel.queue_purge('pv_simulator')
        publisher.publish('test_value', '5500')
        values = channel.consume('pv_simulator')
        val = next(values)
        self.assertEqual(val[-1], b'5500')


if __name__ == '__main__':
    unittest.main()
