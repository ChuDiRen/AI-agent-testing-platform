// 通用卡片模板 - 参考Rules规则市场样式
function createUnifiedCard(item, options = {}) {
    const {
        badgeText = item.tags ? item.tags[0] : (item.type || ''),
        showIcon = false,
        iconName = item.icon || 'star',
        showStatus = false,
        statusText = item.status || '',
        extraBadges = []
    } = options;

    // 装饰性图案（右上角）
    const decorations = [
        `<div style="position:absolute;right:12px;top:12px;opacity:0.6;font-size:2rem;color:${item.textColor}40;"><i class="ph-fill ph-${iconName}"></i></div>`,
        `<div style="position:absolute;right:8px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:4px;opacity:0.5;">
            <div style="width:8px;height:8px;border-radius:50%;background:${item.textColor}60;"></div>
            <div style="width:6px;height:6px;border-radius:50%;background:${item.textColor}40;"></div>
            <div style="width:4px;height:4px;border-radius:50%;background:${item.textColor}30;"></div>
        </div>`
    ];
    const decoration = decorations[Math.floor(Math.random() * decorations.length)];

    // 状态标签（如MCP的Connected/Disconnected）
    const statusHtml = showStatus ? `
        <span class="mcp-status ${statusText.toLowerCase()}" style="margin-left:auto;font-size:0.7rem;">
            <span class="status-dot"></span>
            ${statusText}
        </span>
    ` : '';

    // 额外标签
    const extraBadgesHtml = extraBadges.map(tag =>
        `<span class="badge" style="background-color:${item.color};color:${item.textColor};margin-left:4px;font-size:0.7rem;">${tag}</span>`
    ).join('');

    return `
        <div class="card unified-card" style="background:linear-gradient(145deg, ${item.color}50 0%, ${item.color}20 50%, white 100%);min-height:180px;position:relative;overflow:hidden;">
            ${decoration}
            <div class="card-header" style="position:relative;z-index:1;">
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                    <span class="badge" style="background-color:${item.color};color:${item.textColor};padding:3px 10px;border-radius:4px;font-size:0.75rem;font-weight:500;">
                        ${badgeText}
                    </span>
                    ${extraBadgesHtml}
                </div>
                ${statusHtml}
            </div>
            <h3 class="card-title" style="position:relative;z-index:1;margin-top:12px;font-size:1rem;font-weight:600;">${item.title}</h3>
            <p class="card-desc" style="position:relative;z-index:1;font-size:0.85rem;color:#666;line-height:1.5;margin-top:8px;flex:1;">${item.desc}</p>
            <div class="card-footer" style="position:relative;z-index:1;margin-top:auto;padding-top:12px;">
                <div class="author-info">
                    <div class="avatar-sm" style="background-color:${item.textColor};width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:0.65rem;font-weight:bold;">${item.author[0]}</div>
                    <span style="font-size:0.8rem;color:#888;">${item.author} · ${item.date}</span>
                </div>
            </div>
        </div>
    `;
}

function renderRules() {
    const officialGrid = document.getElementById('rules-grid-official');
    const allGrid = document.getElementById('rules-grid-all');

    if (!officialGrid && !allGrid) return;

    // Render Official Rules
    const officialRules = MockData.rules.filter(r => r.tags.includes('官方'));
    if (officialGrid) {
        officialGrid.innerHTML = officialRules.map(rule =>
            createUnifiedCard(rule, { showIcon: true, iconName: 'scroll' })
        ).join('');
    }

    // Render All Rules
    if (allGrid) {
        allGrid.innerHTML = MockData.rules.map(rule =>
            createUnifiedCard(rule, {
                showIcon: true,
                iconName: 'scroll',
                extraBadges: rule.tags.slice(1)
            })
        ).join('');
    }
}

function renderKnowledge() {
    const grid = document.getElementById('knowledge-grid');
    if (!grid) return;

    grid.innerHTML = MockData.knowledge.map(item =>
        createUnifiedCard(item, {
            badgeText: '文档',
            showIcon: true,
            iconName: item.icon
        })
    ).join('');
}

function renderPlugins() {
    const grid = document.getElementById('plugins-grid');
    if (!grid) return;

    grid.innerHTML = MockData.plugins.map(item =>
        createUnifiedCard(item, {
            badgeText: item.type,
            showIcon: true,
            iconName: item.icon
        })
    ).join('');
}

function renderAgents() {
    const grid = document.getElementById('agents-grid');
    if (!grid) return;

    grid.innerHTML = MockData.agents.map(item =>
        createUnifiedCard(item, {
            badgeText: item.type,
            showIcon: true,
            iconName: item.icon
        })
    ).join('');
}

function renderMCP() {
    const grid = document.getElementById('mcp-grid');
    if (!grid) return;

    grid.innerHTML = MockData.mcp.map(item =>
        createUnifiedCard(item, {
            badgeText: 'MCP',
            showIcon: true,
            iconName: item.icon,
            showStatus: true,
            statusText: item.status
        })
    ).join('');
}

function renderPrompts() {
    const grid = document.getElementById('prompts-grid');
    if (!grid) return;

    grid.innerHTML = MockData.prompts.map(item =>
        createUnifiedCard(item, {
            badgeText: item.tags[0],
            showIcon: true,
            iconName: item.icon,
            extraBadges: item.tags.slice(1)
        })
    ).join('');
}
