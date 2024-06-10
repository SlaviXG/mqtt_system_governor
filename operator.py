import paho.mqtt.client as mqtt
import configparser
import os
from threading import Lock, Thread
import time


class Operator:
    def __init__(self,
                 broker: str,
                 port: int,
                 command_topic: str,
                 response_topic: str,
                 registration_topic: str,
                 ack_topic: str,
                 registration_timeout: int,
                 pipelines: dict,
                 pipeline_mode: bool,
                 realtime_mode: bool,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._registration_topic = registration_topic
        self._ack_topic = ack_topic
        self._registration_timeout = registration_timeout
        self._pipelines = pipelines
        self._pipeline_mode = pipeline_mode
        self._realtime_mode = realtime_mode
        self._clients = set()
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._lock = Lock()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self._client.subscribe(self._registration_topic)
        self._client.subscribe(self._response_topic)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        if topic == self._registration_topic:
            with self._lock:
                if payload not in self._clients:
                    self._clients.add(payload)
                    print(f"Registered client: {payload}")
                    self._client.publish(self._ack_topic, payload)
        elif topic == self._response_topic:
            print(f"Received feedback:\n{payload}")

    def run(self):
        self._client.connect(self._broker, self._port, keepalive=60)
        self._client.loop_start()

        last_registration_time = time.time()
        print("Waiting for clients to register...")
        while True:
            with self._lock:
                if self._clients:
                    if time.time() - last_registration_time > self._registration_timeout:
                        break
                else:
                    last_registration_time = time.time()

        print(f"Registered clients: {', '.join(self._clients)}")

        if self._pipeline_mode:
            self.run_pipelines()

        if self._realtime_mode:
            self.run_realtime_mode()

        input("Press Enter to exit...\n")

        self._client.loop_stop()
        self._client.disconnect()

    def run_pipelines(self):
        print("Running pipelines...")
        with self._lock:
            for pipeline_name, pipeline_commands in self._pipelines.items():
                for client_id in self._clients:
                    for command in pipeline_commands.split(';'):
                        message = f"{client_id}|{command.strip()}"
                        self._client.publish(self._command_topic, message)
                        print(f"Published command to {client_id}: {command.strip()}")
                        time.sleep(1)  # Add a delay to ensure commands are processed sequentially

    def run_realtime_mode(self):
        print("Entering real-time command mode...")
        while True:
            command = input("Enter command to send to all clients (or 'exit' to quit): ")
            if command.lower() == 'exit':
                break
            with self._lock:
                for client_id in self._clients:
                    message = f"{client_id}|{command.strip()}"
                    self._client.publish(self._command_topic, message)
                    print(f"Published command to {client_id}: {command.strip()}")


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    broker = os.getenv('MQTT_BROKER') or config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']
    registration_topic = config['mqtt']['registration_topic']
    ack_topic = config['mqtt']['ack_topic']
    registration_timeout = int(config['operator']['registration_timeout'])
    pipeline_mode = config.getboolean('operator', 'pipeline_mode')
    realtime_mode = config.getboolean('operator', 'realtime_mode')
    pipelines = {k: v for k, v in config['operator'].items() if k.startswith('pipeline')}
    operator = Operator(broker,
                        port,
                        command_topic,
                        response_topic,
                        registration_topic,
                        ack_topic,
                        registration_timeout,
                        pipelines,
                        pipeline_mode,
                        realtime_mode)
    operator.run()
