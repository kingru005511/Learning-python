# 网站克隆工具 (Website Cloner)

## 描述

这是一个使用 Python 编写的网站克隆工具，旨在尽可能完整地下载目标网站的资源（HTML、CSS、JavaScript、图片、字体等），并在本地保留原始网站的目录结构。该工具利用 Selenium 模拟浏览器行为以处理动态加载的内容，并包含多种反爬虫检测规避策略。

## 主要功能

*   **网站克隆**: 下载指定 URL 开始的网站内容。
*   **动态内容处理**: 使用 Selenium 和 ChromeDriver 模拟浏览器环境，执行 JavaScript 并获取动态生成的内容。
*   **反爬虫规避**: 
    *   随机 User-Agent 轮换。
    *   禁用 WebDriver 特征标识。
    *   随机请求延迟和模拟滚动。
    *   设置 Referer 请求头。
*   **资源提取与下载**: 
    *   自动提取 HTML 中的 `<link>`, `<script>`, `<img>`, `<a>`, `<source>`, `<video poster>`, `<audio>`, `<iframe>`, `<embed>`, `<object>` 等标签引用的资源。
    *   解析 CSS 文件 (`.css`) 和内联样式 (`style="..."`) 中的 `url()` 引用，下载相关资源（如背景图片、字体文件）。
    *   支持 `@import` 和 `@font-face` 规则。
*   **文件结构保留**: 在本地 `Mirror` 目录（或指定的输出目录）下，按照原始网站的域名和路径结构保存文件。
*   **链接重写**: 自动修改 HTML 和 CSS 文件中的链接，使其指向本地下载的对应文件，确保克隆后的网站在本地可以正确浏览。
*   **并行下载**: 使用线程池并行下载非 HTML 资源，提高克隆效率。
*   **错误处理与重试**: 对网络请求错误（如超时）进行有限次数的重试，并记录 404 等错误。
*   **健壮的文件名处理**: 清理 URL 中的无效字符，处理过长的文件名（使用哈希值），并能处理 URL 查询参数。
*   **可配置性**: 支持通过命令行参数指定起始 URL、爬取深度、输出目录、下载线程数和日志级别。
*   **大小限制**: 限制下载单个文件的最大体积（默认为 50MB），避免下载过大的视频等文件。

## 环境要求

*   **Python 3**: 建议使用 Python 3.8 或更高版本。
*   **pip**: Python 包管理器。
*   **Google Chrome**: 需要安装 Chrome 浏览器。
*   **ChromeDriver**: 需要下载与已安装 Chrome 版本匹配的 ChromeDriver，并确保其路径在系统的 `PATH` 环境变量中，或者可以直接在脚本中指定路径。

## 安装

1.  **获取代码**: 将 `cloner.py` 文件复制到您的项目目录中。
2.  **安装依赖**: 打开终端或命令行，导航到 `cloner.py` 所在的目录，然后运行以下命令安装所需的 Python 库：
    ```bash
    pip install requests beautifulsoup4 selenium cssutils more-itertools
    ```
3.  **安装 Chrome 和 ChromeDriver**: 
    *   确保您的系统已安装 Google Chrome 浏览器。
    *   访问 ChromeDriver 官方下载页面 ([https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads) 或 [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)) 下载与您的 Chrome 版本匹配的 ChromeDriver。
    *   将下载的 `chromedriver` 可执行文件解压，并将其所在的目录添加到系统的 `PATH` 环境变量中，或者将其放在 `cloner.py` 相同的目录下。

## 使用方法

在终端或命令行中运行脚本，并提供必要的参数。

```bash
python cloner.py <url> [options]
```

**必需参数:**

*   `<url>`: 要克隆的网站的起始 URL (例如 `https://example.com`)。

**可选参数:**

*   `--depth <整数>`: HTML 页面的最大爬取深度。从起始 URL 开始为深度 0。默认值为 `2`。
*   `--output <目录路径>`: 保存克隆网站文件的本地目录。默认为脚本所在目录下的 `Mirror` 文件夹。
*   `--workers <整数>`: 用于并行下载资源的工作线程数。默认值为 `5`。
*   `--log-level <级别>`: 设置日志记录级别。可选值: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`。默认值为 `INFO`。

## 示例

1.  **克隆网站，默认深度 (2)，保存到默认 `Mirror` 目录:**
    ```bash
    python cloner.py https://example.com
    ```

2.  **克隆网站，设置最大深度为 1，保存到指定目录 `/path/to/cloned_site`:**
    ```bash
    python cloner.py https://blog.example.com --depth 1 --output /path/to/cloned_site
    ```

3.  **克隆网站，使用 10 个线程进行下载，并显示 DEBUG 级别的日志:**
    ```bash
    python cloner.py https://another-example.org --workers 10 --log-level DEBUG
    ```

## 注意事项与限制

*   **动态内容复杂性**: 对于高度依赖复杂 JavaScript 交互（例如需要登录、用户操作触发加载）才能完全渲染的网站，克隆效果可能不完美。脚本中的 Selenium 交互（如滚动）是通用的，可能无法触发所有特定网站的动态加载逻辑。
*   **反爬虫策略**: 尽管工具包含一些反爬措施，但强大的反爬虫系统（如 Cloudflare Bot Management, Akamai 等）仍可能检测并阻止爬虫。频繁或大规模地克隆网站可能会导致 IP 被封禁。
*   **资源限制**: 默认设置了 50MB 的文件大小限制，以避免下载大型视频或文件。对于需要下载更大文件的场景，请自行修改代码中的 `MAX_FILE_SIZE` 常量。
*   **CSS 解析**: CSS 解析和 URL 提取依赖 `cssutils` 库和正则表达式，可能无法覆盖所有边缘情况或复杂的 CSS 技巧。
*   **本地浏览**: 克隆完成后，可以通过打开 `Mirror/<域名>/index.html` 文件在本地浏览器中查看克隆的站点。由于浏览器安全策略（CORS 等），某些本地资源（如字体、部分脚本）可能无法正常加载，或者需要通过本地 Web 服务器（如 `python -m http.server`）来访问。
*   **法律与道德**: 请仅在获得网站所有者明确许可的情况下使用此工具。未经授权克隆受版权保护的网站内容可能涉及法律风险。请遵守相关法律法规和网站的 `robots.txt` 规则。

## 未来可能的改进

*   更智能的等待机制（等待特定元素加载完成）。
*   支持 `robots.txt`。
*   集成代理 IP 池。
*   更精细的资源类型过滤选项。
*   增量克隆功能。

