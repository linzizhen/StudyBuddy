/**
 * 成就页面模块
 */

class AchievementsPage {
    constructor() {
        this.container = null;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-achievements');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-achievements');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadData() {
        try {
            const data = await fetch('/api/achievements').then(r => r.json());
            this.render(data);
        } catch (e) {
            console.error('加载成就失败:', e);
        }
    }

    render(data) {
        const { achievements, stats, level } = data;

        // 更新等级信息
        const levelIcon = document.getElementById('level-icon');
        const levelName = document.getElementById('level-name');
        const levelPoints = document.getElementById('level-points');
        const levelProgressText = document.getElementById('level-progress-text');
        const levelProgressBar = document.getElementById('level-progress-bar');

        if (levelIcon) levelIcon.textContent = level?.level?.icon || '🌱';
        if (levelName) levelName.textContent = level?.level?.name || '学习小白';
        if (levelPoints) levelPoints.textContent = `${level?.points || 0} 积分`;
        if (levelProgressText) levelProgressText.textContent = `${Math.round(level?.progress || 0)}%`;
        if (levelProgressBar) levelProgressBar.style.width = `${level?.progress || 0}%`;

        // 更新统计
        const unlockedEl = document.getElementById('achievement-unlocked');
        const lockedEl = document.getElementById('achievement-locked');
        const rateEl = document.getElementById('achievement-rate');

        if (unlockedEl) unlockedEl.textContent = stats?.unlocked_count || 0;
        if (lockedEl) lockedEl.textContent = stats?.locked_count || 0;
        if (rateEl) rateEl.textContent = `${Math.round(stats?.completion_rate || 0)}%`;

        // 渲染成就列表
        const listEl = document.getElementById('achievements-list');
        if (!listEl) return;

        if (!achievements || achievements.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🏆</div>
                    <p>暂无成就数据</p>
                </div>
            `;
            return;
        }

        const unlocked = achievements.filter(a => a.unlocked);
        const locked = achievements.filter(a => !a.unlocked);

        let html = '';

        if (unlocked.length > 0) {
            html += `<h4 class="achievement-category-title mb-3">已解锁 (${unlocked.length})</h4>`;
            html += '<div class="achievement-grid mb-4">';
            unlocked.forEach(a => {
                html += `
                    <div class="achievement-item" title="${a.description || ''}">
                        <div class="achievement-item-icon">${a.icon}</div>
                        <div class="achievement-item-name">${a.name}</div>
                        <div class="achievement-item-points">+${a.reward || 0}</div>
                    </div>
                `;
            });
            html += '</div>';
        }

        if (locked.length > 0) {
            html += `<h4 class="achievement-category-title mb-3">待解锁 (${locked.length})</h4>`;
            html += '<div class="achievement-grid">';
            locked.forEach(a => {
                html += `
                    <div class="achievement-item locked" title="${a.description || ''}">
                        <div class="achievement-item-icon">🔒</div>
                        <div class="achievement-item-name">${a.name}</div>
                        <div class="achievement-item-points">+${a.reward || 0}</div>
                    </div>
                `;
            });
            html += '</div>';
        }

        listEl.innerHTML = html;
    }

    refresh() {
        this.loadData();
    }
}

const achievementsPage = new AchievementsPage();
export default achievementsPage;
window.AchievementsPage = achievementsPage;
