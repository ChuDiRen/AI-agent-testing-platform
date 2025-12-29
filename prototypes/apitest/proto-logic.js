/**
 * 原型系统模拟逻辑 v2.0 - 增强交互体验版
 * 使用 localStorage 存储模拟数据
 * 增强：Toast通知、加载状态、确认对话框、动画效果
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

// 增强版消息提示组件
const ProtoUI = {
    // Toast 消息队列
    _toastQueue: [],
    _toastContainer: null,

    // 初始化 Toast 容器
    _initToastContainer() {
        if (this._toastContainer) return;
        this._toastContainer = document.createElement('div');
        this._toastContainer.id = 'proto-toast-container';
        this._toastContainer.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            display: flex; flex-direction: column; gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(this._toastContainer);
    },

    // 增强版 Toast
    toast(message, type = 'success', duration = 3000) {
        this._initToastContainer();
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        const colors = {
            success: { bg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', icon: '#dcfce7' },
            error: { bg: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', icon: '#fee2e2' },
            warning: { bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', icon: '#fef3c7' },
            info: { bg: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', icon: '#dbeafe' }
        };

        const toast = document.createElement('div');
        toast.style.cssText = `
            display: flex; align-items: center; gap: 12px;
            padding: 14px 20px; border-radius: 12px;
            color: white; font-weight: 500; font-size: 14px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transform: translateX(120%); opacity: 0;
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            background: ${colors[type].bg};
            pointer-events: auto;
            max-width: 360px;
        `;
        
        toast.innerHTML = `
            <span style="
                width: 24px; height: 24px; border-radius: 50%;
                background: rgba(255,255,255,0.2);
                display: flex; align-items: center; justify-content: center;
                font-size: 12px; font-weight: bold;
            ">${icons[type]}</span>
            <span style="flex: 1;">${message}</span>
            <span style="cursor: pointer; opacity: 0.7; font-size: 18px;" onclick="this.parentElement.remove()">×</span>
        `;
        
        this._toastContainer.appendChild(toast);
        
        // 动画进入
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        });
        
        // 自动移除
        setTimeout(() => {
            toast.style.transform = 'translateX(120%)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 400);
        }, duration);
    },

    // 确认对话框
    confirm(message, options = {}) {
        return new Promise((resolve) => {
            const {
                title = '确认操作',
                confirmText = '确认',
                cancelText = '取消',
                type = 'warning'
            } = options;

            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed; inset: 0; background: rgba(0,0,0,0.5);
                display: flex; align-items: center; justify-content: center;
                z-index: 10001; opacity: 0; transition: opacity 0.25s;
                backdrop-filter: blur(4px);
            `;

            const icons = {
                warning: '⚠️',
                danger: '🗑️',
                info: 'ℹ️'
            };

            const dialog = document.createElement('div');
            dialog.style.cssText = `
                background: white; border-radius: 16px; padding: 28px;
                max-width: 400px; width: 90%; box-shadow: 0 25px 50px rgba(0,0,0,0.25);
                transform: scale(0.9) translateY(20px); transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            `;
            dialog.innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 48px; margin-bottom: 12px;">${icons[type] || icons.warning}</div>
                    <h3 style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">${title}</h3>
                    <p style="color: #64748b; font-size: 14px; line-height: 1.6;">${message}</p>
                </div>
                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button id="proto-confirm-cancel" style="
                        padding: 12px 24px; border-radius: 10px; font-weight: 600;
                        background: #f1f5f9; border: none; color: #475569;
                        cursor: pointer; font-size: 14px; transition: all 0.2s;
                    ">${cancelText}</button>
                    <button id="proto-confirm-ok" style="
                        padding: 12px 24px; border-radius: 10px; font-weight: 600;
                        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                        border: none; color: white; cursor: pointer; font-size: 14px;
                        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3); transition: all 0.2s;
                    ">${confirmText}</button>
                </div>
            `;

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            // 动画进入
            requestAnimationFrame(() => {
                overlay.style.opacity = '1';
                dialog.style.transform = 'scale(1) translateY(0)';
            });

            const close = (result) => {
                overlay.style.opacity = '0';
                dialog.style.transform = 'scale(0.9) translateY(20px)';
                setTimeout(() => overlay.remove(), 250);
                resolve(result);
            };

            dialog.querySelector('#proto-confirm-cancel').onclick = () => close(false);
            dialog.querySelector('#proto-confirm-ok').onclick = () => close(true);
            overlay.onclick = (e) => { if (e.target === overlay) close(false); };
        });
    },

    // 加载遮罩
    showLoading(message = '加载中...') {
        let loader = document.getElementById('proto-loading-overlay');
        if (loader) return;

        loader = document.createElement('div');
        loader.id = 'proto-loading-overlay';
        loader.style.cssText = `
            position: fixed; inset: 0; background: rgba(255,255,255,0.9);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 10002; opacity: 0; transition: opacity 0.2s;
            backdrop-filter: blur(4px);
        `;
        loader.innerHTML = `
            <div style="
                width: 48px; height: 48px; border: 3px solid #e2e8f0;
                border-top-color: #4f46e5; border-radius: 50%;
                animation: proto-spin 0.8s linear infinite;
            "></div>
            <p style="margin-top: 16px; color: #64748b; font-size: 14px; font-weight: 500;">${message}</p>
        `;

        // 添加动画样式
        if (!document.getElementById('proto-loading-style')) {
            const style = document.createElement('style');
            style.id = 'proto-loading-style';
            style.textContent = '@keyframes proto-spin { to { transform: rotate(360deg); } }';
            document.head.appendChild(style);
        }

        document.body.appendChild(loader);
        requestAnimationFrame(() => loader.style.opacity = '1');
    },

    hideLoading() {
        const loader = document.getElementById('proto-loading-overlay');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 200);
        }
    },

    // 按钮加载状态
    setButtonLoading(btn, loading, text = '') {
        if (loading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.disabled = true;
            btn.style.opacity = '0.7';
            btn.style.pointerEvents = 'none';
            btn.innerHTML = `
                <span style="
                    width: 16px; height: 16px; border: 2px solid currentColor;
                    border-top-color: transparent; border-radius: 50%;
                    animation: proto-spin 0.8s linear infinite; display: inline-block;
                "></span>
                ${text || '处理中...'}
            `;
        } else {
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
        }
    }
};

// 工具函数：获取 URL 参数
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

/**
 * 自动注入侧边栏布局
 * 仅跳过根入口页面 /apitest/index.html
 */
