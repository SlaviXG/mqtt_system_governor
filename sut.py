import argparse
import paho.mqtt.client as mqtt
import configparser
import subprocess
import os
import time
import json
from queue import Queue, Empty
from threading import Thread, Event
from datetime import datetime
import color_log


class SUT:
    def __init__(self, client_id: str,
                 broker: str,
                 port: int,
                 command_topic: str,
                 response_topic: str,
                 registration_topic: str,
                 ack_topic: str,
                 jsonify: bool,
                 colorlog: bool,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_id = client_id
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._registration_topic = registration_topic
        self._ack_topic = ack_topic
        self._jsonify = jsonify
        self._colorlog = colorlog
        color_log.enable_color_logging(self._colorlog)
        self._client = mqtt.Client(client_id=client_id)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._command_queue = Queue()
        self._stop_event = Event()
        self._ack_received = Event()

        # Start the command processing thread
        self._worker_thread = Thread(target=self._process_commands)
        self._worker_thread.start()

        # Start the registration thread
        self._registration_thread = Thread(target=self._send_registration)
        self._registration_thread.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            color_log.log_info(f"Connected successfully to {self._broker}:{self._port}")
            self._client.subscribe(self._command_topic)
            self._client.subscribe(self._ack_topic)
        else:
            color_log.log_error(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        if msg.topic == self._ack_topic:
            if message == self._client_id:
                color_log.log_info(f"Received acknowledgment for {self._client_id}")
                self._ack_received.set()
        else:
            if self._jsonify:
                try:
                    data = json.loads(message)
                    msg_client_id = data['client_id']
                    command = data['command']
                except json.JSONDecodeError as e:
                    color_log.log_error(f"Failed to decode JSON message: {e}")
                    return
            else:
                msg_client_id, command = message.split('|', 1)

            if msg_client_id == self._client_id:
                color_log.log_warning(f"Received command for {self._client_id}: {command}")
                self._command_queue.put(command)

    def _send_registration(self):
        time.sleep(0.5)  # Wait for starting execution of other threads
        while not self._ack_received.is_set():
            self._client.publish(self._registration_topic, self._client_id)
            color_log.log_info(f"Sent registration for {self._client_id}")
            time.sleep(5)  # Wait before resending registration

    def _process_commands(self):
        while not self._stop_event.is_set():
            try:
                command = self._command_queue.get(timeout=1)  # Non-blocking get with timeout
            except Empty:
                continue  # Loop again if no command is received
            if command is None:
                break
            color_log.log_info(f"Executing command: {command}")
            try:
                start_time = datetime.now()
                start_unix = start_time.timestamp()
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                end_time = datetime.now()
                end_unix = end_time.timestamp()
                output = result.stdout
                error = result.stderr
                feedback = {
                    "client_id": self._client_id,
                    "command": command,
                    "start_time": f"{start_unix}",
                    "end_time": f"{end_unix}",
                    "output": output,
                    "error": error if error else 'None'
                } if self._jsonify else (
                    f"Client: {self._client_id}\n"
                    f"Command: {command}\n"
                    f"Start Time: {start_unix}\n"
                    f"End Time: {end_unix}\n"
                    f"Output: {output}\n"
                    f"Error: {error if error else 'None'}"
                )
                self._client.publish(self._response_topic, json.dumps(feedback) if self._jsonify else feedback)
            except Exception as e:
                end_time = datetime.now()
                end_unix = end_time.timestamp()
                error_feedback = {
                    "client_id": self._client_id,
                    "command": command,
                    "start_time": f"{start_unix}",
                    "end_time": f"{end_unix}",
                    "error": f"Failed to execute command: {e}"
                } if self._jsonify else (
                    f"Client: {self._client_id}\n"
                    f"Command: {command}\n"
                    f"Start Time: {start_unix}\n"
                    f"End Time: {end_unix}\n"
                    f"Error: Failed to execute command: {e}"
                )
                self._client.publish(self._response_topic,
                                     json.dumps(error_feedback) if self._jsonify else error_feedback)
            self._command_queue.task_done()

    def run(self):
        color_log.log_info(f"Attempting to connect to broker at {self._broker}:{self._port}")
        try:
            self._client.connect(self._broker, self._port, 60)
        except Exception as e:
            color_log.log_error(f"Connection to broker failed: {e}")
        self._client.loop_start()

    def stop(self):
        self._stop_event.set()
        self._command_queue.put(None)
        self._worker_thread.join()
        self._registration_thread.join()
        self._client.loop_stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="System Under Test (SUT) for processing commands.")
    parser.add_argument('--config', type=str, default='config.ini', help='Path to the configuration file.')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    broker = os.getenv('MQTT_BROKER') if os.getenv('MQTT_BROKER') is not None else config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']
    registration_topic = config['mqtt']['registration_topic']
    ack_topic = config['mqtt']['ack_topic']
    jsonify = config.getboolean('operator', 'jsonify')
    colorlog = config.getboolean('operator', 'colorlog')
    client_id = os.getenv('CLIENT_ID') or 'client1'  # Default to 'client1' if CLIENT_ID not set
    sut = SUT(client_id, broker, port, command_topic, response_topic, registration_topic, ack_topic, jsonify, colorlog)
    try:
        sut.run()
    except KeyboardInterrupt:
        sut.stop()
