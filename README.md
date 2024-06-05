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
   <br> For Ubuntu: 
   ```bash
   sudo apt-get update
   sudo apt-get install mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   ```
   
   <br> For Windows:
[Mosquitto download link.](https://mosquitto.org/download/)

## Running the example
1. **Set the Environment Variable:**
   ```bash
   export MQTT_BROKER=localhost  # For Windows use `set MQTT_BROKER=localhost`
   ```
   
2. **Run the Subscriber:**
   ```bash
   python subscriber.py
   ```

3. **Run the Publisher:**
   ```bash
   python publisher.py
   ```