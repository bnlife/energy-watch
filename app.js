// GitHub raw URL 基础路径
const BASE_URL = 'https://raw.githubusercontent.com/bnlife/energy-watch/gh-pages/data';

// 国家代码映射
const countries = ['china', 'japan', 'usa', 'germany'];

// 状态
let currentTab = 'oil';
let pages = { oil: 1, electricity: 1 };
const pageSize = 10;
let cachedData = { oil: [], electricity: [] };

// 初始化
async function init() {
    bindEvents();
    await loadData('oil');
    await loadData('electricity');
}

// 绑定事件
function bindEvents() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            document.getElementById('content-oil').classList.toggle('hidden', currentTab !== 'oil');
            document.getElementById('content-electricity').classList.toggle('hidden', currentTab !== 'electricity');
        });
    });
}

// 加载数据
async function loadData(type) {
    try {
        const listUrl = `${BASE_URL}/${type}/list.json`;
        const response = await fetch(listUrl);
        if (!response.ok) throw new Error('Failed to fetch list');
        const fileList = await response.json();

        const allData = [];
        for (const file of fileList) {
            const fileUrl = `${BASE_URL}/${type}/${file}`;
            const resp = await fetch(fileUrl);
            if (resp.ok) {
                const data = await resp.json();
                allData.push(data);
            }
        }

        cachedData[type] = allData;
        renderTable(type);
    } catch (error) {
        console.error(`加载${type}数据失败:`, error);
        document.querySelector(`#table-${type} tbody`).innerHTML =
            '<tr><td colspan="5" style="text-align:center;color:#999;">数据加载失败</td></tr>';
    }
}

// 渲染表格
function renderTable(type) {
    const data = cachedData[type];
    const total = data.length;
    const totalPages = Math.ceil(total / pageSize);
    const start = (pages[type] - 1) * pageSize;
    const end = Math.min(start + pageSize, total);

    const tbody = document.querySelector(`#table-${type} tbody`);
    let html = '';

    for (let i = start; i < end; i++) {
        const item = data[i];
        const prices = item.prices;
        const get = (country) => {
            const p = prices.find(p => p.country === country);
            return p ? p.price : '-';
        };

        html += `
            <tr>
                <td>${item.crawl_date}</td>
                <td>${get('中国')}</td>
                <td>${get('日本')}</td>
                <td>${get('美国')}</td>
                <td>${get('德国')}</td>
            </tr>
        `;
    }

    tbody.innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:#999;">暂无数据</td></tr>';

    // 分页
    const pagination = document.getElementById(`pagination-${type}`);
    let paginationHtml = '';
    for (let i = 1; i <= totalPages; i++) {
        paginationHtml += `<button class="page-btn ${i === pages[type] ? 'active' : ''}" data-type="${type}" data-page="${i}">${i}</button>`;
    }
    pagination.innerHTML = paginationHtml;

    document.querySelectorAll('.page-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            pages[btn.dataset.type] = parseInt(btn.dataset.page);
            renderTable(btn.dataset.type);
        });
    });
}

document.addEventListener('DOMContentLoaded', init);
