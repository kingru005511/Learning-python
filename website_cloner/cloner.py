import os
import time
import requests
import random
import re
import logging
import argparse
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import cssutils
import concurrent.futures

# 设置cssutils日志级别，避免过多警告
cssutils.log.setLevel(logging.CRITICAL)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('website_cloner')

# 常量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIRROR_DIR = os.path.join(BASE_DIR, 'Mirror')
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.114 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0'
]

# 文件大小限制 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

def get_random_user_agent():
    """返回随机用户代理"""
    return random.choice(USER_AGENTS)

def setup_driver():
    """设置Selenium WebDriver"""
    logger.info("设置Selenium WebDriver...")
    chrome_options = Options()
    chrome_options.accept_insecure_certs = True
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logger.info("WebDriver设置完成")
        return driver
    except Exception as e:
        logger.error(f"设置WebDriver时出错: {e}")
        raise

def fetch_page_with_selenium(url, driver, wait_for_selector=None):
    """使用Selenium获取页面内容"""
    logger.info(f"使用Selenium获取URL: {url}")
    try:
        driver.get(url)
        
        # 如果提供了选择器，等待该元素出现
        if wait_for_selector:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
            except Exception as e:
                logger.warning(f"等待选择器 '{wait_for_selector}' 超时: {e}")
        
        # 使用随机延迟
        time.sleep(random.uniform(3, 5))
        
        # 模拟滚动以加载更多内容
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # 滚动几次
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return driver.page_source
    except Exception as e:
        logger.error(f"使用Selenium获取 {url} 时出错: {e}")
        return None

def sanitize_filename(filename):
    """移除或替换文件名中的无效字符"""
    # 移除查询字符串和片段标识符
    filename = filename.split('?')[0].split('#')[0]
    # 替换可能有问题的字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 将多个下划线替换为一个
    filename = re.sub(r'_+', '_', filename)
    # 移除开头/结尾的下划线/空格/句点
    filename = filename.strip('_. ')
    # 处理文件名为空的情况
    if not filename:
        return 'index'
    # 限制长度（操作系统限制各不相同，例如ext4上为255字节）
    # 考虑到路径长度限制，保守一些
    max_len = 150
    if len(filename.encode('utf-8')) > max_len:
        name, ext = os.path.splitext(filename)
        # 截断名称部分，保留扩展名
        while len((name + ext).encode('utf-8')) > max_len and len(name) > 0:
            name = name[:-1]
        filename = name + ext
        # 如果仍然太长（例如，非常长的扩展名），截断整个文件名
        if len(filename.encode('utf-8')) > max_len:
            encoded_filename = filename.encode('utf-8')
            filename = encoded_filename[:max_len].decode('utf-8', errors='ignore')

    return filename

def get_local_path(base_netloc, resource_url, current_page_local_path=None):
    """确定资源的本地文件路径，保留目录结构。
       返回绝对路径和相对于镜像根目录的路径。
    """
    parsed_resource = urlparse(resource_url)
    if not parsed_resource.netloc or parsed_resource.netloc != base_netloc:
        return None, None  # 外部或无效URL

    domain_dir = os.path.join(MIRROR_DIR, base_netloc)

    # 解码并分割路径
    path = unquote(parsed_resource.path).strip('/')
    path_parts = [sanitize_filename(part) for part in path.split('/') if part]

    # 确定文件名和目录路径
    if path.endswith('/') or not path_parts or ('.' not in path_parts[-1] and not parsed_resource.query):
        # URL指向目录或没有文件名部分，假设为index.html
        dir_parts = path_parts
        filename = 'index.html'
    else:
        # URL有文件名
        dir_parts = path_parts[:-1]
        filename = sanitize_filename(path_parts[-1])

    # 如果存在查询字符串，将其添加到文件名中
    if parsed_resource.query:
        query_part = sanitize_filename(parsed_resource.query)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{query_part}{ext}"
        # 添加查询后重新清理并截断
        filename = sanitize_filename(filename)

    # 构建绝对路径
    local_dir_abs = os.path.join(domain_dir, *dir_parts)
    local_path_abs = os.path.join(local_dir_abs, filename)

    # 构建相对于镜像根目录的路径（用于重写链接）
    local_path_rel = os.path.relpath(local_path_abs, MIRROR_DIR)

    return local_path_abs, local_path_rel

