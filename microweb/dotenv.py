try:
    import re
except ImportError:
    import ure as re

# Custom dotenv functionality for MicroPython
def load_dotenv():
    try:
        env_vars = {}
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines or comments
                if not line or line.startswith('#'):
                    continue
                # Split the line into key and value
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    env_vars[key.strip()] = value.strip()
                else:
                    print(f"Skipping malformed .env line: {line}")
        return env_vars
    except Exception as e:
        print(f"Failed to load .env file: {str(e)}")
        return {}

def get_env(key, default=None, env_vars=None):
    return env_vars.get(key, default) if env_vars else default


    