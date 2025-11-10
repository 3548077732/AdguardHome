import os
import re
import requests
import time
import json
import datetime

# 获取北京时间
def get_beijing_time():
    """获取北京时间"""
    # 使用多个API源获取北京时间，增加可靠性
    urls = [
        "https://quan.suning.com/getSysTime.do",  # 优先使用HTTPS版本的苏宁API
        "https://www.baidu.com",                 # 从响应头获取时间
        "https://a.jd.com/js/union_ajax.js",     # 从响应头获取时间
        "https://pages.github.com",              # 从响应头获取时间
        "https://consumer.huawei.com",           # 从响应头获取时间
        "https://www.mi.com",                    # 从响应头获取时间
        "http://quan.suning.com/getSysTime.do"    # 备用：HTTP版本的苏宁API
    ]
    
    for url in urls:
        try:
            # 设置较短的超时时间，避免长时间等待
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, timeout=3, headers=headers)
            
            # 从响应头中获取时间
            if 'Date' in response.headers:
                date_str = response.headers['Date']
                # 解析HTTP日期格式
                gmt_time = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
                # 转换为北京时间（GMT+8）
                beijing_time = gmt_time + datetime.timedelta(hours=8)
                return beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            # 出错时继续尝试下一个源
            continue
    
    # 如果所有API都失败，回退到本地时间
    print("获取北京时间失败，使用本地时间")
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 文件路径配置
COMBINED_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Black.txt")
WHITE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "White.txt")

# 黑名单源
BLACKLIST_SOURCES = {
    "AdGuard DNS filter     ": "https://adguardteam.github.io/HostlistsRegistry/assets/filter_1.txt",
    "秋风的规则              ": "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt",
    "GitHub加速              ": "https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts",
    #"广告规则                ": "https://raw.githubusercontent.com/huantian233/HT-AD/main/AD.txt",
    #"DD自用                  ": "https://raw.githubusercontent.com/afwfv/DD-AD/main/rule/DD-AD.txt",
    "消失DD                  ": "https://raw.githubusercontent.com/afwfv/DD-AD/refs/heads/release/dns.txt",
    #"大萌主           　     ": "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt",
    "逆向涉猎       　       ": "https://raw.githubusercontent.com/790953214/qy-Ads-Rule/main/black.txt",
    "下个ID见                ": "https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts",
    #"那个谁520               ": "https://raw.githubusercontent.com/qq5460168/666/master/rules.txt",
    "1hosts                  ": "https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt",
    "茯苓的广告规则    　     ": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingBlockList.txt",
    "立场不定的               ": "https://raw.githubusercontent.com/Menghuibanxian/Minecraft/refs/heads/main/AdguardHome.txt",
    #"anti-ad混合名单   　     ": "https://anti-ad.net/easylist.txt",
    #"酷安 番茄 七猫　         ": "https://d.kstore.dev/download/10497/xiaoshuo.txt",
    #"酷安          　         ": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/refs/heads/Master/OtherRules/CoolapkRules.txt",
    "那个谁520   　　　　     ": "https://raw.githubusercontent.com/qq5460168/dangchu/main/black.txt"
}

#　#
# ##
# 白名单源
WHITELIST_SOURCES = {
    "茯苓允许列表              ": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingAllowList.txt",
    "qq5460168                ": "https://raw.githubusercontent.com/qq5460168/666/master/allow.txt",
    "个人自用白名单            ": "https://raw.githubusercontent.com/qq5460168/dangchu/main/white.txt",
    #"酷安cocieto白名单         ": "https://raw.githubusercontent.com/urkbio/adguardhomefilter/main/whitelist.txt",
    "BlueSkyXN          　     ": "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/ok.txt",
    #"那个谁520广告白名单 　     ": "https://raw.githubusercontent.com/qq5460168/EasyAds/main/allow.txt",
    #"AdGuardHome通用白名单 　   ": "https://raw.githubusercontent.com/mphin/AdGuardHomeRules/main/Allowlist.txt",
    #"jhsvip白名单               ": "https://raw.githubusercontent.com/jhsvip/ADRuls/main/white.txt",
    #"liwenjie119白名单          ": "https://raw.githubusercontent.com/liwenjie119/adg-rules/master/white.txt",
    #"喵二白名单                 ": "https://raw.githubusercontent.com/miaoermua/AdguardFilter/main/whitelist.txt",
    "Cats-Team白名单          　": "https://raw.githubusercontent.com/Cats-Team/AdRules/script/script/allowlist.txt",
    "那个谁520 　　　          　": "https://raw.githubusercontent.com/qq5460168/dangchu/main/white.txt",
    "浅笑白名单                  ": "https://raw.githubusercontent.com/user001235/112/main/white.txt"
}

