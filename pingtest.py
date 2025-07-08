import requests
import yaml
import time
import os
import logging
import socket
import concurrent.futures
import traceback
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义常量
TIMEOUT = 5  # 秒
MAX_WORKERS = 5  # 降低并发数，避免端口冲突
NORMAL_LINKS_FILE = 'normal_links.txt'
TIMEOUT_LINKS_FILE = 'timeout_links.txt'
LOCAL_PROXY_PORT_START = 1080  # 本地代理端口起始值
TEST_URL = "https://cp.cloudflare.com/generate_204"  # 测试URL

def get_node_key(node):
    non_key_fields = ['name', 'remarks', 'group', 'ps', 'tag']
    key_fields = {k: v for k, v in node.items() if k not in non_key_fields}
    sorted_items = sorted(key_fields.items(), key=lambda x: x[0])
    key_str = ','.join(f"{k}:{v}" for k, v in sorted_items)
    return key_str

def remove_duplicate_nodes(nodes):
    """去除重复的节点"""
    unique_nodes = {}
    duplicate_count = 0
    for node in nodes:
        node_key = get_node_key(node)
        if node_key not in unique_nodes:
            unique_nodes[node_key] = node
        else:
            duplicate_count += 1
    if duplicate_count > 0:
        logging.info(f"移除了 {duplicate_count} 个重复的节点")
    return list(unique_nodes.values())

def is_github_gist_url(url):
    """检查URL是否是GitHub Gist的URL"""
    return "gist.githubusercontent.com" in url

def download_subscription(url):
    """从GitHub Gist URL下载订阅内容"""
    try:
        if not is_github_gist_url(url):
            logging.error("错误: 仅支持GitHub Gist的URL")
            return None
        logging.info("检测到GitHub Gist链接，开始下载...")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        logging.info("订阅内容下载成功。")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"下载订阅内容时出错: {e}")
        return None

def parse_subscription(content):
    """解析订阅内容"""
    try:
        subscription = yaml.safe_load(content)
        if subscription is None:
            logging.warning("解析后的内容为空，可能是YAML格式问题或内容为空。")
            return []
        proxies = subscription.get('proxies', [])
        unique_proxies = remove_duplicate_nodes(proxies)
        logging.info(f"去重前有 {len(proxies)} 个节点，去重后有 {len(unique_proxies)} 个节点")
        return unique_proxies
    except yaml.YAMLError as e:
        logging.error(f"解析YAML订阅内容时出错: {e}")
        return []
    except Exception as e:
        logging.error(f"解析订阅内容时发生未知错误: {e}")
        return []

def direct_socket_test(server, port, timeout=5):
    """直接使用socket测试连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((server, port))
        end_time = time.time()
        sock.close()

        if result == 0:
            return (end_time - start_time) * 1000  # 转换为毫秒
        else:
            return None
    except Exception as e:
        logging.debug(f"直接socket测试失败: {e}")
        return None

def test_node_delay(node):
    """测试单个节点延迟"""
    server = node.get('server', '')
    port = int(node.get('port', 0))
    node_name = node.get('name', '未知节点')

    if not server or not port:
        logging.debug(f"节点 '{node_name}' 缺少服务器或端口信息")
        return None

    # 仅保留直接socket连接测试
    direct_delay = direct_socket_test(server, port)
    if direct_delay is not None:
        # 去除输出每个节点延迟的日志信息
        return direct_delay
    else:
        logging.debug(f"节点 '{node_name}' 直接连接失败")  # 使用debug级别，避免干扰用户视图
        return None

def format_time(seconds):
    """将秒数转换为分钟和秒的格式"""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}分钟{remaining_seconds}秒" if minutes > 0 else f"{remaining_seconds}秒"

def format_node(node):
    """将节点字典格式化为指定的字符串格式"""
    items = []
    for key, value in node.items():
        if isinstance(value, str):
            if any(c.isspace() for c in value) or not value.isalnum():
                value_str = f'"{value}"'
            else:
                value_str = value
        elif isinstance(value, bool):
            value_str = str(value).lower()
        else:
            value_str = str(value)
        items.append(f"{key}: {value_str}")
    formatted = ", ".join(items)
    return f"  - {{{formatted}}}"

def save_nodes_to_file(nodes, file_path):
    """将节点信息保存到txt文件中"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("proxies:\n")
            for node in nodes:
                f.write(format_node(node) + '\n')
        logging.info(f"节点信息已保存到: {file_path}")
    except Exception as e:
        logging.error(f"保存节点信息时出错: {e}")

def main():
    print("请输入GitHub Gist原始内容链接:")
    subscription_url = input()

    if not is_github_gist_url(subscription_url):
        logging.error("错误: 仅支持GitHub Gist的URL")
        return

    subscription_content = download_subscription(subscription_url)
    if not subscription_content:
        logging.error("无法下载订阅内容。")
        return

    nodes = parse_subscription(subscription_content)
    if not nodes:
        logging.error("无法解析订阅内容。")
        return

    logging.info(f"成功解析到 {len(nodes)} 个节点")

    timeout_nodes = []
    normal_nodes = []
    start_time = time.time()

    logging.info(f"开始测试 {len(nodes)} 个节点的延迟，请稍候...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_node = {executor.submit(test_node_delay, node): node for node in nodes}
        processed_count = 0
        total_nodes = len(nodes)
        show_long_test_message = False
        last_update_time = start_time

        for future in concurrent.futures.as_completed(future_to_node):
            node = future_to_node[future]
            processed_count += 1

            try:
                delay = future.result()
                if delay is None:
                    timeout_nodes.append(node)
                else:
                    node['delay'] = delay
                    normal_nodes.append(node)
            except Exception as exc:
                logging.debug(f"节点 '{node.get('name', '未知')}' ({node.get('server', '')}:{node.get('port', '')}) 测试时发生未知异常: {exc}")
                timeout_nodes.append(node)

            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time > 10 and not show_long_test_message:
                print("\n本次总节点有点多，正在测试节点延迟中，主人请不要关闭窗口走开哦~")
                show_long_test_message = True

            if (current_time - last_update_time) >= 1 or processed_count == total_nodes:
                if show_long_test_message:
                    print(f"\r已测试 {processed_count}/{total_nodes} 个节点，累计时间：{format_time(elapsed_time)}", end="", flush=True)
                last_update_time = current_time

    total_time = time.time() - start_time
    if show_long_test_message or total_nodes > 0:
        print()

    normal_nodes_count = len(normal_nodes)
    timeout_nodes_count = len(timeout_nodes)

    logging.info(f"测试完成，总用时：{format_time(total_time)}")
    logging.info(f"正常节点数量: {normal_nodes_count}")
    logging.info(f"超时节点数量: {timeout_nodes_count}")

    # 按延迟排序
    normal_nodes.sort(key=lambda x: x.get('delay', float('inf')))

    # 保存结果
    save_nodes_to_file(normal_nodes, NORMAL_LINKS_FILE)
    save_nodes_to_file(timeout_nodes, TIMEOUT_LINKS_FILE)

if __name__ == "__main__":
    main()
