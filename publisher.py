import paho.mqtt.client as mqtt
import os

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
topic = 'commands/system_performance'
response_topic = 'responses/system_performance'

# Create a new MQTT client instance
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the response topic
    client.subscribe(response_topic)

def on_message(client, userdata, msg):
    feedback = msg.payload.decode()
    print(f"Received feedback:\n{feedback}")

# Set the callbacks for connection and message reception
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
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

# Start the MQTT client loop to listen for responses
client.loop_start()

# Keep the script running to receive feedback
input("Press Enter to exit...\n")

# Stop the MQTT client loop and disconnect
client.loop_stop()
client.disconnect()
