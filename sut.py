import paho.mqtt.client as mqtt
import configparser
import subprocess
import os
from queue import Queue
from threading import Thread, Event


class SUT:
    def __init__(self, client_id: str, broker: str, port: int, command_topic: str, response_topic: str, registration_topic: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_id = client_id
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._registration_topic = registration_topic
        self._client = mqtt.Client(client_id=client_id)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._command_queue = Queue()
        self._stop_event = Event()

        # Start the command processing thread
        self._worker_thread = Thread(target=self._process_commands)
        self._worker_thread.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected successfully to {self._broker}:{self._port}")
            self._client.subscribe(self._command_topic)
            self._client.publish(self._registration_topic, self._client_id)
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        msg_client_id, command = message.split('|', 1)
        if msg_client_id == self._client_id:
            print(f"Received command for {self._client_id}: {command}")
            self._command_queue.put(command)

    def _process_commands(self):
        while not self._stop_event.is_set():
            command = self._command_queue.get()
            if command is None:
                break
            print(f"Executing command: {command}")
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout
                error = result.stderr
                feedback = f"Client: {self._client_id}\nCommand: {command}\nOutput: {output}\nError: {error if error else 'None'}"
                self._client.publish(self._response_topic, feedback)
            except Exception as e:
                error_feedback = f"Client: {self._client_id}\nCommand: {command}\nError: Failed to execute command: {e}"
                self._client.publish(self._response_topic, error_feedback)
            self._command_queue.task_done()

    def run(self):
        print(f"Attempting to connect to broker at {self._broker}:{self._port}")
        try:
            self._client.connect(self._broker, self._port, 60)
        except Exception as e:
            print(f"Connection to broker failed: {e}")
        self._client.loop_forever()

    def stop(self):
        self._stop_event.set()
        self._command_queue.put(None)
        self._worker_thread.join()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    broker = os.getenv('MQTT_BROKER') if os.getenv('MQTT_BROKER') is not None else config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']
    registration_topic = config['mqtt']['registration_topic']
    client_id = os.getenv('CLIENT_ID') or 'client1'  # Default to 'client1' if CLIENT_ID not set
    sut = SUT(client_id, broker, port, command_topic, response_topic, registration_topic)
    try:
        sut.run()
    except KeyboardInterrupt:
        sut.stop()