def save_resource(url, content, path):
    """将内容保存到文件，必要时创建目录"""
    try:
        safe_path = os.path.abspath(path)
        if not safe_path.startswith(os.path.abspath(MIRROR_DIR)):
            logger.error(f"尝试保存到MIRROR_DIR之外: {path}")
            return False

        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, 'wb') as f:
            f.write(content)
        logger.info(f"已保存资源: {url} -> {safe_path}")
        return True
    except OSError as e:
        logger.error(f"保存资源 {url} 到 {path} 时出现OS错误: {e}")
        try:
            # 尝试使用更简单的文件名
            dirname = os.path.dirname(safe_path)
            filename = os.path.basename(safe_path)
            name, ext = os.path.splitext(filename)
            # 使用哈希值作为文件名
            import hashlib
            hashed_name = hashlib.md5(name.encode()).hexdigest()[:20]
            new_filename = f"{hashed_name}{ext}"
            new_safe_path = os.path.join(dirname, new_filename)
            
            os.makedirs(os.path.dirname(new_safe_path), exist_ok=True)
            with open(new_safe_path, 'wb') as f:
                f.write(content)
            logger.warning(f"使用哈希文件名保存: {url} -> {new_safe_path}")
            return True
        except Exception as inner_e:
            logger.error(f"使用哈希文件名保存资源 {url} 时出错: {inner_e}")
            return False
    except Exception as e:
        logger.error(f"保存资源 {url} 到 {path} 时出现通用错误: {e}")
        return False

