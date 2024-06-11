# MQTT System Governor

This repository contains a simple MQTT client-server setup where the server sends commands that get executed 
on each of the connected clients (subscribers), primarily used for measuring system performance and testing.
The special feature if this application is the opportunity to build and run pipelines (sequences of terminal
commands that get executed on client systems).

## Prerequisites

- Python 3.x
- `paho-mqtt` library, `colorama` library
- An MQTT broker (e.g., Mosquitto)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/SlaviXG/mqtt-system-governor.git
   cd mqtt-system-governor
   ```

2. **Install the Required Python Packages:**
   ```bash
   pip install paho-mqtt colorama
   ```
   
3. **Set Up the MQTT Broker:** <br>
   Install and run an MQTT broker (e.g., Mosquitto).
   
   ### For Ubuntu: 
   ```bash
   sudo apt-get update
   sudo apt-get install mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   ```
   
   By default, Mosquitto may only listen on the loopback interface (localhost). You need to configure it to listen on all interfaces.
   Edit the Mosquitto configuration file (usually located at /etc/mosquitto/mosquitto.conf or /etc/mosquitto/conf.d/default.conf) and add the following line:
   ```yaml
   listener 1883
   allow_anonymous true
   ```

   **Restart the Mosquitto service to apply the changes:**
   ```bash
   sudo systemctl restart mosquitto
   ```   
   
   **Open the MQTT Port on the Broker:**
   ```bash
   sudo ufw allow 1883
   ```
   
   ### For Windows:

   [Mosquitto download link.](https://mosquitto.org/download/)

## Running the example
1. **Run client machines**
   ```bash
   export MQTT_BROKER=<MQTT_BROKER_IP_ADDRESS>
   export CLIENT_ID=<client1,2,...>
   python sut.py
   ```
   (Different IDs for different clients should be used)
   
2. **Run the operator**

   On the broker machine, run:
   ```bash
   export MQTT_BROKER=localhost  # For Windows use `set MQTT_BROKER=localhost`
   python operator.py
   ```

## Configuration Guide
This guide explains how to set up the configuration file (`config.ini`) and what each configuration option does.

### [mqtt] Section

- **broker**: The address of the MQTT broker. Use `localhost` if running locally.
- **port**: The port on which the MQTT broker is listening. Default is `1883`.
- **command_topic**: The MQTT topic for sending commands to the clients. Default is `system_performance/commands`.
- **response_topic**: The MQTT topic for receiving responses from the clients. Default is `system_performance/responses`.
- **registration_topic**: The MQTT topic for client registration. Default is `clients/registration`.
- **ack_topic**: The MQTT topic for acknowledgment of client registration. Default is `clients/acknowledgment`.

### [operator] Section

- **registration_timeout**: The time (in seconds) to wait for clients to register. Default is `5`.
- **enable_pipeline_mode**: Boolean option to enable or disable pipeline mode. If `True`, the defined pipelines will be executed in order. Default is `True`.
- **enable_realtime_mode**: Boolean option to enable or disable real-time mode. If `True`, commands can be sent to clients in real-time via the terminal. Default is `True`.
- **jsonify**: Boolean option to enable or disable JSON formatting of messages. If `True`, messages will be formatted as JSON. Default is `True`.
- **colorlog**: Boolean option to enable or disable color logging in the terminal. If `True`, logs will be colored for better readability. Default is `True`.
- **save_feedback**: Boolean option to enable or disable saving feedback to a file. If `True`, feedback from clients will be saved to the specified feedback file. Default is `True`.
- **feedback_file**: The name of the file where feedback will be saved. Default is `feedback.txt`.

### Pipeline Commands

- **pipeline1, pipeline2, ...**: Define the sequence of commands to be executed as part of each pipeline. Each pipeline is executed in the order defined in the configuration file. Each command within a pipeline is separated by a `;`.

## Example Configuration

```ini
[mqtt]
broker = localhost
port = 1883
command_topic = system_performance/commands
response_topic = system_performance/responses
registration_topic = clients/registration
ack_topic = clients/acknowledgment

[operator]
registration_timeout = 5
enable_pipeline_mode = True
enable_realtime_mode = True
jsonify = True
colorlog = True
save_feedback = True
feedback_file = feedback.txt
pipeline1 = sudo cpufreq-set -r -f 600000; stress-ng --cpu 0 --timeout 60s --metrics-brief
pipeline2 = sudo cpufreq-set -r -f 1200000; stress-ng --cpu 0 --timeout 60s --metrics-brief
pipeline3 = sudo cpufreq-set -r -f 1800000; stress-ng --cpu 0 --timeout 60s --metrics-brief
```