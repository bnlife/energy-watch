# Energy Watch ⚡

全球能源价格追踪器，监控中国、日本、美国、德国的汽油和电价。

## 数据来源

[GlobalPetrolPrices.com](https://www.globalpetrolprices.com/) - 每周更新

## 当前价格

| 国家 | 汽油 (元/升) | 电价 (元/kWh) |
|------|-------------|---------------|
| 🇨🇳 中国 | 8.53 | 0.532 |
| 🇯🇵 日本 | 7.14 | 1.49 |
| 🇺🇸 美国 | 7.66 | 1.37 |
| 🇩🇪 德国 | 10.75 | 2.22 |

*最后更新: 2026-06-24*

## 在线访问

🔗 https://bnlife.github.io/energy-watch/

## 自动更新

GitHub Actions 每周一 09:00 (北京时间) 自动爬取最新数据。

## 项目结构

```
energy-watch/
├── index.html          # 前端页面
├── style.css           # 样式
├── app.js              # 前端逻辑
├── data/
│   ├── oil/            # 汽油价格数据
│   └── electricity/    # 电价数据
├── scripts/
│   └── crawl.py        # 爬虫脚本
└── images/             # 国旗图片
```

## 手动运行

```bash
pip install requests beautifulsoup4
python scripts/crawl.py
```

## 数据格式

```json
{
  "crawl_date": "2026-06-24",
  "source": "globalpetrolprices.com",
  "unit": "CNY/liter",
  "prices": [
    {"country": "中国", "price": 8.53},
    {"country": "日本", "price": 7.14},
    {"country": "美国", "price": 7.66},
    {"country": "德国", "price": 10.75}
  ]
}
```

## License

MIT
