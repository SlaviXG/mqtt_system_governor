import paho.mqtt.client as mqtt
import os
import subprocess

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
topic = 'commands/system_performance'
response_topic = 'responses/system_performance'


class SUT(mqtt.Client):
    def __init__(self,
                 broker: str,
                 port: int,
                 topic: str,
                 response_topic: str,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self._broker = broker
        self._port = port
        self._topic = topic
        self._response_topic = response_topic

        # # Set the callbacks for connection and message reception
        # self.on_connect = self._on_connect
        # self.on_message = self._on_message

    def _on_connect(self, userdata, flags, rc):
        if rc == 0:
            print(f"Connected successfully to {broker}:{port}")
            self.subscribe(topic)
        else:
            print(f"Connection failed with code {rc}")

    def _on_message(self, userdata, msg):
        command = msg.payload.decode()
        print(f"Received command: {command}")

        try:
            # Execute the received command in the terminal
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout
            error = result.stderr
            # Publish the command output to the response topic
            feedback = f"Command: {command}\nOutput: {output}\nError: {error if error else 'None'}"
            self.publish(response_topic, feedback)
        except Exception as e:
            error_feedback = f"Failed to execute command: {e}"
            self.publish(response_topic, error_feedback)

    def run(self):
        print(f"Attempting to connect to broker at {broker}:{port}")
        try:
            # Connect to the MQTT broker
            self.connect(broker, port, 60)
        except Exception as e:
            print(f"Connection to broker failed: {e}")

        # Start the MQTT client loop to listen for messages
        self.loop_forever()


if __name__ == '__main__':
    # Create a new MQTT client instance
    sut = SUT(broker, port, topic, response_topic)
    # Run System Under Test
    sut.run()