#    "冷漠白名单         　     ": "https://file-git.trli.club/file-hosts/allow/Domains",            暂时别用qq.com被白名单了
#

def remove_comments_and_blank_lines(rules):
    """移除规则中的注释和空行（保留正则中的 ! 和 #）"""
    result = []
    for raw in rules:
        line = raw.strip()
        # 跳过空行和以 ! 或 # 开头的整行注释
        if not line or line.startswith("!") or line.startswith("#"):
            continue
        # 仅移除以空白跟随的内联注释片段，例如："rule  # comment" 或 "rule  ! comment"
        # 避免误删正则中的 "?!"、"#[...]" 等模式
        line = re.sub(r"\s[!#].*$", "", line).strip()
        if line:
            result.append(line)
    return result

def extract_whitelist_from_blacklist(blacklist_rules):
    """从黑名单规则中提取规则"""
    # 假设白名单规则在黑名单中以特定格式存在，例如以@@开头（AdGuard格式）
    whitelist_rules = [rule for rule in blacklist_rules if rule.startswith("@@")]
    # 过滤后的黑名单规则（移除白名单规则）
    filtered_blacklist = [rule for rule in blacklist_rules if not rule.startswith("@@")]
    return filtered_blacklist, whitelist_rules

def deduplicate_rules(rules):
    """移除重复的规则"""
    # 使用集合去重并保持顺序
    seen = set()
    result = []
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            result.append(rule)
    return result

def parse_rule_components(rule: str):
    s = rule.strip()
    comps = {
        "is_comment": s.startswith("#") or s.startswith("!"),
        "is_regex": s.startswith("/") and s.endswith("/"),
        "is_whitelist": s.startswith("@@"),
        "is_hosts": False,
        "is_basic_adguard": False,
        "domain": None,
        "has_modifiers": False,
        "modifiers": []
    }
    if not s or comps["is_comment"]:
        return comps
    # hosts 格式
    m = re.match(r'^(?:0\.0\.0\.0|127\.0\.0\.1|::1?)\s+([^\s#]+)', s)
    if m:
        comps["is_hosts"] = True
        comps["domain"] = m.group(1).strip()
        return comps
    # 是否包含修饰符
    if "$" in s:
        comps["has_modifiers"] = True
        mods = s[s.find("$")+1:]
        comps["modifiers"] = [x.strip() for x in mods.split(",") if x.strip()]
    # AdGuard 基本语法 ||domain^ 或 @@||domain^
    if s.startswith("@@||"):
        rest = s[4:]
        dm = re.match(r'^([^\^\$\s]+)', rest)
        if dm:
            comps["is_basic_adguard"] = True
            comps["domain"] = dm.group(1)
            return comps
    if s.startswith("||"):
        rest = s[2:]
        dm = re.match(r'^([^\^\$\s]+)', rest)
        if dm:
            comps["is_basic_adguard"] = True
            comps["domain"] = dm.group(1)
            return comps
    # 纯域名行（Domains-only syntax）
    if ' ' not in s and not s.startswith('|'):
        rest = s[2:] if s.startswith("@@") else s
        dm = re.match(r'^([^\^\$\s]+)', rest)
        if dm:
            dom = dm.group(1)
            if re.match(r'^[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+$', dom) and "*" not in dom:
                comps["domain"] = dom
    return comps

