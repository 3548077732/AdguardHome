# AdguardHome
我很懒如果你愿意帮我那我乐此不疲喵

黑名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Black.txt


白名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/White.txt

精简黑名单:



## 项目结构

```
仓库根目录/
├── .github/
│   └── workflows/
│       └── auto-commit.yml        # GitHub Actions工作流配置
├── scripts/
│   └── adguard_rules_merger.py   # 规则更新脚本(规则脚本的位置)
├── Black.txt                      # 黑名单的规则(内含白名单规则)
└── White.txt                      # 白名单的规则(仅仅白名单规则)
```
