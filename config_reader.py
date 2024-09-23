class config:
    def __init__(self, file):
        self.values = {}
        self._load_config(file)

    def _load_config(self, file):
        try:
            with open(file, "r") as f:
                for line in f:
                    line = line.strip()
                    # Ignore comments and blank lines
                    if line.startswith("#") or not line:
                        continue
                    try:
                        key, value = line.split("=", 1)
                        self.values[key.strip()] = value.strip()
                    except ValueError:
                        print(f"Warning: Malformed line in config: '{line}'")
        except FileNotFoundError:
            print(f"Error: Config file '{file}' not found.")
        except Exception as e:
            print(f"Error: {e}")

    def get(self, key, default=None):
        """ Returns the value of the given key, or default if key doesn't exist. """
        return self.values.get(key, default)

    def get_discord_token(self):
        """ Returns the Discord token. """
        return self.get('discord_token')
    
    def get_obs_ip(self):
        """ Returns the OBS socket IP """
        return self.get("obs_ip")
    
    def get_obs_port(self):
        """ Returns the OBS socket port number"""
        return self.get("obs_port")
    
    def get_obs_password(self):
        """ Returns the OBS socket password """
        return self.get("obs_password")