def format_whitelist_rule(rule):
    """白名单规则尽量保留原始格式；仅在缺少 @@ 时最小补全"""
    s = rule.strip()
    if not s:
        return s

    # 已是白名单规则，原样返回（支持 @@||、@@|、@@/regex/ 等）
    if s.startswith("@@"):
        return s

    # 阻止规则或锚点形式（|| 或 |）但没有 @@：仅前置 @@，其余保持不变
    if s.startswith("||") or s.startswith("|"):
        return "@@" + s

    # 纯域名（无前后缀与修饰符）：最小补全为 @@||domain^
    dm = re.match(r"^([A-Za-z0-9.-]+\.[A-Za-z0-9.-]+)$", s)
    if dm:
        return "@@||" + dm.group(1) + "^"

    # 其他情况保持原样
    return s

def download_blacklist_sources():
    """下载所有黑名单源的规则"""
    all_blacklist_rules = []
    
    print(f"开始下载 {len(BLACKLIST_SOURCES)} 个黑名单源...")
    
    for name, url in BLACKLIST_SOURCES.items():
        try:
            print(f"正在下载 {name} ({url})...")
            response = requests.get(url, timeout=30)  # 增加超时时间
            response.raise_for_status()
            
            # 处理不同格式的规则文件
            rules = response.text.split("\n")
            # 移除注释和空行
            cleaned_rules = remove_comments_and_blank_lines(rules)
            
            all_blacklist_rules.extend(cleaned_rules)
            print(f"成功下载 {name}，获取到 {len(cleaned_rules)} 条规则")
            
            # 添加延迟以避免请求过于频繁
            time.sleep(1)
        except Exception as e:
            print(f"下载 {name} 失败 ({url}): {e}")
    
    print(f"所有黑名单源下载完成，共获取到 {len(all_blacklist_rules)} 条规则")
    return all_blacklist_rules

def download_whitelist_sources():
    """下载所有白名单源的规则"""
    all_whitelist_rules = []
    
    print(f"开始下载 {len(WHITELIST_SOURCES)} 个白名单源...")
    
    for name, url in WHITELIST_SOURCES.items():
        try:
            print(f"正在下载 {name} ({url})...")
            response = requests.get(url, timeout=30)  # 增加超时时间
            response.raise_for_status()
            
            # 处理不同格式的规则文件
            rules = response.text.split("\n")
            # 移除注释和空行
            cleaned_rules = remove_comments_and_blank_lines(rules)
            
            all_whitelist_rules.extend(cleaned_rules)
            print(f"成功下载 {name}，获取到 {len(cleaned_rules)} 条规则")
            
            # 添加延迟以避免请求过于频繁
            time.sleep(1)
        except Exception as e:
            print(f"下载 {name} 失败 ({url}): {e}")
    
    print(f"所有白名单源下载完成，共获取到 {len(all_whitelist_rules)} 条规则")
    return all_whitelist_rules

def extract_domains_from_rules(rules, is_whitelist=False):
    """从规则中提取域名（黑名单仅统计无修饰的纯域名规则）"""
    domains = set()
    for rule in rules:
        c = parse_rule_components(rule)
        if c["domain"] and "*" not in c["domain"]:
            if not is_whitelist and (c["has_modifiers"] or c["is_regex"]):
                continue
            domains.add(c["domain"])
    return domains

def remove_conflicting_rules(blacklist_rules, whitelist_rules):
    """移除重复并报告潜在冲突（不删除高级规则，避免误伤）"""
    blacklist_domains = extract_domains_from_rules(blacklist_rules, is_whitelist=False)
    whitelist_domains = extract_domains_from_rules(whitelist_rules, is_whitelist=True)
    conflicting_domains = blacklist_domains.intersection(whitelist_domains)
    print(f"发现 {len(conflicting_domains)} 个潜在冲突域名（保留两侧规则，避免误删）")

    # 黑名单：仅对无修饰的纯域名按域名去重；保留带修饰/正则/通配的高级规则
    filtered_blacklist = []
    processed_domains = set()
    for rule in blacklist_rules:
        c = parse_rule_components(rule)
        if c["domain"] and not c["has_modifiers"] and not c["is_regex"] and "*" not in c["domain"]:
            if c["domain"] in processed_domains:
                continue
            processed_domains.add(c["domain"])
        filtered_blacklist.append(rule)

    # 白名单保持原样（已在上游做文本去重）
    filtered_whitelist = whitelist_rules[:]
    print(f"过滤后白名单规则数量: {len(filtered_whitelist)}")

    return filtered_blacklist, filtered_whitelist

