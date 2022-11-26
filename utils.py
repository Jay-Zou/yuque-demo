import gc
import os
import pathlib
import socket
import subprocess
import sys
import time

import yaml
from playwright.sync_api import Browser, Page
from playwright.sync_api import Playwright


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


def create_or_conn(p: Playwright, config: Config) -> (Browser, bool):
    """ 创建或连接已有的浏览器。返回：浏览器示例，是否为创建的 """
    if os.path.exists(config.debugPortFile):
        # 文件存在，则读取，并尝试连接
        with open(config.debugPortFile, mode='r') as _f:
            debug_port = _f.readline()
        if debug_port:
            try:
                return p.chromium.connect_over_cdp('http://localhost:' + debug_port), False
            except Exception:
                pass
    # 如果不存在、或者连接失败，则创建浏览器，再连接
    debug_port = start_chrome(config)
    # 等待浏览器启动
    time.sleep(1)
    # 连接
    browser = p.chromium.connect_over_cdp('http://localhost:%d' % debug_port)
    # 记录端口
    with open(config.debugPortFile, mode='w+') as _f:
        _f.write(str(debug_port))
    return browser, True


def new_page(config: Config, browser: Browser, is_new: bool) -> Page:
    # 获取原始窗口的第一个
    if len(browser.contexts) == 0:
        print('Cannot found an exist browser\'s context')
        sys.exit(1)
    context = browser.contexts[0]
    # 如果 context 已经关闭
    if len(context.pages) == 0:
        print('Context has been close')
        sys.exit(1)
    # 如果指定新页面，并且非此次创建的新的浏览器对象
    if config.newPage and not is_new:
        return context.new_page()
    # 否则使用第一个页面。同时激活页面
    page = context.pages[0]
    page.bring_to_front()
    return page
