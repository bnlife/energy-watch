import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# 国家配置（货币符号）
COUNTRIES = {
    '中国': {'en': 'China', 'currency': 'CNY'},
    '日本': {'en': 'Japan', 'currency': 'JPY'},
    '美国': {'en': 'USA', 'currency': 'USD'},
    '德国': {'en': 'Germany', 'currency': 'EUR'},
}

def get_exchange_rates():
    """获取汇率（基于美元）"""
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
                'EUR': usd_to_cny / usd_to_eur,
            }
    except Exception as e:
        print(f"获取汇率失败，使用默认值: {e}")
    # 默认汇率
    return {
        'CNY': 1.0,
        'USD': 7.25,
        'JPY': 0.052,
        'EUR': 7.85,
    }

def crawl_country(country_name, config):
    """爬取单个国家的汽油和电价"""
    url = f'https://www.globalpetrolprices.com/{config["en"]}/gasoline-prices/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 获取页面文本
        text = soup.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        oil_price = None
        oil_date = None
        elec_price = None
        elec_date = None
        
        # 标记是否在电价区域
        in_electricity_section = False
        
        for i, line in enumerate(lines):
            # 查找汽油价格
            if 'Gasoline prices' in line and i + 2 < len(lines):
                date_str = lines[i + 1]
                price_str = lines[i + 2]
                try:
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        oil_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    oil_price = float(price_str)
                except (ValueError, IndexError):
                    pass
            
            # 查找电价区域
            if 'Electricity prices per kWh' in line:
                in_electricity_section = True
            
            # 查找天然气区域（退出电价区域）
            if 'Natural gas prices per kWh' in line:
                in_electricity_section = False
            
            # 在电价区域内查找家庭用户价格
            if in_electricity_section and 'Households' in line and i + 2 < len(lines):
                date_str = lines[i + 1]
                price_str = lines[i + 2]
                try:
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        elec_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    elec_price = float(price_str)
                except (ValueError, IndexError):
                    pass
        
        return {
            'oil_price': oil_price,
            'oil_date': oil_date,
            'elec_price': elec_price,
            'elec_date': elec_date,
        }
    except Exception as e:
        print(f"爬取{country_name}失败: {e}")
        return None

def crawl_all():
    """爬取所有国家"""
    # 获取汇率
    rates = get_exchange_rates()
    print(f"当前汇率: {rates}")
    
    results_oil = []
    results_elec = []
    
    for country_name, config in COUNTRIES.items():
        print(f"\n正在爬取 {country_name}...")
        data = crawl_country(country_name, config)
        
        if data:
            currency = config['currency']
            rate = rates[currency]
            
            if data['oil_price'] is not None:
                cny_price = round(data['oil_price'] * rate, 2)
                results_oil.append({
                    'country': country_name,
                    'price': cny_price,
                    'original_price': data['oil_price'],
                    'currency': currency,
                    'date': data['oil_date'],
                })
                print(f"  汽油: {data['oil_price']} {currency} -> {cny_price} CNY/L ({data['oil_date']})")
            else:
                print(f"  汽油: 获取失败")
            
            if data['elec_price'] is not None:
                cny_price = round(data['elec_price'] * rate, 3)
                results_elec.append({
                    'country': country_name,
                    'price': cny_price,
                    'original_price': data['elec_price'],
                    'currency': currency,
                    'date': data['elec_date'],
                })
                print(f"  电价: {data['elec_price']} {currency} -> {cny_price} CNY/kWh ({data['elec_date']})")
            else:
                print(f"  电价: 获取失败")
        else:
            print(f"  全部获取失败")
    
    # 保存汽油数据
    if results_oil:
        today = datetime.now().strftime('%Y-%m-%d')
        oil_data = {
            'crawl_date': today,
            'source': 'globalpetrolprices.com',
            'unit': 'CNY/liter',
            'prices': results_oil,
        }
        
        oil_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'oil')
        os.makedirs(oil_dir, exist_ok=True)
        filepath = os.path.join(oil_dir, f'{today}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(oil_data, f, ensure_ascii=False, indent=2)
        print(f"\n汽油数据已保存: {filepath}")
        
        update_list(oil_dir)
    
    # 保存电价数据
    if results_elec:
        today = datetime.now().strftime('%Y-%m-%d')
        elec_data = {
            'crawl_date': today,
            'source': 'globalpetrolprices.com',
            'unit': 'CNY/kWh',
            'prices': results_elec,
        }
        
        elec_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'electricity')
        os.makedirs(elec_dir, exist_ok=True)
        filepath = os.path.join(elec_dir, f'{today}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(elec_data, f, ensure_ascii=False, indent=2)
        print(f"电价数据已保存: {filepath}")
        
        update_list(elec_dir)

def update_list(data_dir):
    """更新 list.json 文件"""
    list_file = os.path.join(data_dir, 'list.json')
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json') and f != 'list.json'])
    with open(list_file, 'w', encoding='utf-8') as f:
        json.dump(files, f, ensure_ascii=False)
    print(f"列表已更新: {list_file}")

if __name__ == '__main__':
    crawl_all()
