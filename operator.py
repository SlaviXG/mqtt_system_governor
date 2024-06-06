import paho.mqtt.client as mqtt
import configparser
import os
from threading import Lock


class Operator:
    def __init__(self, broker: str, port: int, command_topic: str, response_topic: str, registration_topic: str,
                 commands: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._registration_topic = registration_topic
        self._commands = commands
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
                self._clients.add(payload)
                print(f"Registered client: {payload}")
        elif topic == self._response_topic:
            print(f"Received feedback:\n{payload}")

    def run(self):
        self._client.connect(self._broker, self._port, keepalive=60)
        self._client.loop_start()

        input("Press Enter to start sending commands...\n")

        while not self._clients:
            print("Waiting for clients to register...")
            self._client.loop(timeout=1.0)  # Wait for clients to register

        with self._lock:
            for client_id in self._clients:
                for command in self._commands:
                    message = f"{client_id}|{command}"
                    self._client.publish(self._command_topic, message)
                    print(f"Published command to {client_id}: {command}")

        input("Press Enter to exit...\n")

        self._client.loop_stop()
        self._client.disconnect()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    broker = os.getenv('MQTT_BROKER') or config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']
    registration_topic = config['mqtt']['registration_topic']
    commands = [c.strip() for c in config['operator']['commands'].split(';')]
    operator = Operator(broker, port, command_topic, response_topic, registration_topic, commands)
    operator.run()
