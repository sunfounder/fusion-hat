import json
import os
from typing import Optional, Iterator


class Config():
    def __init__(self, config_file: str) -> None:
        """
        Initialize the config class

        :param config_file: config file path
        :type config_file: str
        """
        self.config_file = config_file
        
        if not os.path.exists(config_file):
            os.system(f'touch {config_file}')
            os.system(f'chown 1000:1000 {config_file}')
        with open(config_file, 'r') as f:
            content = f.read()
            if content == '':
                content = '{}'
            self._config = json.loads(content)

    def get(self, key: str, default_value: Optional[any] = None) -> any:
        """
        Get the value of the key

        :param key: key name
        :type key: str

        :param default_value: default value if the key is not found
        :type default_value: Optional[any]

        :return: value of the key
        :rtype: any
        """
        return self._config.get(key, default_value)

    def set(self, key: str, value: any) -> None:
        """
        Set the value of the key

        :param key: key name
        :type key: str

        :param value: value of the key
        :type value: any
        """
        self._config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=4)

    def delete(self, key: str) -> None:
        """
        Delete the key

        :param key: key name
        :type key: str
        """
        if key in self._config:
            del self._config[key]
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def __getitem__(self, key: str) -> any:
        """
        Get the value of the key

        :param key: key name
        :type key: str

        :return: value of the key
        :rtype: any
        """
        return self.get(key)

    def __setitem__(self, key: str, value: any) -> None:
        """
        Set the value of the key

        :param key: key name
        :type key: str

        :param value: value of the key
        :type value: any
        """
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """
        Delete the key

        :param key: key name
        :type key: str
        """
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        """
        Check if the key exists

        :param key: key name
        :type key: str

        :return: True if the key exists, False otherwise
        :rtype: bool
        """
        return key in self._config

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over the keys

        :return: iterator over the keys
        :rtype: Iterator[str]
        """
        return iter(self._config)

    def __len__(self) -> int:
        """
        Get the number of keys

        :return: number of keys
        :rtype: int
        """
        return len(self._config)

    def __str__(self) -> str:
        """
        Get the string representation of the config

        :return: string representation of the config
        :rtype: str
        """
        return json.dumps(self._config, indent=4)

    def __repr__(self) -> str:
        """
        Get the string representation of the config

        :return: string representation of the config
        :rtype: str
        """
        return f'Config({self.config_file})'