def download_resource(url, session, referer, max_retries=3):
    """下载资源"""
    logger.info(f"下载资源: {url}")
    retries = 0
    while retries < max_retries:
        try:
            headers = {
                'User-Agent': get_random_user_agent(),
                'Referer': referer,  # 使用引用页面URL
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            response = session.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # 检查内容类型和大小，避免过大的文件
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                logger.warning(f"跳过大文件 (>{MAX_FILE_SIZE/1024/1024:.1f}MB): {url}")
                return None

            # 分块读取内容，避免内存问题
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > MAX_FILE_SIZE:
                    logger.warning(f"下载过程中跳过大文件 (>{MAX_FILE_SIZE/1024/1024:.1f}MB): {url}")
                    return None
            return content

        except requests.exceptions.Timeout:
            retries += 1
            logger.warning(f"下载资源 {url} 超时 (尝试 {retries}/{max_retries})")
            if retries >= max_retries:
                logger.error(f"下载资源 {url} 超时，已达到最大重试次数")
                return None
            time.sleep(random.uniform(1, 3))  # 重试前等待
            
        except requests.exceptions.RequestException as e:
            # 对于404等错误，不重试
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 404:
                    logger.warning(f"资源不存在 (404): {url}")
                    return None
                elif status_code >= 400 and status_code < 500:
                    logger.warning(f"客户端错误 ({status_code}): {url}")
                    return None
            
            retries += 1
            logger.warning(f"下载资源 {url} 时出错: {e} (尝试 {retries}/{max_retries})")
            if retries >= max_retries:
                logger.error(f"下载资源 {url} 失败，已达到最大重试次数")
                return None
            time.sleep(random.uniform(1, 3))  # 重试前等待
            
        except Exception as e:
            logger.error(f"下载资源 {url} 时出现意外错误: {e}")
            return None

def rewrite_url(tag, attr, original_url, base_netloc, current_page_local_path):
    """重写BeautifulSoup标签中的URL属性，指向本地路径"""
    abs_local_path, rel_local_path = get_local_path(base_netloc, original_url)
    if abs_local_path and rel_local_path:
        # 计算从当前HTML文件到资源的相对路径
        current_dir = os.path.dirname(current_page_local_path)
        try:
            relative_path_to_resource = os.path.relpath(abs_local_path, start=current_dir)
            tag[attr] = relative_path_to_resource
            logger.debug(f"重写了标签 {tag.name} 中的 {attr}: {original_url} -> {relative_path_to_resource}")
            return abs_local_path  # 返回绝对路径用于下载检查
        except ValueError as e:
            # 在Windows上，如果路径在不同驱动器上，可能会发生这种情况，这里应该不是问题
            logger.error(f"计算从 {current_dir} 到 {abs_local_path} 的相对路径时出错: {e}")
            # 回退到相对于镜像根目录的路径？或保留原始路径？
            # 使用rel_local_path（相对于Mirror根目录）作为回退
            tag[attr] = rel_local_path
            logger.warning(f"使用相对于Mirror根目录的路径重写 {attr}: {original_url} -> {rel_local_path}")
            return abs_local_path
    else:
        logger.debug(f"未重写标签 {tag.name} 中的 {attr}: {original_url}（外部或无效）")
        return None

def handle_inline_style_url(match, current_url, base_netloc, current_page_local_path, resource_queue, downloaded_resources, current_depth):
    """处理内联样式中找到的url()"""
    url_match = match.group(1).strip(' \'"')  # 从正则表达式匹配中获取URL
    absolute_resource_url = urljoin(current_url, url_match)
    parsed_resource = urlparse(absolute_resource_url)

    if parsed_resource.scheme not in ['http', 'https'] or parsed_resource.netloc != base_netloc:
        return match.group(0)  # 如果是外部或无效，返回原始内容

    abs_local_path, rel_local_path = get_local_path(base_netloc, absolute_resource_url)
    if abs_local_path and rel_local_path:
        current_dir = os.path.dirname(current_page_local_path)
        try:
            relative_path_to_resource = os.path.relpath(abs_local_path, start=current_dir)
            # 如果尚未处理，添加到下载队列
            if absolute_resource_url not in downloaded_resources:
                resource_queue.add((absolute_resource_url, current_depth + 1))
            return f"url('{relative_path_to_resource}')"
        except ValueError:
            # 回退到相对于镜像根目录的路径
            if absolute_resource_url not in downloaded_resources:
                resource_queue.add((absolute_resource_url, current_depth + 1))
            return f"url('{rel_local_path}')"
    return match.group(0)  # 如果路径计算失败，返回原始内容

def extract_css_urls(css_content, base_url, base_netloc, current_page_local_path, resource_queue, downloaded_resources, current_depth):
    """从CSS内容中提取URL并添加到下载队列"""
    try:
        sheet = cssutils.parseString(css_content)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for property in rule.style:
                    if property.name in ['background', 'background-image', 'src', 'content'] and 'url(' in property.value:
                        # 使用正则表达式提取url()中的内容
                        urls = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', property.value)
                        for url in urls:
                            absolute_url = urljoin(base_url, url)
                            parsed_url = urlparse(absolute_url)
                            
                            # 只处理同一域名的资源
                            if parsed_url.netloc == base_netloc and parsed_url.scheme in ['http', 'https']:
                                if absolute_url not in downloaded_resources:
                                    resource_queue.add((absolute_url, current_depth + 1))
                                    logger.debug(f"从CSS中提取URL: {absolute_url}")
            
            elif rule.type == rule.IMPORT_RULE:
                # 处理@import规则
                import_url = urljoin(base_url, rule.href)
                parsed_url = urlparse(import_url)
                if parsed_url.netloc == base_netloc and parsed_url.scheme in ['http', 'https']:
                    if import_url not in downloaded_resources:
                        resource_queue.add((import_url, current_depth + 1))
                        logger.debug(f"从CSS @import中提取URL: {import_url}")
            
            elif rule.type == rule.FONT_FACE_RULE:
                # 处理@font-face规则
                for property in rule.style:
                    if property.name == 'src' and 'url(' in property.value:
                        urls = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', property.value)
                        for url in urls:
                            absolute_url = urljoin(base_url, url)
                            parsed_url = urlparse(absolute_url)
                            if parsed_url.netloc == base_netloc and parsed_url.scheme in ['http', 'https']:
                                if absolute_url not in downloaded_resources:
                                    resource_queue.add((absolute_url, current_depth + 1))
                                    logger.debug(f"从CSS @font-face中提取URL: {absolute_url}")
    except Exception as e:
        logger.error(f"解析CSS内容时出错: {e}")

def clone_website(start_url, max_depth=3, max_workers=5):
    """克隆网站的主函数"""
    logger.info(f"开始克隆: {start_url} (最大深度: {max_depth})")
    parsed_start_url = urlparse(start_url)
    base_netloc = parsed_start_url.netloc
    if not base_netloc:
        logger.error("无效的起始URL: 缺少网络位置")
        return

    driver = None
    session = requests.Session()  # 使用会话进行下载

    # 队列存储元组: (url, depth)
    queue = {(start_url, 0)}
    visited_html = set()  # 跟踪已访问的HTML页面，避免重复处理
    downloaded_resources = set()  # 跟踪已下载的资源URL，避免重复下载

    try:
        driver = setup_driver()
        
        # 创建线程池用于并行下载资源
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {}  # 跟踪提交的任务
            
            while queue:
                if not queue:
                    break
                current_url, current_depth = queue.pop()

                # 标准化URL（移除片段，确保方案）
                parsed_temp = urlparse(current_url)
                current_url = urljoin(current_url, parsed_temp.path)  # 不带片段重建
                if not current_url.startswith(('http://', 'https://')):
                    logger.warning(f"跳过非HTTP(S) URL: {current_url}")
                    continue

                # 检查域名
                parsed_current = urlparse(current_url)
                if parsed_current.netloc != base_netloc:
                    logger.info(f"跳过外部URL: {current_url}")
                    continue

                # 确定当前URL的本地路径
                current_local_path_abs, _ = get_local_path(base_netloc, current_url)
                if not current_local_path_abs:
                    logger.warning(f"无法确定本地路径: {current_url}")
                    continue

                # --- 检查是否已处理/下载 --- 
                # 启发式：检查是否看起来像HTML页面
                is_html = (not os.path.splitext(parsed_current.path)[1] or 
                        any(parsed_current.path.lower().endswith(ext) for ext in ['.html', '.htm', '/[^.]*$']))  # 正则表达式匹配尾部斜杠或无扩展名
                is_html = is_html or (current_url == start_url)  # 将起始URL视为HTML

                if is_html:
                    if current_url in visited_html:
                        continue
                    visited_html.add(current_url)
                    logger.info(f"处理HTML (深度 {current_depth}): {current_url}")
                else:
                    if current_url in downloaded_resources:
                        continue
                    # 对于非HTML，我们直接下载，不使用Selenium
                    logger.info(f"处理资源: {current_url}")

                # --- 获取内容 --- 
                content = None
                modified_soup = None
                if is_html:
                    if current_depth > max_depth:
                        logger.info(f"由于深度限制跳过HTML页面: {current_url}")
                        continue

                    page_source = fetch_page_with_selenium(current_url, driver)
                    if page_source:
                        content = page_source.encode('utf-8')
                        soup = BeautifulSoup(page_source, 'html.parser')

                        # --- 资源/链接提取和重写 --- 
                        tags_to_process = {
                            'link': 'href', 
                            'script': 'src', 
                            'img': 'src', 
                            'a': 'href',
                            'source': 'src',  # 用于视频/音频
                            'video': 'poster',  # 视频海报图片
                            'audio': 'src',  # 音频源
                            'iframe': 'src',  # 内嵌框架
                            'embed': 'src',  # 嵌入内容
                            'object': 'data',  # 对象数据
                        }

                        for tag_name, attr_name in tags_to_process.items():
                            for tag in soup.find_all(tag_name, **{attr_name: True}):  # 查找具有指定属性的标签
                                original_resource_url = tag[attr_name]
                                # 解析相对URL
                                absolute_resource_url = urljoin(current_url, original_resource_url)
                                parsed_resource = urlparse(absolute_resource_url)

                                # 跳过数据URI、javascript:链接等
                                if parsed_resource.scheme not in ['http', 'https']:
                                    continue

                                # 重写标签中的URL并获取本地路径
                                resource_local_path = rewrite_url(tag, attr_name, absolute_resource_url, base_netloc, current_local_path_abs)

                                # 如果是内部资源且需要下载
                                if resource_local_path and parsed_resource.netloc == base_netloc:
                                    # 添加资源到下载队列
                                    if absolute_resource_url not in downloaded_resources and absolute_resource_url not in visited_html:
                                        # 添加到主队列进行处理（如果不是HTML则下载）
                                        queue.add((absolute_resource_url, current_depth + 1))  # 资源继承深度

                                    # 如果是链接（<a>标签）且在深度限制内，添加到访问队列
                                    if tag_name == 'a' and current_depth + 1 <= max_depth:
                                        if absolute_resource_url not in visited_html:
                                            queue.add((absolute_resource_url, current_depth + 1))

                        # 处理内联样式中的url()
                        for tag in soup.find_all(style=True):
                            style_content = tag['style']
                            # 用于url()的基本正则表达式 - 可能需要改进
                            updated_style = re.sub(r'url\(([^)]+)\)', 
                                                lambda m: handle_inline_style_url(m, current_url, base_netloc, current_local_path_abs, queue, downloaded_resources, current_depth), 
                                                style_content)
                            if updated_style != style_content:
                                tag['style'] = updated_style
                                logger.debug(f"重写了标签 {tag.name} 中的内联样式")

                        # 特殊处理CSS文件
                        for link in soup.find_all('link', rel='stylesheet', href=True):
                            css_url = urljoin(current_url, link['href'])
                            parsed_css = urlparse(css_url)
                            
                            # 只处理同一域名的CSS
                            if parsed_css.netloc == base_netloc and css_url not in downloaded_resources:
                                # 将CSS添加到下载队列
                                queue.add((css_url, current_depth + 1))

                        modified_soup = soup

                else:  # 处理非HTML资源（CSS、JS、图片等）
                    # 提交下载任务到线程池
                    if current_url not in future_to_url:
                        future = executor.submit(download_resource, current_url, session, current_url)
                        future_to_url[future] = current_url
                        downloaded_resources.add(current_url)
                        
                        # 如果是CSS文件，稍后会解析并查找更多资源
                        continue  # 继续处理队列中的其他项目，等待下载完成

                # --- 保存获取/修改的内容 --- 
                if content:
                    if modified_soup:
                        # 保存修改后的HTML
                        save_resource(current_url, modified_soup.prettify('utf-8'), current_local_path_abs)
                    else:
                        # 保存原始资源（CSS、JS、图片或未修改的HTML）
                        save_resource(current_url, content, current_local_path_abs)
                        # 即使保存失败也添加到已下载集合，避免重试
                        downloaded_resources.add(current_url)
                else:
                    # 即使下载失败也添加到已下载集合，避免重试
                    if not is_html:
                        downloaded_resources.add(current_url)

                # 添加随机延迟
                time.sleep(random.uniform(0.5, 1.5))
                
                # 检查完成的下载任务
                done_futures = [f for f in future_to_url.keys() if f.done()]
                for future in done_futures:
                    url = future_to_url[future]
                    try:
                        content = future.result()
                        if content:
                            # 获取本地路径
                            local_path_abs, _ = get_local_path(base_netloc, url)
                            if local_path_abs:
                                # 保存资源
                                save_resource(url, content, local_path_abs)
                                
                                # 如果是CSS文件，解析并提取其中的URL
                                if url.lower().endswith('.css'):
                                    css_text = content.decode('utf-8', errors='ignore')
                                    extract_css_urls(css_text, url, base_netloc, local_path_abs, queue, downloaded_resources, current_depth)
                    except Exception as e:
                        logger.error(f"处理下载结果时出错 {url}: {e}")
                    
                    # 从跟踪字典中移除已完成的任务
                    del future_to_url[future]
            
            # 等待所有剩余的下载任务完成
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        # 获取本地路径
                        local_path_abs, _ = get_local_path(base_netloc, url)
                        if local_path_abs:
                            # 保存资源
                            save_resource(url, content, local_path_abs)
                            
                            # 如果是CSS文件，解析并提取其中的URL
                            if url.lower().endswith('.css'):
                                css_text = content.decode('utf-8', errors='ignore')
                                extract_css_urls(css_text, url, base_netloc, local_path_abs, queue, downloaded_resources, current_depth)
                except Exception as e:
                    logger.error(f"处理下载结果时出错 {url}: {e}")

    except Exception as e:
        logger.error(f"克隆过程中发生意外错误: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()
        logger.info(f"克隆完成。已访问HTML页面: {len(visited_html)}。已下载资源: {len(downloaded_resources)}。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='本地克隆网站。')
    parser.add_argument('url', help='要克隆的网站的起始URL。')
    parser.add_argument('--depth', type=int, default=2, help='HTML页面的最大爬取深度（默认: 2）。')
    parser.add_argument('--output', default=MIRROR_DIR, help=f'克隆站点的输出目录（默认: {MIRROR_DIR}）。')
    parser.add_argument('--workers', type=int, default=5, help='用于并行下载资源的工作线程数（默认: 5）。')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        help='日志级别（默认: INFO）。')

    args = parser.parse_args()

    # 设置日志级别
    logger.setLevel(getattr(logging, args.log_level))

    # 更新MIRROR_DIR（如果指定）
    MIRROR_DIR = os.path.abspath(args.output)

    # 如果不存在，创建Mirror目录
    if not os.path.exists(MIRROR_DIR):
        os.makedirs(MIRROR_DIR)
        logger.info(f"创建输出目录: {MIRROR_DIR}")
    else:
        logger.info(f"使用现有输出目录: {MIRROR_DIR}")

    # 使用参数中的URL和深度
    clone_website(args.url, max_depth=args.depth, max_workers=args.workers)
