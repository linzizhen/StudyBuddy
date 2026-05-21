/**
 * 记忆页面模块
 */

class MemoryPage {
    constructor() {
        this.container = null;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-memory');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-memory');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadData() {
        try {
            const res = await fetch('/api/buddy/memory').then(r => r.json());
            if (res.success) {
                this.render(res);
            }
        } catch (e) {
            console.error('加载记忆失败', e);
        }
    }

    render(data) {
        const statsEl = document.getElementById('memory-stats');
        if (statsEl) {
            statsEl.textContent = `记录了 ${data.stats?.scenes || 0} 个场景，${data.stats?.conversations || 0} 次对话`;
        }

        const container = document.getElementById('recent-scenes');
        if (!container) return;

        const scenes = data.recent_scenes || [];
        if (scenes.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🧠</div>
                    <p>还没有记忆记录，和小豆多聊聊吧~</p>
                </div>
            `;
            return;
        }

        container.innerHTML = scenes.map(scene => `
            <div class="memory-card" onclick="App.openChatWith('${scene.summary?.substring(0, 20) || ''}')">
                <span class="memory-type ${scene.type || 'conversation'}">${scene.type || 'conversation'}</span>
                <div class="text-xs text-muted mb-2">${scene.date}</div>
                <div class="text-sm">${scene.summary}</div>
                ${scene.details ? `<div class="text-xs text-muted mt-2">${scene.details.substring(0, 60)}...</div>` : ''}
            </div>
        `).join('');
    }

    refresh() {
        this.loadData();
    }
}

const memoryPage = new MemoryPage();
export default memoryPage;
window.MemoryPage = memoryPage;
