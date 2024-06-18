import paho.mqtt.client as mqtt
import configparser
import os
import json
import time
from threading import Lock
import color_log


class Operator:
    def __init__(self,
                 broker: str,
                 port: int,
                 command_topic: str,
                 response_topic: str,
                 registration_topic: str,
                 ack_topic: str,
                 command_loader_topic: str,
                 registration_timeout: int,
                 pipelines: dict,
                 pipeline_mode: bool,
                 realtime_mode: bool,
                 jsonify: bool,
                 colorlog: bool,
                 save_feedback: bool,
                 feedback_file: str,
                 receive_commands: bool,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._registration_topic = registration_topic
        self._ack_topic = ack_topic
        self._command_loader_topic = command_loader_topic
        self._registration_timeout = registration_timeout
        self._pipelines = pipelines
        self._pipeline_mode = pipeline_mode
        self._realtime_mode = realtime_mode
        self._jsonify = jsonify
        self._colorlog = colorlog
        self._save_feedback = save_feedback
        self._feedback_file = feedback_file
        self._receive_commands = receive_commands
        color_log.enable_color_logging(self._colorlog)
        self._clients = set()
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._lock = Lock()

    def on_connect(self, client, userdata, flags, rc):
        color_log.log_info(f"Connected with result code {rc}")
        self._client.subscribe(self._registration_topic)
        self._client.subscribe(self._response_topic)
        if self._receive_commands:
            self._client.subscribe(self._command_loader_topic)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        if topic == self._registration_topic:
            with self._lock:
                if payload not in self._clients:
                    self._clients.add(payload)
                    color_log.log_info(f"Registered client: {payload}")
                    self._client.publish(self._ack_topic, payload)
        elif topic == self._response_topic:
            color_log.log_info(f"Received feedback:\n{payload}")
            if self._save_feedback:
                self.save_feedback_to_file(payload)
        elif topic == self._command_loader_topic:
            self.handle_command_loader(payload)

    def handle_command_loader(self, payload):
        try:
            command_data = json.loads(payload)
            client_id = command_data.get('client_id')
            command = command_data.get('command')
            if client_id and command:
                color_log.log_warning(f"Published command to {client_id}: {command}")
                if self._jsonify:
                    message = json.dumps({"client_id": client_id, "command": command})
                else:
                    message = f"{client_id}|{command}"
                self._client.publish(self._command_topic, message)
            else:
                color_log.log_error("Invalid command format")
        except json.JSONDecodeError as e:
            color_log.log_error(f"Failed to decode JSON: {e}")

    def save_feedback_to_file(self, feedback: str):
        with open(self._feedback_file, 'a') as f:
            f.write(feedback + '\n')

    def run(self):
        self._client.connect(self._broker, self._port, keepalive=60)
        self._client.loop_start()

        last_registration_time = time.time()
        color_log.log_info("Waiting for clients to register...")
        while True:
            with self._lock:
                if self._clients:
                    if time.time() - last_registration_time > self._registration_timeout:
                        break
                else:
                    last_registration_time = time.time()

        color_log.log_info(f"Registered clients: {', '.join(self._clients)}")

        if self._pipeline_mode:
            self.run_pipelines()

        if self._realtime_mode:
            self.run_realtime_mode()

        input("Press Enter to exit...\n")

        self._client.loop_stop()
        self._client.disconnect()

    def run_pipelines(self):
        color_log.log_info("Running pipelines...")
        with self._lock:
            for pipeline_name, pipeline_commands in self._pipelines.items():
                for client_id in self._clients:
                    for command in pipeline_commands.split(';'):
                        command_message = command.strip()
                        if self._jsonify:
                            message = json.dumps({"client_id": client_id, "command": command_message})
                        else:
                            message = f"{client_id}|{command_message}"
                        self._client.publish(self._command_topic, message)
                        color_log.log_warning(f"Published command to {client_id}: {command_message}")
                        time.sleep(1)  # Add a delay to ensure commands are processed sequentially

    def run_realtime_mode(self):
        color_log.log_info("Entering real-time command mode...")
        while True:
            command = input("Enter command to send to all clients (or 'exit' to quit): \n")
            if command.lower() == 'exit':
                break
            with self._lock:
                for client_id in self._clients:
                    command_message = command.strip()
                    if self._jsonify:
                        message = json.dumps({"client_id": client_id, "command": command_message})
                    else:
                        message = f"{client_id}|{command_message}"
                    self._client.publish(self._command_topic, message)
                    color_log.log_warning(f"Published command to {client_id}: {command_message}")


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    broker = os.getenv('MQTT_BROKER') or config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']
    registration_topic = config['mqtt']['registration_topic']
    ack_topic = config['mqtt']['ack_topic']
    command_loader_topic = config['mqtt']['command_loader_topic']
    registration_timeout = int(config['operator']['registration_timeout'])
    pipeline_mode = config.getboolean('operator', 'enable_pipeline_mode')
    realtime_mode = config.getboolean('operator', 'enable_realtime_mode')
    jsonify = config.getboolean('operator', 'jsonify')
    colorlog = config.getboolean('operator', 'colorlog')
    save_feedback = config.getboolean('operator', 'save_feedback')
    feedback_file = config['operator']['feedback_file']
    receive_commands = config.getboolean('operator', 'receive_commands')
    pipelines = {k: v for k, v in config['operator'].items() if k.startswith('pipeline')}
    operator = Operator(broker,
                        port,
                        command_topic,
                        response_topic,
                        registration_topic,
                        ack_topic,
                        command_loader_topic,
                        registration_timeout,
                        pipelines,
                        pipeline_mode,
                        realtime_mode,
                        jsonify,
                        colorlog,
                        save_feedback,
                        feedback_file,
                        receive_commands)
    operator.run()
