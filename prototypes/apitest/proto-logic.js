/**
 * 原型系统模拟逻辑 - 实现伪真实的数据交互
 * 使用 localStorage 存储模拟数据
 */

const ProtoStorage = {
    get(key, defaultValue = []) {
        const data = localStorage.getItem('api_proto_' + key);
        return data ? JSON.parse(data) : defaultValue;
    },
    set(key, value) {
        localStorage.setItem('api_proto_' + key, JSON.stringify(value));
    },
    // 初始化种子数据
    initSeed(key, seedData) {
        if (!localStorage.getItem('api_proto_' + key)) {
            this.set(key, seedData);
        }
    }
};

// 模拟 API 延迟
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms));

const ProtoService = {
    // 通用 CRUD
    list(module) {
        return ProtoStorage.get(module);
    },
    get(module, id) {
        const items = this.list(module);
        return items.find(item => item.id == id);
    },
    save(module, data) {
        const items = this.list(module);
        if (data.id) {
            // 更新
            const index = items.findIndex(item => item.id == data.id);
            if (index !== -1) items[index] = { ...items[index], ...data };
        } else {
            // 新增
            data.id = Date.now();
            items.push(data);
        }
        ProtoStorage.set(module, items);
        return data;
    },
    delete(module, id) {
        const items = this.list(module);
        const filtered = items.filter(item => item.id != id);
        ProtoStorage.set(module, filtered);
    }
};

// 消息提示组件
const ProtoUI = {
    toast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed; top: 20px; right: 20px; 
            padding: 12px 24px; border-radius: 8px; 
            color: white; font-weight: 500; z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: 0.3s; transform: translateY(-20px); opacity: 0;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
        `;
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        }, 10);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};

// 工具函数：获取 URL 参数
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

/**
 * UX Upgrade: Initialize Global Layout
 * Injects Sidebar and wraps existing content in .proto-main
 */
ProtoUI.initLayout = function () {
    // 1. Check if layout already initialized
    if (document.querySelector('.proto-sidebar')) return;

    // 2. Define Sidebar HTML
    const sidebarHtml = `
        <div class="proto-sidebar">
            <div class="proto-sidebar-brand">
                <span>⚡ Antigravity</span>
            </div>
            <nav class="proto-nav">
                <a href="../dashboard/index.html" class="proto-nav-item" id="nav-dashboard">📊 仪表盘</a>
                <a href="../project/index.html" class="proto-nav-item" id="nav-project">📝 项目管理</a>
                <a href="../apiinfo/index.html" class="proto-nav-item" id="nav-api">🔌 接口定义</a>
                <a href="../apiinfocase/index.html" class="proto-nav-item" id="nav-case">🧪 用例编排</a>
                <a href="../collection/index.html" class="proto-nav-item" id="nav-collection">📅 测试计划</a>
                <a href="../keyword/index.html" class="proto-nav-item" id="nav-keyword">🔑 关键字库</a>
                <a href="../function/index.html" class="proto-nav-item" id="nav-function">ƒ  自定义函数</a>
                <a href="../apimate/index.html" class="proto-nav-item" id="nav-mate">📂 素材管理</a>
                <a href="../project/db_index.html" class="proto-nav-item" id="nav-db">🗄️ 数据库配置</a>
                <a href="../locust/index.html" class="proto-nav-item" id="nav-locust">🦗 性能测试</a>
            </nav>
            <div style="padding: 24px; font-size: 12px; color: #64748b; border-top: 1px solid #334155;">
                v1.0.0 Prototypes
            </div>
        </div>
    `;

    // 3. Move existing content to .proto-main
    const body = document.body;
    const existingContent = Array.from(body.childNodes);

    // Create Main Wrapper
    const mainWrapper = document.createElement('div');
    mainWrapper.className = 'proto-main';

    // Clear body and append Sidebar + Main
    body.innerHTML = sidebarHtml;
    body.appendChild(mainWrapper);

    // Re-append existing content to Main
    existingContent.forEach(node => mainWrapper.appendChild(node));

    // 4. Highlight Active Link
    const path = window.location.pathname;
    const navs = {
        'dashboard': 'nav-dashboard',
        'project': 'nav-project',
        'apiinfo': 'nav-api',
        'apiinfocase': 'nav-case',
        'collection': 'nav-collection',
        'keyword': 'nav-keyword',
        'function': 'nav-function',
        'apimate': 'nav-mate',
        'db_': 'nav-db',
        'locust': 'nav-locust'
    };

    for (const [key, id] of Object.entries(navs)) {
        if (path.includes(key)) {
            const el = document.getElementById(id);
            if (el) el.classList.add('active');
            break;
        }
    }
};

// Initialize Layout on Load
window.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure DOM is ready if script is in head (though usually it's at end of body)
    ProtoUI.initLayout();
});
