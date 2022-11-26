# Playwight 案例：语雀访问登录

> 需求：访问目标页面时，有可能会需要登录，需要做判断。

### 依赖：
- Python 2.7 及以上版本
- playwright~=1.28.0
- PyYAML~=6.0

### 功能：
- 程序执行完成后，也不会关闭 Chrome
- 可以连接已经打开的 Chrome
- 支持登录后再跳转

### 文件说明：
- config.yaml：配置文件
- main.py：启动文件
- debugPort.txt：记录 debug 端口的文件。配置文件中可更改。
- chrome-win：chromium 程序的本体目录。配置文件中可指定。

### 使用：
- 安装依赖：`pip install -r requirements.txt`
- 下载 Chrome，并解压到目录：
  - https://playwright-akamai.azureedge.net/builds/chromium/1033/chromium-win64.zip
- 修改 config.yaml 中的 chromePath，指定 Chrome 的目录
  > 注意：如果你不准备下载上述的 Chromium，而是使用已有的 Chrome 应用，在使用此程序前，需要把后台的 Chrome 进程先关闭。
  > 
  > 否则 Chrome 将会启动不了 Debug 端口，从而导致此程序无法连接上 Chrome。
- 选择一篇你的语雀文章，需要登录的那种（公开的也不会影响使用），修改配置文件中的 targetUrl
- 启动应用：python main.py