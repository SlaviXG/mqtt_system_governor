import paho.mqtt.client as mqtt
import os

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
topic = 'commands/system_performance'
response_topic = 'responses/system_performance'

# Define performance measurement commands
commands = [
    'echo CPU Usage: && top -b -n1 | grep "Cpu(s)"',
    'echo Memory Usage: && free -m',
    'echo Disk Usage: && df -h'
]


class Operator(mqtt.Client):
    def __init__(self,
                 broker: str,
                 port: int,
                 topic: str,
                 response_topic: str,
                 commands: list[str],
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # Establish client configuration
        self._broker = broker
        self._port = port
        self._topic = topic
        self._response_topic = response_topic
        self._commands = commands

        # # Set the callbacks for connection and message reception
        # self.on_connect = self._on_connect
        # self.on_message = self._on_message

    def _on_connect(self, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to the response topic
        self.subscribe(self._response_topic)

    def _on_message(self, userdata, msg):
        feedback = msg.payload.decode()
        print(f"Received feedback:\n{feedback}")

    def run(self):
        # Connect to the MQTT broker
        self.connect(self._broker, self._port, keepalive=60)

        # Publish commands to the topic
        for command in commands:
            self.publish(topic, command)
            print(f"Published command: {command}")

        # Start the MQTT client loop to listen for responses
        self.loop_start()

        # Keep the script running to receive feedback
        input("Press Enter to exit...\n")

        # Stop the MQTT client loop and disconnect
        self.loop_stop()
        self.disconnect()


if __name__ == '__main__':
    # Create a new client instance
    operator = Operator(broker, port, topic, response_topic, commands)
    # Run System Operator
    operator.run()
