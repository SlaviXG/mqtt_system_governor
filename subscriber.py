import paho.mqtt.client as mqtt
import os
import subprocess

# Read the broker address from the environment variable
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
topic = 'commands/system_performance'
response_topic = 'responses/system_performance'

print(f"Attempting to connect to broker at {broker}:{port}")

# Create a new MQTT client instance
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected successfully to {broker}:{port}")
        client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}")


def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"Received command: {command}")

    try:
        # Execute the received command in the terminal
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout
        error = result.stderr
        # Publish the command output to the response topic
        feedback = f"Command: {command}\nOutput: {output}\nError: {error if error else 'None'}"
        client.publish(response_topic, feedback)
    except Exception as e:
        error_feedback = f"Failed to execute command: {e}"
        client.publish(response_topic, error_feedback)


# Set the callbacks for connection and message reception
client.on_connect = on_connect
client.on_message = on_message

try:
    # Connect to the MQTT broker
    client.connect(broker, port, 60)
except Exception as e:
    print(f"Connection to broker failed: {e}")

# Start the MQTT client loop to listen for messages
client.loop_forever()
