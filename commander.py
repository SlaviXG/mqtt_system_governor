import argparse
import paho.mqtt.client as mqtt
import configparser
import os
import json
import time


class BaseCommander:
    def __init__(self,
                 broker,
                 port,
                 command_loader_topic,
                 response_topic,
                 jsonify):
        self._broker = broker
        self._port = port
        self._command_loader_topic = command_loader_topic
        self._response_topic = response_topic
        self._jsonify = jsonify
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self._client.subscribe(self._response_topic)

    def on_message(self, client, userdata, msg):
        feedback = msg.payload.decode()
        if self._jsonify:
            try:
                feedback = json.loads(feedback)
                print(f"Received feedback:\n{json.dumps(feedback, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON feedback: {e}\nRaw feedback: {feedback}")
        else:
            print(f"Received feedback:\n{feedback}")

    def connect(self):
        self._client.connect(self._broker, self._port, keepalive=60)
        self._client.loop_start()

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()

    def send_command(self, client_id, command):
        if client_id.lower() == 'all':
            client_id = 'all'
        if self._jsonify:
            message = json.dumps({"client_id": client_id, "command": command})
        else:
            message = f"{client_id}|{command}"
        self._client.publish(self._command_loader_topic, message)
        print(f"Sent command to {client_id}: {command}")


def init_commander(config_path: os.path) -> BaseCommander:
    config = configparser.ConfigParser()
    config.read(config_path)
    broker = os.getenv('MQTT_BROKER') or config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_loader_topic = config['mqtt']['command_loader_topic']
    response_topic = config['mqtt']['response_topic']
    jsonify = config.getboolean('commander', 'jsonify')

    return BaseCommander(broker, port, command_loader_topic, response_topic, jsonify)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Commander for sending commands to clients.")
    parser.add_argument('--config', type=str, default='config.ini', help='Path to the configuration file.')
    args = parser.parse_args()

    commander = init_commander(args.config)
    commander.connect()

    try:
        while True:
            client_id = input("Enter the client ID (or 'all' to send to all clients): ")
            command = input("Enter the command to send: ")
            commander.send_command(client_id, command)
            time.sleep(1)  # Add a small delay to ensure commands are processed
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        commander.disconnect()
