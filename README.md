# Energy Watch ⚡

全球能源价格追踪器，监控中国、日本、美国、德国的汽油和居民电价。

## 数据来源

[GlobalPetrolPrices.com](https://www.globalpetrolprices.com/) - 每周更新

价格通过实时汇率（open.er-api.com）从当地货币自动换算为人民币：原始价格 ×（USD→CNY汇率 / 当地货币→USD汇率）。

## 自动更新

GitHub Actions 每周一 09:00 (北京时间) 自动爬取最新数据，同时更新 master 和 gh-pages 分支。

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
    {"country": "德国", "price": 13.94}
  ]
}
```

## License

MIT
