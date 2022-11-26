import gc
import pathlib
import socket
import subprocess

import yaml


class Config:
    chromePath: str = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    debugPort: int = 0
    windowSize: str = 'max'
    startupUrl: str = 'about:blank'
    debugPortFile: str = 'debugPort.txt'
    targetUrl: str = 'about:blank'
    newPage: bool = False

    def __init__(self, **entries):
        self.__dict__.update(entries)


def load_conf(file='config.yaml') -> Config:
    yaml_dict = yaml.safe_load(pathlib.Path(file).read_text(encoding='utf-8'))
    return Config(**yaml_dict)


def get_free_port(port=0) -> int:
    sock = socket.socket()
    sock.bind(('localhost', port))
    port = sock.getsockname()[1]
    sock.close()
    del sock
    gc.collect()
    return port


def start_chrome(config: Config) -> int:
    debug_port = get_free_port(config.debugPort)
    start_cmd = [
        config.chromePath,
        config.startupUrl,
        '--test-type',
        '--remote-debugging-port=%d' % debug_port,
    ]
    if config.windowSize == 'max':
        start_cmd.append('--start-maximized')
    else:
        start_cmd.append('--window-size=%s' % config.windowSize)

    subprocess.Popen(start_cmd)
    return debug_port
