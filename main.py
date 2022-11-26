import os.path
import sys
import time

from playwright.sync_api import Browser
from playwright.sync_api import Page
from playwright.sync_api import Playwright, sync_playwright

import utils


def create_or_conn(config: utils.Config) -> (Browser, bool):
    """ 创建或连接已有的浏览器。返回：浏览器示例，是否为创建的 """
    if os.path.exists(config.debugPortFile):
        # 文件存在，则读取，并尝试连接
        with open(config.debugPortFile, mode='r') as _f:
            debug_port = _f.readline()
        if debug_port:
            try:
                return playwright.chromium.connect_over_cdp('http://localhost:' + debug_port), False
            except Exception:
                pass
    # 如果不存在、或者连接失败，则创建浏览器，再连接
    debug_port = utils.start_chrome(config)
    # 等待浏览器启动
    time.sleep(1)
    # 连接
    browser = playwright.chromium.connect_over_cdp('http://localhost:%d' % debug_port)
    # 记录端口
    with open(config.debugPortFile, mode='w+') as _f:
        _f.write(str(debug_port))
    return browser, True


def new_page(config: utils.Config, browser: Browser, is_new: bool) -> Page:
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


def run(playwright: Playwright) -> None:
    config = utils.load_conf()
    browser, is_new = create_or_conn(config)
    page = new_page(config, browser, is_new)

    target_url = config.targetUrl

    # 访问页面，如果返回 404，则执行登录逻辑。然后再请求到目标页面
    # 如果返回 200，则继续
    with page.expect_response(
            lambda response: response.url == target_url,
            timeout=0) as resp:
        page.goto(target_url)
    # 等待响应
    resp = resp.value
    if resp.status == 404:
        # 点击登录后，等待 url 变化
        with page.expect_navigation(url='https://www.yuque.com/login'):
            page.get_by_role("link", name="登录 / 注册").click()
        # 点击微信登录图标，从 0 开始，第三个所以是 nth(2)
        page.get_by_test_id("third-login-link").locator("a").nth(2).click()
        # 点击同意后，等待页面跳转到扫码界面
        with page.expect_navigation(url='https://www.yuque.com/login?platform=wechat&loginType=sms'):
            page.get_by_role("button", name="同 意").click()

        # 等待登录后，自动重定向回 target_url
        # 某些网站只会重定向回主页，则需要进行判断后，程序进行跳转
        with page.expect_response(
                lambda response: response.url == target_url and response.status == 200,
                timeout=0):
            print('Wait for login')
        print('Login success')
    elif resp.status != 200:
        print('Unknown status: %d' % resp.status)
        sys.exit(1)

    # 点击右上角的菜单
    page.get_by_test_id("doc-reader-more-actions").locator("svg").click()
    print('done')
    # page.pause()
    # page.close()
    #
    # # ---------------------
    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