def process_rules(rules):
    """处理规则，去除不需要的内容"""
    original_rules = []  # 原规则
    extracted_rules = []  # 提取规则（以|开头的规则）
    
    # 首先分离原规则和提取规则
    for line in rules:
        if line.startswith("|"):
            extracted_rules.append(line)
        else:
            original_rules.append(line)
    
    # 处理原规则------去除特殊字符(!或$)的行-------去除定字符开头的行(/、.、-)------------
    usable_original = []
    for line in original_rules:
        if (not line or                           # 空行
            "!" in line or "$" in line or         # 包含特殊字符
            "/" in line or                        # 包含/
            line.startswith((".", "-"))):         # 特定开头
            continue
        usable_original.append(line)
    
    # 处理提取规则-----------------跳过$!--------暂时不拦截$---------------------------
    usable_extracted = []
    for line in extracted_rules:
        if (not line or "!" in line or
            "/" in line):                         # 包含/
            continue
        usable_extracted.append(line)
    
    # 合并处理后的规则，顺序：提取规则 + 原规则
    final_rules = usable_extracted + usable_original
    return final_rules

def main(generate_white_file=True, override_time: str = None):
    print("开始处理AdGuardHome规则...")
    
    # 获取当前北京时间或使用传入的统一时间戳
    current_time = override_time if override_time else get_beijing_time()
    
    # 下载所有黑名单源
    blacklist_rules = download_blacklist_sources()
    
    # 从黑名单中提取白名单规则
    filtered_blacklist, extracted_whitelist = extract_whitelist_from_blacklist(blacklist_rules)
    print(f"从黑名单中提取的白名单规则数量: {len(extracted_whitelist)}")
    print(f"过滤后的黑名单规则数量: {len(filtered_blacklist)}")
    
    # 黑名单去重
    deduplicated_blacklist = deduplicate_rules(filtered_blacklist)
    print(f"去重后的黑名单规则数量: {len(deduplicated_blacklist)}")
    
    # 下载白名单源
    downloaded_whitelist = download_whitelist_sources()
    print(f"下载的白名单规则数量: {len(downloaded_whitelist)}")
    
    # 合并提取的白名单和下载的白名单
    merged_whitelist = extracted_whitelist + downloaded_whitelist
    
    # 去重
    deduplicated_whitelist = deduplicate_rules(merged_whitelist)
    print(f"合并去重后的白名单规则数量: {len(deduplicated_whitelist)}")
    
    # 移除冲突和重复的规则
    final_blacklist, filtered_whitelist = remove_conflicting_rules(deduplicated_blacklist, deduplicated_whitelist)
    print(f"移除冲突规则后的黑名单数量: {len(final_blacklist)}")
    print(f"过滤后的白名单数量: {len(filtered_whitelist)}")
    
    # 直接合并黑名单和白名单到 Black.txt，不创建临时文件
    # 准备黑名单内容（过滤掉以[开头且以]结尾的行）
    blacklist_content_lines = []
    for rule in final_blacklist:
        if not (rule.startswith('[') and rule.endswith(']')):
            blacklist_content_lines.append(rule)
    
    # 对黑名单规则进行额外处理
    processed_blacklist = process_rules(blacklist_content_lines)
    
    # 准备白名单内容（过滤掉以[开头且以]结尾的行）
    whitelist_content_lines = []
    for rule in filtered_whitelist:
        if not (rule.startswith('[') and rule.endswith(']')):
            whitelist_content_lines.append(rule)
    
    # 处理白名单规则，确保它们遵循 AdGuardHome 格式
    formatted_whitelist_content_lines = []
    for line in whitelist_content_lines:
        line = line.strip()
        # 跳过空行
        if not line:
            continue
        # 格式化白名单规则
        formatted_rule = format_whitelist_rule(line)
        formatted_whitelist_content_lines.append(formatted_rule)

    # 先过滤白名单内容（去除空行、特殊字符和路径分隔符）-----------------------------------
    filtered_whitelist_lines = []
    for line in formatted_whitelist_content_lines:
        if str(line).strip() and not (
            "!" in line or                    # 包含特殊字符
            "/" in line or                    # 包含/
            line.startswith((".", "-"))       # 特定开头
        ):
            filtered_whitelist_lines.append(line)

    # 统一白名单格式：若不是 @@|| 开头，则移除行内的 @ 与 |，并前置 @@||
    normalized_whitelist_lines = []
    for line in filtered_whitelist_lines:
        s = str(line).strip()
        if s.startswith('@@||'):
            normalized_whitelist_lines.append(s)
        else:
            sanitized = re.sub(r'[@|]', '', s)
            normalized_whitelist_lines.append('@@||' + sanitized)

    # 根据最终将写入的有效规则行数进行统计，确保与文件一致
    blacklist_count = sum(1 for l in processed_blacklist if str(l).strip())
    whitelist_count = len(normalized_whitelist_lines)  # 使用规范化后的白名单数量
    total_count = blacklist_count + whitelist_count
    
    # 合并黑名单和格式化后的白名单到 Black.txt
    with open(COMBINED_FILE, "w", encoding="utf-8-sig") as f:
        # 写入新的文件头部信息
        f.write(f"# 更新时间: {current_time}\n")
        f.write(f"# 总规则数：{total_count} (黑名单: {blacklist_count}, 白名单: {whitelist_count})\n")
        f.write(f"# 作者名称: Menghuibanxian  酷安名: 梦半仙\n")
        f.write(f"# 作者主页: https://github.com/Menghuibanxian/AdguardHome\n")
        f.write("\n")
        
        # 写入处理后的黑名单内容
        for line in processed_blacklist:
            if str(line).strip():
                f.write(f"{line}\n")
        
        # 写入规范化后的白名单内容到Black.txt
        for line in normalized_whitelist_lines:
            f.write(f"{line}\n")

    # 如果需要生成单独的White.txt文件
    if generate_white_file:
        # 单独生成White.txt文件
        with open(WHITE_FILE, "w", encoding="utf-8-sig") as f:
            # 写入白名单文件头部信息（使用过滤后的实际规则数量）
            f.write(f"# 更新时间: {current_time}\n")
            f.write(f"# 白名单规则数：{len(normalized_whitelist_lines)}\n")  # 使用规范化后的实际数量
            f.write(f"# 作者名称: Menghuibanxian  酷安名: 梦半仙\n")
            f.write(f"# 作者主页: https://github.com/Menghuibanxian/AdguardHome\n")
            f.write("\n")
            
            # 写入规范化后的白名单内容到White.txt
            for line in normalized_whitelist_lines:
                f.write(f"{line}\n")
        
        print("AdGuardHome规则处理完成！Black.txt和White.txt文件已生成。")
    else:
        # 如果不需要生成White.txt文件，删除已存在的文件
        if os.path.exists(WHITE_FILE):
            os.remove(WHITE_FILE)
        print("AdGuardHome规则处理完成！Black.txt文件已生成。")

if __name__ == "__main__":
    import sys
    # 解析参数：是否生成 White.txt，以及统一时间戳
    generate_white_file = "--no-white-file" not in sys.argv
    override_time = None
    if "--timestamp" in sys.argv:
        try:
            idx = sys.argv.index("--timestamp")
            override_time = sys.argv[idx+1]
        except Exception:
            pass
    main(generate_white_file, override_time)
