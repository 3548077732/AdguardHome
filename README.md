# AdguardHome
我很懒如果你愿意帮我那我乐此不疲喵

本仓库每十分时准时自动执行

黑名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/Black.txt

白名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/White.txt

精简黑名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/pure%20black.txt


## 项目结构

```
仓库根目录/
├── .github/
│   └── workflows/
│       └── adguard-rules.yml              # GitHub Actions工作流配置（合并→聚合→简化）
│
├── scripts/
│   ├── adguard_rules_merger.py            # 下载/清洗/合并黑白名单，输出 Black.txt & White.txt
│   ├── aggregate_domains.py               # 聚合 logs 中 querylog*.json，更新 domain name.txt
│   └── adguard_rules_simplifier.py        # 基于本地 Black.txt 生成纯黑名单 pure black.txt
│       └──logs/
│          ├── domain name.txt             # 域名累计统计（聚合脚本维护）
│          ├── log                         # 最近处理的域名与时间戳标记
│          └── querylog*.json              # 临时日志（聚合后删除，提交包含删除）
│
├── Black.txt                              # 合并后的总规则（黑名单+格式化白名单）
├── White.txt                              # 独立白名单规则
└── pure black.txt                         # 合并后的总规则（纯黑名单＋白名单）
```





