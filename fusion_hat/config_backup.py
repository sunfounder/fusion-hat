import json
import os
from re import S
from time import sleep
from fusion_hat.utils import debug

class Config():
    def __init__(self, db:str, mode:str=None, owner:str=None):
        """初始化Config类，兼容fileDB的API接口
        
        :param db: 保存数据的文件路径
        :type db: str
        :param mode: 文件模式
        :type mode: str
        :param owner: 文件所有者
        :type owner: str
        """
        self.config_file = db
        
        if self.config_file != None:
            self.file_check_create(db, mode, owner)
        else:
            raise ValueError('db: Missing file path parameter.')
            
        with open(self.config_file, 'r') as f:
            content = f.read()
            if content == '':
                content = '{}'
            try:
                self._config = json.loads(content)
            except json.JSONDecodeError:
                # 如果文件不是有效的JSON格式，尝试解析为key=value格式并转换为JSON
                self._config = {}
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and not line.strip().startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self._config[key.strip()] = value.strip()
                # 将转换后的数据保存为JSON格式
                with open(self.config_file, 'w') as fw:
                    json.dump(self._config, fw, indent=4)

    def file_check_create(self, file_path:str, mode:str=None, owner:str=None):
        dir = file_path.rsplit('/',1)[0]
        try:
            if os.path.exists(file_path):
                if not os.path.isfile(file_path):
                    print('Could not create file, there is a folder with the same name')
                    return
            else:
                if os.path.exists(dir):
                    if not os.path.isdir(dir):
                        print('Could not create directory, there is a file with the same name')
                        return
                else:
                    os.makedirs(dir, mode=0o754)
                    sleep(0.001)
                with open(file_path, 'w') as f:
                    f.write("# robot-hat config and calibration value of robots\n\n")
            if mode != None:
                # neo传参是十进制，强制性转换成八进制
                octal_mode = oct(mode)[2:] if isinstance(mode, int) else str(mode)
                os.popen(f'sudo chmod {octal_mode} {file_path}')
                # 增加文件检查
                cmd = f'sudo chmod {octal_mode} "{file_path}"'
                result = os.system(cmd)
                if result != 0:
                    debug(f"Warning: Failed to set permissions with command: {cmd}")
            if owner != None:
                os.popen(f'sudo chown -R {owner}:{owner} {dir}')
                cmd = f'sudo chown -R {owner}:{owner} "{dir}"'
                result = os.system(cmd)
                if result != 0:
                    debug(f"Warning: Failed to set owner with command: {cmd}")
        except Exception as e:
            raise(e) 


    def get(self, key, default_value=None):
        """Get the value for the specified key
        
        :param key: The key to get
        :type key: str
        :param default_value: The default value to return if the key is not found
        :type default_value: Any
        :return: The value for the specified key or the default value if the key is not found
        :rtype: Any
        """
        return self._config.get(key, default_value)

    def set(self, key, value):
        """Set the value for the specified key
        
        :param key: The key to set
        :type key: str
        :param value: The value to set
        :type value: Any
        """
        self._config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=4)
    
    
    def write(self):
        """Write the current configuration to a file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=4)

    def delete(self, key):
        """Delete the specified key from the configuration  
        :param key: The key to delete
        :type key: str
        """
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