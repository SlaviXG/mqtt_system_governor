import paho.mqtt.client as mqtt
import configparser
import os

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883

# Define performance measurement commands
commands = [
    'echo CPU Usage: && top -b -n1 | grep "Cpu(s)"',
    'echo Memory Usage: && free -m',
    'echo Disk Usage: && df -h'
]


class Operator:
    def __init__(self,
                 broker: str,
                 port: int,
                 command_topic: str,
                 response_topic: str,
                 commands: list[str],
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # Establish configuration
        self._broker = broker
        self._port = port
        self._command_topic = command_topic
        self._response_topic = response_topic
        self._commands = commands
        self._client = mqtt.Client()

        # Set the callbacks for connection and message reception
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to the response topic
        self._client.subscribe(self._response_topic)

    def on_message(self, client, userdata, msg):
        feedback = msg.payload.decode()
        print(f"Received feedback:\n{feedback}")

    def run(self):
        # Connect to the MQTT broker
        self._client.connect(self._broker, self._port, keepalive=60)

        # Publish commands to the topic
        for command in commands:
            self._client.publish(self._command_topic, command)
            print(f"Published command: {command}")

        # Start the MQTT client loop to listen for responses
        self._client.loop_start()

        # Keep the script running to receive feedback
        input("Press Enter to exit...\n")

        # Stop the MQTT client loop and disconnect
        self._client.loop_stop()
        self._client.disconnect()


if __name__ == '__main__':
    # Read configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    broker = os.getenv('MQTT_BROKER') if os.getenv('MQTT_BROKER') is not None else config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_topic = config['mqtt']['command_topic']
    response_topic = config['mqtt']['response_topic']

    commands = [c.strip() for c in config['operator']['commands'].split(';')]

    # Create a new client instance
    operator = Operator(broker, port, command_topic, response_topic, commands)
    # Run System Operator
    operator.run()
