# AdguardHome
我很懒如果你愿意帮我那我乐此不疲

规则集:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Black.txt(推荐仅用规则内的白名单)





一个更激进的分支:
https://github.com/Menghuibanxian/AdguardHome_all

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
