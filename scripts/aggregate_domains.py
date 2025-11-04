#!/usr/bin/env python3
import os
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
import glob
import shutil

# 仓库根目录
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 日志目录位于 scripts/logs
LOGS_DIR = os.path.join(REPO_ROOT, "scripts", "logs")
# 域名统计文件位于 logs 目录
OUTPUT_FILE = os.path.join(LOGS_DIR, "domain name.txt")
LOG_FILE = os.path.join(LOGS_DIR, "log")

# 读取上次处理的最新日志信息
def read_latest_log_info():
    if not os.path.exists(LOG_FILE):
        return None, None
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().strip()
            if content:
                parts = content.split(' ', 1)
                if len(parts) == 2:
                    domain, timestamp = parts
                    return domain, timestamp
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    return None, None

# 保存最新日志信息的函数 - 简化格式为"域名 时间戳"
def save_latest_log_info(domain, timestamp):
    # 格式化时间戳为年月日时分秒
    formatted_time = format_timestamp(timestamp)
    
    # 确保域名和时间戳都有效
    if domain and formatted_time:
        with open(LOG_FILE, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(f"{domain} {formatted_time}")
    else:
        print(f"Warning: Invalid domain or timestamp: domain='{domain}', timestamp='{timestamp}', formatted='{formatted_time}'")

# 合并现有的domain name.txt与新统计结果
def merge_domain_counts(new_counts):
    existing_counts = {}
    
    # 读取现有的domain name.txt
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.rsplit(' ', 1)
                        if len(parts) == 2:
                            domain, count = parts
                            try:
                                existing_counts[domain] = int(count)
                            except ValueError:
                                print(f"Warning: Invalid count format in line: {line}")
        except Exception as e:
            print(f"Error reading existing domain name.txt: {e}")
    
    # 合并计数
    for domain, count in new_counts.items():
        if domain in existing_counts:
            existing_counts[domain] += count
        else:
            existing_counts[domain] = count
    
    return existing_counts

# 格式化时间戳为标准格式
def format_timestamp(timestamp):
    if not timestamp:
        return ""
        
    # 如果是纯数字格式且长度为14，直接返回
    if isinstance(timestamp, str) and timestamp.isdigit() and len(timestamp) == 14:
        return timestamp
        
    try:
        # 尝试解析ISO格式时间戳
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        # 转换为年月日时分秒格式
        return dt.strftime('%Y%m%d%H%M%S')
    except (ValueError, TypeError, AttributeError):
        # 如果解析失败，尝试使用正则表达式提取年月日时分秒
        try:
            match = re.search(r'(\d{4})-?(\d{2})-?(\d{2})T?(\d{2}):?(\d{2}):?(\d{2})', str(timestamp))
            if match:
                year, month, day, hour, minute, second = match.groups()
                return f"{year}{month}{day}{hour}{minute}{second}"
        except:
            pass
    
    # 如果所有方法都失败，返回空字符串而不是原始时间戳
    print(f"Warning: Could not format timestamp: {timestamp}")
    return ""

def main():
    # 获取所有日志文件
    log_files = glob.glob(os.path.join(LOGS_DIR, "querylog*.json"))
    
    # 如果没有找到querylog文件，直接退出
    if not log_files:
        print("No querylog files found. No updates needed.")
        return
    
    # 读取上次处理的最新日志信息
    last_domain, last_timestamp = read_latest_log_info()
    if last_domain and last_timestamp:
        print(f"Last processed log: domain={last_domain}, timestamp={last_timestamp}")
    
    # 按文件名排序（通常包含时间戳）
    log_files.sort()
    
    # 域名计数器
    domain_counts = Counter()
    
    # 用于去重的集合
    seen_events = set()
    
    # 最新的日志信息
    latest_domain = None
    latest_timestamp = None
    
    # 处理每个日志文件
    total_events = 0
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # 逐行读取NDJSON格式
                line_index = 0
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # 解析JSON对象
                        entry = json.loads(line)
                        
                        # 提取域名 (QH字段)
                        domain = None
                        if 'QH' in entry:
                            domain = entry['QH']
                        
                        # 提取时间 (T字段)
                        timestamp = None
                        if 'T' in entry:
                            timestamp = entry['T']
                        
                        # 提取客户端IP (IP字段)
                        client_ip = None
                        if 'IP' in entry:
                            client_ip = entry['IP']
                        
                        # 提取查询类型 (QT字段)
                        query_type = None
                        if 'QT' in entry:
                            query_type = entry['QT']
                        
                        # 如果找到域名
                        if domain and timestamp:
                            # 格式化当前时间戳
                            formatted_current = format_timestamp(timestamp)
                            
                            # 检查是否需要跳过这条记录
                            # 规则1: 如果域名和时间戳完全匹配，则跳过
                            # 规则2: 如果时间戳早于或等于上次处理的时间戳，则跳过
                            if last_domain and last_timestamp:
                                if (domain == last_domain and formatted_current == last_timestamp) or formatted_current < last_timestamp:
                                    continue
                            
                            # 更新最新日志信息
                            if latest_timestamp is None or timestamp > latest_timestamp:
                                latest_domain = domain
                                latest_timestamp = timestamp
                            
                            # 创建唯一键以避免重复计数
                            event_key = None
                            if client_ip and query_type:
                                event_key = (domain, timestamp, client_ip, query_type)
                            else:
                                # 如果缺少客户端IP或查询类型，则使用文件名+行号作为唯一键
                                event_key = (domain, os.path.basename(log_file), line_index)
                            
                            # 如果这个事件之前没见过，则计数
                            if event_key not in seen_events:
                                domain_counts[domain] += 1
                                seen_events.add(event_key)
                                total_events += 1
                        
                    except json.JSONDecodeError:
                        # 忽略无效的JSON行
                        pass
                    
                    line_index += 1
                    
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
    
    # 如果没有处理任何新事件，直接退出
    if total_events == 0:
        print("No new events to process. No updates needed.")
        return
    
    # 合并与现有结果
    merged_counts = merge_domain_counts(domain_counts)
    
    # 按计数降序和域名升序排序
    sorted_domains = sorted(merged_counts.items(), key=lambda x: (-x[1], x[0]))
    
    # 写入结果文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for domain, count in sorted_domains:
            f.write(f"{domain} {count}\n")
    
    print(f"Wrote '{OUTPUT_FILE}' with {len(sorted_domains)} domains. Unique events: {total_events}")
    
    # 保存最新日志信息
    if latest_domain and latest_timestamp:
        save_latest_log_info(latest_domain, latest_timestamp)
        print(f"Saved latest log info to '{LOG_FILE}'")
    
    # 删除所有querylog开头的文件
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"Deleted: {os.path.basename(log_file)}")
        except Exception as e:
            print(f"Error deleting {log_file}: {e}")

if __name__ == "__main__":
    main()
