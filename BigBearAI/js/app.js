document.addEventListener('DOMContentLoaded', () => {
    injectSidebar();
    highlightActiveMenu();
});

function injectSidebar() {
    const appContainer = document.querySelector('.app-container');
    if (!appContainer) return;

    const sidebarHTML = `
        <aside class="sidebar">
            <div class="logo-area">
                <i class="ph-fill ph-robot logo-icon"></i>
                <span>大熊AI</span>
            </div>
            <nav class="nav-menu">
                <a href="index.html" class="nav-item" data-page="index">
                    <i class="ph ph-house"></i>
                    <span>Home</span>
                </a>
                <a href="rules.html" class="nav-item" data-page="rules">
                    <i class="ph ph-scroll"></i>
                    <span>Rules</span>
                </a>
                <a href="agents.html" class="nav-item" data-page="agents">
                    <i class="ph ph-robot"></i>
                    <span>智能体</span>
                </a>
                <a href="prompt.html" class="nav-item" data-page="prompt">
                    <i class="ph ph-magic-wand"></i>
                    <span>Prompt</span>
                </a>
                <a href="mcp.html" class="nav-item" data-page="mcp">
                    <i class="ph ph-plugs-connected"></i>
                    <span>MCP</span>
                </a>
                <a href="knowledge.html" class="nav-item" data-page="knowledge">
                    <i class="ph ph-books"></i>
                    <span>知识库</span>
                </a>
                <a href="plugins.html" class="nav-item" data-page="plugins">
                    <i class="ph ph-puzzle-piece"></i>
                    <span>插件</span>
                </a>
            </nav>
        </aside>
    `;

    // Insert sidebar at the beginning of the container
    appContainer.insertAdjacentHTML('afterbegin', sidebarHTML);
}

function highlightActiveMenu() {
    const path = window.location.pathname;
    const page = path.split("/").pop().replace(".html", "") || "index";

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.dataset.page === page) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}
