import paho.mqtt.client as mqtt
import os

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
topic = 'commands/system_performance'

# Create a new MQTT client instance
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


# Connect to the MQTT broker
client.on_connect = on_connect
client.connect(broker, port, 60)

# Define performance measurement commands
commands = [
    'echo CPU Usage: && top -b -n1 | grep "Cpu(s)"',
    'echo Memory Usage: && free -m',
    'echo Disk Usage: && df -h'
]

# Publish commands to the topic
for command in commands:
    client.publish(topic, command)
    print(f"Published command: {command}")

# Disconnect from the broker
client.disconnect()
