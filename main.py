import sys

from playwright.sync_api import Playwright, sync_playwright

import utils


def run(p: Playwright) -> None:
    config = utils.load_conf()
    browser, is_new = utils.create_or_conn(p, config)
    page = utils.new_page(config, browser, is_new)

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
