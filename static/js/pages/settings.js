/**
 * 设置页面模块
 */

class SettingsPage {
    constructor() {
        this.container = null;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-settings');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadAchievementStats();
    }

    unmount() {
        const pageEl = document.getElementById('page-settings');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadAchievementStats() {
        try {
            const data = await fetch('/api/achievements').then(r => r.json());
            const statsEl = document.getElementById('achievement-stats');
            if (statsEl && data.stats) {
                const total = (data.stats.unlocked_count || 0) + (data.stats.locked_count || 0);
                statsEl.textContent = `已解锁 ${data.stats.unlocked_count || 0}/${total} 个成就`;
            }
        } catch (e) {}
    }

    refresh() {
        this.loadAchievementStats();
    }
}

const settingsPage = new SettingsPage();
export default settingsPage;
window.SettingsPage = settingsPage;