ProtoUI.initLayout = function () {
    const path = window.location.pathname;
    // 仅跳过根入口页面（已有自己的侧边栏）
    const isRootIndex = path.endsWith('/apitest/index.html') || path.endsWith('/apitest/');
    if (isRootIndex || document.querySelector('.proto-sidebar')) {
        return;
    }

    // 侧边栏 HTML - 增强版设计
    const sidebarHtml = `
        <div class="proto-sidebar">
            <div class="proto-sidebar-brand">
                <div class="brand-logo">⚡</div>
                <span class="brand-text">Antigravity</span>
            </div>
            <nav class="proto-nav">
                <div class="nav-section">
                    <div class="nav-section-title">核心功能</div>
                    <a href="../dashboard/index.html" class="proto-nav-item" id="nav-dashboard">
                        <span class="nav-icon">📊</span>
                        <span class="nav-text">仪表盘</span>
                    </a>
                    <a href="../project/index.html" class="proto-nav-item" id="nav-project">
                        <span class="nav-icon">📁</span>
                        <span class="nav-text">项目管理</span>
                    </a>
                    <a href="../apiinfo/index.html" class="proto-nav-item" id="nav-api">
                        <span class="nav-icon">🔌</span>
                        <span class="nav-text">接口定义</span>
                    </a>
                    <a href="../apiinfocase/index.html" class="proto-nav-item" id="nav-case">
                        <span class="nav-icon">🧪</span>
                        <span class="nav-text">用例编排</span>
                    </a>
                    <a href="../collection/index.html" class="proto-nav-item" id="nav-collection">
                        <span class="nav-icon">📅</span>
                        <span class="nav-text">测试计划</span>
                    </a>
                </div>
                <div class="nav-section">
                    <div class="nav-section-title">工具箱</div>
                    <a href="../keyword/index.html" class="proto-nav-item" id="nav-keyword">
                        <span class="nav-icon">🔑</span>
                        <span class="nav-text">关键字库</span>
                    </a>
                    <a href="../function/index.html" class="proto-nav-item" id="nav-function">
                        <span class="nav-icon">ƒ</span>
                        <span class="nav-text">自定义函数</span>
                    </a>
                    <a href="../apimate/index.html" class="proto-nav-item" id="nav-mate">
                        <span class="nav-icon">📂</span>
                        <span class="nav-text">素材管理</span>
                    </a>
                </div>
                <div class="nav-section">
                    <div class="nav-section-title">系统配置</div>
                    <a href="../message/robot.html" class="proto-nav-item" id="nav-message">
                        <span class="nav-icon">🤖</span>
                        <span class="nav-text">消息管理</span>
                    </a>
                    <a href="../project/db_index.html" class="proto-nav-item" id="nav-db">
                        <span class="nav-icon">🗄️</span>
                        <span class="nav-text">数据库配置</span>
                    </a>
                    <a href="../locust/index.html" class="proto-nav-item" id="nav-locust">
                        <span class="nav-icon">🦗</span>
                        <span class="nav-text">性能测试</span>
                    </a>
                </div>
            </nav>
            <div class="proto-sidebar-footer">
                <div class="version-info">v1.0.0 Prototype</div>
            </div>
        </div>
    `;

    // 注入侧边栏样式 - 增强版
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .proto-sidebar {
            width: 260px;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            color: white;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            display: flex;
            flex-direction: column;
            z-index: 1000;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
        }
        
        .proto-sidebar-brand {
            padding: 24px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .brand-logo {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }
        
        .brand-text {
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        .proto-nav {
            padding: 16px 0;
            flex: 1;
            overflow-y: auto;
        }
        
        .nav-section {
            margin-bottom: 8px;
        }
        
        .nav-section-title {
            padding: 12px 24px 8px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #64748b;
            font-weight: 600;
        }
        
        .proto-nav-item {
            padding: 12px 24px;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            margin: 2px 8px 2px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .proto-nav-item:hover {
            background: rgba(255, 255, 255, 0.06);
            color: white;
            transform: translateX(4px);
        }
        
        .proto-nav-item.active {
            background: linear-gradient(90deg, rgba(79, 70, 229, 0.2) 0%, transparent 100%);
            color: white;
            border-left-color: #6366f1;
        }
        
        .proto-nav-item.active .nav-icon {
            transform: scale(1.1);
        }
        
        .nav-icon {
            font-size: 18px;
            width: 24px;
            text-align: center;
            transition: transform 0.2s;
        }
        
        .nav-text {
            flex: 1;
        }
        
        .proto-sidebar-footer {
            padding: 16px 24px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .version-info {
            font-size: 12px;
            color: #64748b;
        }
        
        .proto-main {
            margin-left: 260px;
            min-height: 100vh;
            width: calc(100% - 260px);
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        /* 响应式侧边栏 */
        @media (max-width: 1024px) {
            .proto-sidebar {
                width: 72px;
            }
            .proto-sidebar-brand {
                padding: 20px 16px;
                justify-content: center;
            }
            .brand-text,
            .nav-section-title,
            .nav-text,
            .version-info {
                display: none;
            }
            .proto-nav-item {
                padding: 14px;
                justify-content: center;
                margin: 2px 8px;
                border-radius: 8px;
                border-left: none;
            }
            .proto-nav-item.active {
                background: rgba(79, 70, 229, 0.3);
            }
            .nav-icon {
                font-size: 20px;
            }
            .proto-main {
                margin-left: 72px;
                width: calc(100% - 72px);
            }
        }
        
        @media (max-width: 768px) {
            .proto-sidebar {
                display: none;
            }
            .proto-main {
                margin-left: 0;
                width: 100%;
            }
        }
    `;
    document.head.appendChild(styleEl);

    // 包装现有内容
    const body = document.body;
    const existingContent = Array.from(body.childNodes);
    
    const mainWrapper = document.createElement('div');
    mainWrapper.className = 'proto-main';
    
    body.innerHTML = sidebarHtml;
    body.appendChild(mainWrapper);
    
    existingContent.forEach(node => mainWrapper.appendChild(node));

    // 高亮当前导航
    const navMap = {
        'dashboard': 'nav-dashboard',
        'project': 'nav-project',
        'apiinfo': 'nav-api',
        'apiinfocase': 'nav-case',
        'collection': 'nav-collection',
        'keyword': 'nav-keyword',
        'function': 'nav-function',
        'apimate': 'nav-mate',
        'message': 'nav-message',
        'db_': 'nav-db',
        'locust': 'nav-locust'
    };

    for (const [key, id] of Object.entries(navMap)) {
        if (path.includes(key)) {
            const el = document.getElementById(id);
            if (el) el.classList.add('active');
            break;
        }
    }
};

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', () => {
    ProtoUI.initLayout();
    
    // 添加页面过渡效果
    document.body.style.opacity = '0';
    requestAnimationFrame(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    });
});
