import paho.mqtt.client as mqtt
import configparser
import subprocess
import os


class SUT:
    def __init__(self,
                 broker: str,
                 port: int,
                 command_topic: str,
                 response_topic: str,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # Establish configuration
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._client = mqtt.Client()

        # Set the callbacks for connection and message reception
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected successfully to {broker}:{port}")
            self._client.subscribe(self._command_topic)
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        command = msg.payload.decode()
        print(f"Received command: {command}")

        try:
            # Execute the received command in the terminal
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout
            error = result.stderr
            # Publish the command output to the response topic
            feedback = f"Command: {command}\nOutput: {output}\nError: {error if error else 'None'}"
            self._client.publish(response_topic, feedback)
        except Exception as e:
            error_feedback = f"Failed to execute command: {e}"
            self._client.publish(response_topic, error_feedback)

    def run(self):
        print(f"Attempting to connect to broker at {broker}:{port}")
        try:
            # Connect to the MQTT broker
            self._client.connect(broker, port, 60)
        except Exception as e:
            print(f"Connection to broker failed: {e}")

        # Start the MQTT client loop to listen for messages
        self._client.loop_forever()


if __name__ == '__main__':
    # Read configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    broker = os.getenv('MQTT_BROKER') if os.getenv('MQTT_BROKER') is not None else config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']

    # Create a new MQTT client instance
    sut = SUT(broker, port, command_topic, response_topic)

    # Run System Under Test
    sut.run()
