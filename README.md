# MQTT System Stress Tester

This repository contains a simple MQTT client-server setup where the server sends commands to measure system performance, and the subscribers execute these commands and report the results.

## Prerequisites

- Python 3.x
- `paho-mqtt` library
- An MQTT broker (e.g., Mosquitto)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/SlaviXG/mqtt-system-stress-tester.git
   cd mqtt-system-stress-tester
   ```

2. **Install the Required Python Packages:**
   ```bash
   pip install paho-mqtt
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
1. **Set the Environment Variable:**

   On the broker machine, run:
   ```bash
   export MQTT_BROKER=localhost  # For Windows use `set MQTT_BROKER=localhost`
   ```
   
   On client machines, run:
   ```bash
   export MQTT_BROKER=<MQTT_BROKER_IP_ADDRESS>
   ```
   
2. **Run the System Under Test (SUT):**
   ```bash
   python sut.py
   ```

3. **Run the System Operator:**
   ```bash
   python operator.py
   ```