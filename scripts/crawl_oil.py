import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# 国家配置
COUNTRIES = {
    '中国': {'name_en': 'China', 'currency': 'CNY'},
    '日本': {'name_en': 'Japan', 'currency': 'JPY'},
    '美国': {'name_en': 'USA', 'currency': 'USD'},
    '德国': {'name_en': 'Germany', 'currency': 'EUR'},
}

# 汇率（美元兑人民币，其他货币通过美元换算）
EXCHANGE_RATES = {
    'CNY': 1.0,
    'USD': 7.25,
    'JPY': 0.048,
    'EUR': 7.85,
}

def get_exchange_rates():
    """尝试从 API 获取实时汇率，失败则使用默认值"""
    try:
        resp = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            rates = data.get('rates', {})
            usd_to_cny = rates.get('CNY', 7.25)
            usd_to_jpy = rates.get('JPY', 138.5)
            usd_to_eur = rates.get('EUR', 0.92)
            return {
                'CNY': 1.0,
                'USD': usd_to_cny,
                'JPY': usd_to_cny / usd_to_jpy,
                'EUR': usd_to_cny * usd_to_eur,
            }
    except Exception as e:
        print(f"获取汇率失败，使用默认值: {e}")
    return EXCHANGE_RATES

def crawl_country(country_name, country_en):
    """爬取单个国家的汽油价格"""
    url = f'https://www.globalpetrolprices.com/{country_en}/gasoline_prices/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 查找包含 "Gasoline prices" 的表格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    text = cells[0].get_text(strip=True)
                    if 'Gasoline' in text or 'gasoline' in text:
                        price_text = cells[1].get_text(strip=True)
                        try:
                            price = float(price_text)
                            return price
                        except ValueError:
                            continue

        # 如果表格找不到，尝试其他解析方式
        text = soup.get_text()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'gasoline_prices' in line.lower() or 'gasoline prices' in line.lower():
                for j in range(i+1, min(i+5, len(lines))):
                    try:
                        price = float(lines[j].strip())
                        if 1 < price < 1000:  # 合理价格范围
                            return price
                    except ValueError:
                        continue
    except Exception as e:
        print(f"爬取{country_name}汽油价格失败: {e}")
    return None

def crawl_all():
    """爬取所有国家汽油价格"""
    rates = get_exchange_rates()
    print(f"当前汇率: {rates}")

    results = []
    for country_name, config in COUNTRIES.items():
        price = crawl_country(country_name, config['name_en'])
        if price is not None:
            # 转换为人民币
            cny_price = round(price * rates[config['currency']], 2)
            results.append({
                'country': country_name,
                'price': cny_price,
                'original_price': price,
                'currency': config['currency'],
            })
            print(f"{country_name}: {price} {config['currency']} -> {cny_price} CNY")
        else:
            print(f"{country_name}: 获取失败")
            results.append({
                'country': country_name,
                'price': None,
                'original_price': None,
                'currency': config['currency'],
            })

    # 构建数据文件
    today = datetime.now().strftime('%Y-%m-%d')
    data = {
        'crawl_date': today,
        'source': 'globalpetrolprices.com',
        'unit': 'CNY/liter',
        'prices': results,
    }

    # 保存数据文件
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'oil')
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, f'{today}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {filepath}")

    # 更新 list.json
    update_list(data_dir)

    return data

def update_list(data_dir):
    """更新 list.json 文件"""
    list_file = os.path.join(data_dir, 'list.json')
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json') and f != 'list.json'])
    with open(list_file, 'w', encoding='utf-8') as f:
        json.dump(files, f, ensure_ascii=False)
    print(f"列表已更新: {list_file}")

if __name__ == '__main__':
    crawl_all()
