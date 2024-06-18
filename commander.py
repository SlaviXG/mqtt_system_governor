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
        if self._jsonify:
            message = json.dumps({"client_id": client_id, "command": command})
        else:
            message = f"{client_id}|{command}"
        self._client.publish(self._command_loader_topic, message)
        print(f"Sent command to {client_id}: {command}")


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    broker = os.getenv('MQTT_BROKER') or config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_loader_topic = config['mqtt']['command_loader_topic']
    response_topic = config['mqtt']['response_topic']
    jsonify = config.getboolean('commander', 'jsonify')

    commander = BaseCommander(broker, port, command_loader_topic, response_topic, jsonify)
    commander.connect()

    try:
        while True:
            client_id = input("Enter the client ID: ")
            command = input("Enter the command to send: ")
            commander.send_command(client_id, command)
            time.sleep(1)  # Add a small delay to ensure commands are processed
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        commander.disconnect()
