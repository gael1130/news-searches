import json

def load_credentials(credentials_path):
    """Load credentials from a JSON file and return as a dictionary."""
    try:
        with open(credentials_path, 'r') as file:
            credentials = json.load(file)
            return credentials
    except FileNotFoundError:
        print(f"Error: The file {credentials_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {credentials_path} is not a valid JSON.")
    return None
