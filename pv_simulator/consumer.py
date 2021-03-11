# subscriber.py
import pika
import os
import logging
from datetime import datetime

import time
import csv


class Subscriber:

    def __init__(self, queue_name, binding_key, config, external_handler=None):
        self.queue_name = queue_name
        self.binding_key = binding_key
        self.config = config
        self.connection = self._create_connection()
        self.external_handler = external_handler

    def __del__(self):
        self.connection.close()

    def _create_connection(self):
        credentials = pika.PlainCredentials(self.config['username'],
                                            self.config['password'])
        parameters = pika.ConnectionParameters(self.config['host'],
                                               self.config['port'],
                                               '/',
                                               credentials)
        return pika.BlockingConnection(parameters)

    def on_message_callback(self, channel, method, properties, body):
        binding_key = method.routing_key
        if self.external_handler is not None:
            self.external_handler(binding_key, body)

        logging.warning('received: %s' % body)
        print("received new message for -" + binding_key)

    def setup(self):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.config['exchange'],
                                 exchange_type='topic')
        # create or check queue
        channel.queue_declare(queue=self.queue_name)
        # binds to queue
        channel.queue_bind(queue=self.queue_name,
                           exchange=self.config['exchange'],
                           routing_key=self.binding_key)
        channel.basic_consume(queue=self.queue_name,
                              on_message_callback=self.on_message_callback,
                              auto_ack=True)
        print(' [*] Waiting for data for ' + self.queue_name + '. To exit press CTRL+C')
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()


def save_to_csv(file_addr, cols, rows_lst, append=True):
    try:
        open(file_addr)
    except IOError:
        append = False

    write_mode = 'a' if append else 'w'
    with open(file_addr, write_mode) as csvout:
        writer = csv.writer(csvout)
        if not append:
            writer.writerow(cols)
        for row in rows_lst:
            writer.writerow(row)
    return True


def pv_output_handler(binding_key, body):
    body = body.decode("utf-8")
    try:
        value = float(body)
    except ValueError:  # bad value
        return

    pv = value / 1000
    row_lst = list()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_lst.append([ts, body, pv, pv + value])
    save_to_csv('output.csv',
                ['timestamp', 'meter', 'pv', 'pv_meter'],
                row_lst)
    return True


if __name__ == '__main__':
    host = os.environ.get('RABBIT_HOST', 'localhost')
    port = os.environ.get('RABBIT_PORT', '5672')
    username = os.environ.get('RABBIT_USER', 'guest')
    password = os.environ.get('RABBIT_PASS', 'guest')
    exchange = os.environ.get('RABBIT_CHANNEL', 'my_exchange')
    config = dict(host=host, port=port, exchange=exchange,
                  username=username, password=password)
    # waiting for rabbit service to be connected
    time.sleep(10)
    logging.basicConfig(filename='logfile.log', format='%(asctime)s - %(message)s')
    logging.warning('Started')
    subscriber = Subscriber('pv_simulator', 'meter_value', config,
                            external_handler=pv_output_handler)
    subscriber.setup()
