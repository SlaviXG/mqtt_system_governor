import json
import configparser


def parse_feedback(file_path: str):
    feedback_entries = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                feedback_entry = json.loads(line)
                feedback_entries.append(feedback_entry)
            except json.JSONDecodeError as e:
                print(f"Failed to parse line as JSON: {line}\nError: {e}")
    return feedback_entries


def display_feedback(feedback_entries):
    for entry in feedback_entries:
        print(f"Client ID: {entry['client_id']}")
        print(f"Command: {entry['command']}")
        print(f"Start Time: {entry['start_time']}")
        print(f"End Time: {entry['end_time']}")
        print(f"Output: {entry['output']}")
        print(f"Error: {entry['error']}")
        print("-" * 40)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    feedback_file_path = config['operator']['feedback_file']  # Load feedback_file_path from config.ini

    feedback_entries = parse_feedback(feedback_file_path)
    display_feedback(feedback_entries)

    # # Optionally, you can print the parsed feedback entries as a list of dictionaries
    # print("\nParsed feedback entries (as list of dictionaries):")
    # print(feedback_entries)
