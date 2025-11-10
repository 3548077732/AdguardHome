#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import requests
import datetime
from urllib.parse import urlparse
from typing import Set, List, Tuple

class AdGuardRulesSimplifier:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 域名文件位于 scripts/logs 下
        self.domain_file = os.path.join(self.base_dir, "scripts", "logs", "domain name.txt")
        # 输出文件改为 pure black.txt，位于仓库根目录
        self.output_file = os.path.join(self.base_dir, "pure black.txt")
        
        # 输入规则从本地合并产物 Black.txt 读取，避免远程依赖
        self.black_url = os.path.join(self.base_dir, "Black.txt")
        # 白名单来源：本地生成的 White.txt
        self.white_file = os.path.join(self.base_dir, "White.txt")
        self.autumn_url = "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt"
        self.github_url = "https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts"
    
    def read_updated_time_from_black(self) -> str:
        """从 Black.txt 头部读取更新时间，找不到则返回当前北京时间"""
        try:
            if os.path.exists(self.black_url):
                with open(self.black_url, 'r', encoding='utf-8', errors='ignore') as f:
                    for _ in range(10):  # 只检查前若干行
                        line = f.readline()
                        if not line:
                            break
                        s = line.strip().lstrip('\ufeff')
                        # 支持中英文冒号
                        m = re.match(r"^#\s*更新时间[:：]\s*(.+)$", s)
                        if m:
                            return m.group(1).strip()
        except Exception:
            pass
        # 回退：当前北京时间
        return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        
    def download_rules(self, url: str) -> List[str]:
        """加载规则文件：支持本地文件路径或HTTP(S)链接"""
        # 如果传入的是本地路径，直接读取文件
        if os.path.exists(url):
            try:
                print(f"读取本地规则: {url}")
                with open(url, 'r', encoding='utf-8', errors='ignore') as f:
                    return [line.rstrip('\n') for line in f]
            except Exception as e:
                print(f"读取本地规则失败 {url}: {e}")
                return []
        # 否则尝试作为网络地址下载
        try:
            print(f"正在下载规则: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text.splitlines()
        except Exception as e:
            print(f"下载规则失败 {url}: {e}")
            return []
    
    def load_domain_list(self) -> Set[str]:
        """加载domain name.txt中的域名"""
        domains = set()
        if os.path.exists(self.domain_file):
            try:
                with open(self.domain_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 提取域名部分（去掉计数）
                            domain = line.split()[0] if line.split() else line
                            domains.add(domain.lower())
                print(f"加载了 {len(domains)} 个域名")
            except Exception as e:
                print(f"读取域名文件失败: {e}")
        else:
            print("域名文件不存在")
        return domains
    
    def remove_comments(self, rules: List[str]) -> List[str]:
        """删除@！#开头的注释规则"""
        cleaned_rules = []
        for rule in rules:
            rule = rule.strip().lstrip('\ufeff')  # 去除可能的BOM
            if rule and not rule.startswith(('@', '!', '#')):
                cleaned_rules.append(rule)
        return cleaned_rules

    def load_whitelist_from_white(self) -> List[str]:
        """从 White.txt 读取白名单内容，跳过注释和空行，保留规则原样"""
        whitelist = []
        if os.path.exists(self.white_file):
            try:
                with open(self.white_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        s = line.strip().lstrip('\ufeff')
                        # 跳过头部注释和空行
                        if not s or s.startswith('#') or s.startswith('!'):
                            continue
                        # 保留 @@ 开头及已格式化的白名单规则
                        whitelist.append(s)
                print(f"读取 White.txt 白名单规则: {len(whitelist)} 条")
            except Exception as e:
                print(f"读取 White.txt 失败: {e}")
        else:
            print("White.txt 文件不存在，跳过追加白名单")
        return whitelist
    
    def extract_pipe_rules(self, rules: List[str]) -> Tuple[List[str], List[str]]:
        """提取|开头的规则并从原规则中删除"""
        pipe_rules = []
        remaining_rules = []
        
        for rule in rules:
            rule = rule.strip()
            if rule.startswith('|'):
                pipe_rules.append(rule)
            else:
                remaining_rules.append(rule)
        
        print(f"提取了 {len(pipe_rules)} 个|开头的规则")
        return pipe_rules, remaining_rules
    
    def extract_domain_from_rule(self, rule: str) -> str:
        """从规则中提取域名"""
        # 处理|开头的规则
        if rule.startswith('||'):
            # ||example.com^ -> example.com
            domain = rule[2:].split('^')[0].split('/')[0].split(':')[0]
        elif rule.startswith('|'):
            # |http://example.com -> example.com
            try:
                parsed = urlparse(rule[1:])
                domain = parsed.netloc or parsed.path.split('/')[0]
            except:
                domain = rule[1:].split('/')[0].split(':')[0]
        else:
            # 其他格式尝试提取域名
            domain = rule.split('/')[0].split(':')[0]
        
        return domain.lower().strip()
    
    def match_domains_and_restore(self, pipe_rules: List[str], remaining_rules: List[str], 
                                 domain_set: Set[str]) -> List[str]:
        """将提取规则的域名与domain name.txt匹配，匹配上的放回原规则"""
        restored_rules = remaining_rules.copy()
        matched_count = 0
        
        for rule in pipe_rules:
            domain = self.extract_domain_from_rule(rule)
            if domain in domain_set:
                restored_rules.append(rule)
                matched_count += 1
        
        print(f"匹配并恢复了 {matched_count} 个规则")
        return restored_rules
    
    def process_hosts_file(self, hosts_lines: List[str]) -> List[str]:
        """处理hosts文件格式，转换为AdGuard格式"""
        adguard_rules = []
        for line in hosts_lines:
            line = line.strip().lstrip('\ufeff')  # 去除可能的BOM
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2 and parts[0] in ['0.0.0.0', '127.0.0.1']:
                    domain = parts[1]
                    # 转换为AdGuard格式
                    adguard_rules.append(f"||{domain}^")
        return adguard_rules
    
    def merge_and_deduplicate(self, *rule_lists: List[str]) -> List[str]:
        """合并多个规则列表并去重"""
        all_rules = set()
        
        for rules in rule_lists:
            for rule in rules:
                rule = rule.strip().lstrip('\ufeff')  # 去除可能的BOM
                if rule and not rule.startswith(('@', '!', '#')):
                    all_rules.add(rule)
        
        return sorted(list(all_rules))

    def reverse_rules(self, rules: List[str]) -> List[str]:
        """仅倒序规则列表（不影响文件头部注释）"""
        return list(reversed(rules))
    
    def save_rules(self, rules: List[str], filename: str = None, black_count: int = None, updated_time: str = None, whitelist_rules: List[str] = None, whitelist_count: int = None):
        """保存规则到文件，头部与 Black.txt 一致，并将白名单追加到底部"""
        if filename is None:
            filename = self.output_file
        if updated_time is None:
            # 使用北京时间（UTC+8）
            updated_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        # 规则计数
        if rules is None:
            rules = []
        if whitelist_rules is None:
            whitelist_rules = []
        if black_count is None:
            black_count = len([r for r in rules if str(r).strip()])
        if whitelist_count is None:
            whitelist_count = len([w for w in whitelist_rules if str(w).strip()])
        total_count = black_count + whitelist_count

        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(f"# 更新时间: {updated_time}\n")
                f.write(f"# 总规则数：{total_count} (黑名单: {black_count}, 白名单: {whitelist_count})\n")
                f.write(f"# 作者名称: Menghuibanxian  酷安名: 梦半仙\n")
                f.write(f"# 作者主页: https://github.com/Menghuibanxian/AdguardHome\n")
                f.write("\n")
                # 写入黑名单
                for rule in rules:
                    if str(rule).strip():
                        f.write(rule + "\n")
                # 追加白名单到底部
                for w in whitelist_rules:
                    if str(w).strip():
                        f.write(w + "\n")
            print(f"规则已保存到: {filename}")
            print(f"黑名单: {black_count}，白名单: {whitelist_count}，总计: {total_count}")
        except Exception as e:
            print(f"保存规则失败: {e}")
    
    def run(self, override_time: str = None):
        """运行主程序"""
        print("=== AdGuard规则简化器 ===")
        
        # 1. 加载域名列表
        print("\n1. 加载域名列表...")
        domain_set = self.load_domain_list()
        
        # 2. 下载并处理Black.txt规则
        print("\n2. 处理Black.txt规则...")
        black_rules = self.download_rules(self.black_url)
        if not black_rules:
            print("无法下载Black.txt规则，跳过处理")
            return
        
        # 删除注释
        black_rules = self.remove_comments(black_rules)
        print(f"删除注释后剩余 {len(black_rules)} 个规则")
        
        # 提取|开头的规则
        pipe_rules, remaining_rules = self.extract_pipe_rules(black_rules)
        
        # 匹配域名并恢复规则
        final_black_rules = self.match_domains_and_restore(pipe_rules, remaining_rules, domain_set)
        
        # 3. 下载并处理秋风规则
        print("\n3. 处理秋风规则...")
        autumn_rules = self.download_rules(self.autumn_url)
        autumn_rules = self.remove_comments(autumn_rules)
        print(f"秋风规则: {len(autumn_rules)} 个")
        
        # 4. 下载并处理GitHub加速规则
        print("\n4. 处理GitHub加速规则...")
        github_hosts = self.download_rules(self.github_url)
        github_rules = self.process_hosts_file(github_hosts)
        print(f"GitHub加速规则: {len(github_rules)} 个")
        
        # 5. 合并所有规则并去重
        print("\n5. 合并规则并去重...")
        final_rules = self.merge_and_deduplicate(final_black_rules, autumn_rules, github_rules)

        # 5.1 倒序规则（保持文件头部注释在顶部）
        final_rules = self.reverse_rules(final_rules)
        
        # 6. 读取 White.txt 并保存最终规则（白名单追加到底部）
        print("\n6. 保存最终规则并追加白名单...")
        updated_time = override_time if override_time else self.read_updated_time_from_black()
        whitelist_rules = self.load_whitelist_from_white()
        black_count = len([r for r in final_rules if str(r).strip()])
        white_count = len([w for w in whitelist_rules if str(w).strip()])
        self.save_rules(final_rules, updated_time=updated_time, black_count=black_count, whitelist_rules=whitelist_rules, whitelist_count=white_count)
        
        print("\n=== 处理完成 ===")

if __name__ == "__main__":
    import sys
    simplifier = AdGuardRulesSimplifier()
    override_time = None
    if "--timestamp" in sys.argv:
        try:
            idx = sys.argv.index("--timestamp")
            override_time = sys.argv[idx+1]
        except Exception:
            pass
    simplifier.run(override_time)
