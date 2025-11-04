#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import requests
from urllib.parse import urlparse
from typing import Set, List, Tuple

class AdGuardRulesSimplifier:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 域名文件位于 scripts/logs 下
        self.domain_file = os.path.join(self.base_dir, "scripts", "logs", "domain name.txt")
        # 输出的 Black.txt 位于仓库根目录
        self.output_file = os.path.join(self.base_dir, "Black.txt")
        
        # Black.txt 使用本地合并产物，避免远程依赖
        self.black_url = self.output_file
        self.autumn_url = "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt"
        self.github_url = "https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts"
        
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
    
    def save_rules(self, rules: List[str], filename: str = None):
        """保存规则到文件"""
        if filename is None:
            filename = self.output_file
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("! AdGuard规则简化版\n")
                f.write(f"! 总计规则数: {len(rules)}\n")
                f.write("! 生成时间: " + str(__import__('datetime').datetime.now()) + "\n")
                f.write("\n")
                
                for rule in rules:
                    f.write(rule + "\n")
            
            print(f"规则已保存到: {filename}")
            print(f"总计规则数: {len(rules)}")
        except Exception as e:
            print(f"保存规则失败: {e}")
    
    def run(self):
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
        
        # 6. 保存最终规则
        print("\n6. 保存最终规则...")
        self.save_rules(final_rules)
        
        print("\n=== 处理完成 ===")

if __name__ == "__main__":
    simplifier = AdGuardRulesSimplifier()
    simplifier.run()
