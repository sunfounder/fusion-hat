import json
import os

class Config():
    def __init__(self, config_file):
        self.config_file = config_file
        
        if not os.path.exists(config_file):
            os.system(f'touch {config_file}')
            os.system(f'chown 1000:1000 {config_file}')
        with open(config_file, 'r') as f:
            content = f.read()
            if content == '':
                content = '{}'
            self._config = json.loads(content)

    def get(self, key, default_value=None):
        return self._config.get(key, default_value)

    def set(self, key, value):
        self._config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=4)

    def delete(self, key):
        if key in self._config:
            del self._config[key]
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __contains__(self, key):
        return key in self._config

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

    def __str__(self):
        return json.dumps(self._config, indent=4)

    def __repr__(self):
        return f'Config({self.config_file})'
