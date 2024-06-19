# MQTT System Governor

This repository contains a simple MQTT client-server setup where the server sends commands that get executed 
on each of the connected clients (subscribers), primarily used for measuring system performance and testing.
The special feature if this application is the opportunity to build and run pipelines (sequences of terminal
commands that get executed on client systems).

## Prerequisites

## Prerequisites

- **Operating System**: Linux (Debian-based distributions recommended for compatibility with `cpufreq-set` and `stress-ng` 
   commands (as in example), but generally make sure that all the commands are compatible with executing system.)
- **Python 3.x**
- **Python Libraries**: 
  - `paho-mqtt` library
  - `colorama` library
- **MQTT Broker**: Ensure you have an MQTT broker running, such as Mosquitto.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/SlaviXG/mqtt_system_governor.git
   cd mqtt_system_governor
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
- **command_loader_topic**: The MQTT topic for loading commands to be sent to clients. Default is system_performance/command_loader.

### [operator] Section

- **registration_timeout**: The time (in seconds) to wait for clients to register. Default is `5`.
- **enable_pipeline_mode**: Boolean option to enable or disable pipeline mode. If `True`, the defined pipelines will be executed in order. Default is `True`.
- **enable_realtime_mode**: Boolean option to enable or disable real-time mode. If `True`, commands can be sent to clients in real-time via the terminal. Default is `True`.
- **jsonify**: Boolean option to enable or disable JSON formatting of messages. If `True`, messages will be formatted as JSON. Default is `True`.
- **colorlog**: Boolean option to enable or disable color logging in the terminal. If `True`, logs will be colored for better readability. Default is `True`.
- **save_feedback**: Boolean option to enable or disable saving feedback to a file. If `True`, feedback from clients will be saved to the specified feedback file. Default is `True`.
- **feedback_file**: The name of the file where feedback will be saved. Default is `feedback.txt`.

### [commander] Section
**jsonify**: Boolean option to enable or disable JSON formatting of messages. If True, messages will be formatted as JSON. Default is True.

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
command_loader_topic = system_performance/command_loader

[operator]
registration_timeout = 5
enable_pipeline_mode = True
enable_realtime_mode = True
jsonify = True
colorlog = True
save_feedback = True
feedback_file = feedback.txt
receive_commands = True
pipeline1 = sudo cpufreq-set -r -f 600000; stress-ng --cpu 0 --timeout 60s --metrics-brief
pipeline2 = sudo cpufreq-set -r -f 1200000; stress-ng --cpu 0 --timeout 60s --metrics-brief
pipeline3 = sudo cpufreq-set -r -f 1800000; stress-ng --cpu 0 --timeout 60s --metrics-brief

[commander]
jsonify = True
```

## Commander Introduction

The Commander is a customizable MQTT client designed to send commands to specific clients (Systems Under Test, or SUTs) 
via the MQTT broker and receive feedback on command execution. The Commander can be configured to format messages 
in JSON or plain text, and it can be extended or implemented in other custom programs to suit specific needs.

![image](https://github.com/SlaviXG/mqtt_system_governor/assets/78792148/770e92cf-c445-4d67-ae7a-88a452224d1e)


### Key Features

- **Send Commands**: Send commands to clients using the MQTT command_loader_topic.
- **Receive Feedback**: Receive and process feedback from clients using the MQTT response_topic.
- **Configurable Format**: Configure whether messages are formatted as JSON or plain text.
- **Customizable**: Extend the base Commander class to implement custom behavior or integrate with other systems.

### How to Use

1. **Set Up Configuration**: Ensure the config.ini file is properly configured with the MQTT broker details and the 
desired settings for JSON formatting.
2. **Run the Commander**: Execute the commander.py script to start the Commander.
3. **Send Commands**: Enter the client ID (or 'all' to send to all clients) and the command to send when prompted. The Commander will publish the command to the command_loader_topic.
4. **Receive Feedback**: The Commander will automatically subscribe to the response_topic and print received feedback to the console.

### Example Usage

```shell
python commander.py
```

### Customizing the Commander

The BaseCommander class is designed as a customizable base. You can extend this class to implement custom behavior 
or integrate with other systems. For example, you could override the on_message method to process feedback differently 
or add new methods to handle specific types of commands.

### Example of Extending the BaseCommander

Here is an example of how you can extend the BaseCommander to create a custom commander:
```python
from commander import BaseCommander

class CustomCommander(BaseCommander):
    def on_message(self, client, userdata, msg):
        feedback = msg.payload.decode()
        if self._jsonify:
            try:
                feedback = json.loads(feedback)
                # Custom processing of feedback
                print(f"Custom received feedback:\n{json.dumps(feedback, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON feedback: {e}\nRaw feedback: {feedback}")
        else:
            print(f"Custom received feedback:\n{feedback}")

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    broker = os.getenv('MQTT_BROKER') or config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    command_loader_topic = config['mqtt']['command_loader_topic']
    response_topic = config['mqtt']['response_topic']
    jsonify = config.getboolean('commander', 'jsonify')

    custom_commander = CustomCommander(broker, port, command_loader_topic, response_topic, jsonify)
    custom_commander.connect()

    try:
        while True:
            client_id = input("Enter the client ID: ")
            command = input("Enter the command to send: ")
            custom_commander.send_command(client_id, command)
            time.sleep(1)  # Add a small delay to ensure commands are processed
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        custom_commander.disconnect()
```

The BaseCommander provides a flexible and extensible way to manage command execution and feedback in a distributed system, 
making it a valuable tool for system operators and developers.
