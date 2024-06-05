import paho.mqtt.client as mqtt
import os
import subprocess

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
topic = 'commands/system_performance'

# Create a new MQTT client instance
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)


def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"Received command: {command}")

    try:
        # Execute the received command in the terminal
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Command output:\n{result.stdout}")
        if result.stderr:
            print(f"Command error:\n{result.stderr}")
    except Exception as e:
        print(f"Failed to execute command: {e}")


# Set the callbacks for connection and message reception
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker, port, 60)

# Start the MQTT client loop to listen for messages
client.loop_forever()
