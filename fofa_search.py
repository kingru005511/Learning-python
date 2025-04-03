import requests
import base64
import time
import math
import ipaddress
import sys

FOFA_EMAIL = ''
FOFA_KEY = ''
FOFA_API = 'https://fofa.info/api/v1/search/all'

keyword = input("请输入你的fofa搜索关键词：").strip()

all_results = set()
output_file = 'fofa_search_results.txt'

# 全局变量记录首次检测到的总量
initial_total_size = 0

def fofa_search(query, page=1, size=10000):
    payload = {
        'email': FOFA_EMAIL,
        'key': FOFA_KEY,
        'qbase64': base64.b64encode(query.encode()).decode(),
        'page': page,
        'size': size,
        'fields': 'host'
    }
    try:
        response = requests.get(FOFA_API, params=payload, timeout=20)
        response.raise_for_status()
        results = response.json()
        if results.get('error'):
            print(f"\n搜索出错: {results['errmsg']}")
            return None, 0
        return results.get('results', []), results.get('size', 0)
    except Exception as e:
        print(f"\n请求出错: {e}")
        return None, 0

def check_fofa_api():
    test_query = 'domain="fofa.info"'
    result, _ = fofa_search(test_query, page=1, size=1)
    if result is None:
        print("❌ FOFA API不可用，请检查你的API Key和Email是否正确，或网络连接是否正常。")
        return False
    else:
        print("✅ FOFA API检测成功，开始搜索任务...\n")
        return True

def save_results_immediately():
    global initial_total_size
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in sorted(all_results):
            f.write(url + '\n')
    print(f"\n💾 已实时保存当前进度，共 {len(all_results)} 条数据。\n")

    # 判断任务是否已经完成
    if len(all_results) >= initial_total_size:
        print(f"🎉 当前已收集数据量 ({len(all_results)}) 已达到或超过首次检测总量 ({initial_total_size})，任务已完成！")
        sys.exit()

# 新增一个字典，用于记录每个IP段最初检测到的总数量
ip_segment_total_sizes = {}

# 递归细化IP段搜索函数（优化版）
ip_segment_total_sizes = {}

def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def recursive_search(ip_net):
    global all_results, ip_segment_total_sizes

    query = f'ip="{ip_net}" && {keyword}'

    if ip_net not in ip_segment_total_sizes:
        _, segment_total_size = fofa_search(query, page=1, size=1)
        ip_segment_total_sizes[ip_net] = segment_total_size
    else:
        segment_total_size = ip_segment_total_sizes[ip_net]

    if segment_total_size == 0:
        print(f'⚠️ IP段 {ip_net} 无数据，跳过。')
        return

    current_segment_results = {
        host for host in all_results
        if is_valid_ip(host.split(':')[0]) and ipaddress.ip_address(host.split(':')[0]) in ipaddress.ip_network(ip_net)
    }

    if len(current_segment_results) >= segment_total_size:
        print(f'✅ IP段 {ip_net} 已收集完整（{len(current_segment_results)}条），跳过进一步细分。')
        return

    if segment_total_size <= 10000:
        total_pages = math.ceil(segment_total_size / 10000)
        print(f'✅ IP段 {ip_net} 有 {segment_total_size} 条数据，共 {total_pages} 页，正在获取...')
        for page in range(1, total_pages + 1):
            results, _ = fofa_search(query, page=page, size=10000)
            if results:
                for item in results:
                    all_results.add(item)
            print(f'\r🔄 IP段 {ip_net} 第 {page}/{total_pages} 页获取完毕。', end='', flush=True)
            save_results_immediately()

            current_segment_results = {
                host for host in all_results
                if is_valid_ip(host.split(':')[0]) and ipaddress.ip_address(host.split(':')[0]) in ipaddress.ip_network(ip_net)
            }
            if len(current_segment_results) >= segment_total_size:
                print(f'\n✅ IP段 {ip_net} 已收集完整（{len(current_segment_results)}条），提前结束此IP段搜索。')
                return

        print(f'\n✅ IP段 {ip_net} 获取完毕。\n')
    else:
        print(f'🔍 IP段 {ip_net} 数据超过10000条({segment_total_size})，细分网段...')
        network = ipaddress.ip_network(ip_net)
        subnets = network.subnets(new_prefix=network.prefixlen + 8)
        for subnet in subnets:
            current_segment_results = {
                host for host in all_results
                if is_valid_ip(host.split(':')[0]) and ipaddress.ip_address(host.split(':')[0]) in network
            }
            if len(current_segment_results) >= segment_total_size:
                print(f'✅ 大IP段 {ip_net} 已收集完整（{len(current_segment_results)}条），停止继续细分。')
                return

            recursive_search(str(subnet))
            time.sleep(1)

if __name__ == "__main__":
    if not check_fofa_api():
        sys.exit()

    try:
        print("🔎 正在首次进行全网关键词搜索，以确定数据总量...")
        _, initial_total_size = fofa_search(keyword, page=1, size=1)
        print(f"📊 关键词 '{keyword}' 在全网共有 {initial_total_size} 条数据。\n")

        if initial_total_size == 0:
            print("⚠️ 全网无相关数据，任务结束。")
            sys.exit()

        if initial_total_size <= 10000:
            total_pages = math.ceil(initial_total_size / 10000)
            print(f"✅ 数据总量 ≤ 10000 ({initial_total_size} 条)，正在直接获取全部数据...")
            for page in range(1, total_pages + 1):
                results, _ = fofa_search(keyword, page=page, size=10000)
                if results:
                    for item in results:
                        all_results.add(item)
                print(f'\r🔄 第 {page}/{total_pages} 页获取完毕。', end='', flush=True)
                save_results_immediately()
            print(f"\n🎉 数据全部获取完毕，共获得 {len(all_results)} 条去重结果。")
        else:
            print(f"⚠️ 数据总量超过10000条，正在启动IP段细化遍历...\n")
            for i in range(1, 224):
                if i == 127:
                    continue
                ip_range = f'{i}.0.0.0/8'
                recursive_search(ip_range)
                print('⏳ 等待1秒，开始下一个大IP段搜索...\n')
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n⚠️ 用户主动中断了程序，正在保存当前进度...")
        save_results_immediately()
        sys.exit()

    except Exception as e:
        print(f"\n❌ 程序异常终止: {e}，正在保存当前进度...")
        save_results_immediately()
        sys.exit()

    finally:
        save_results_immediately()
        print(f'🎉 全部搜索完成或中断！共获得 {len(all_results)} 条去重结果，已导出到 "{output_file}" 中！')