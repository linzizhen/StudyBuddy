/**
 * 学习计划页面模块
 */

class PlansPage {
    constructor() {
        this.container = null;
        this.plans = [];
        window.plansPageInstance = this;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-plans');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-plans');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadData() {
        try {
            const res = await fetch('/api/plans').then(r => r.json());
            this.plans = [
                ...(res.active_plans || []),
                ...(res.completed_plans || [])
            ];
            this.expiringCount = res.stats?.expiring_count || 0;
            this.render();
        } catch (e) {
            console.error('加载计划失败:', e);
            this.renderEmpty();
        }
    }

    render() {
        const totalEl = document.getElementById('plans-total');
        const expiringEl = document.getElementById('plans-expiring');
        const listEl = document.getElementById('plans-list');

        if (totalEl) totalEl.textContent = this.plans.length;
        if (expiringEl) expiringEl.textContent = this.expiringCount;

        if (!listEl) return;

        if (this.plans.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <p>暂无学习计划，点击右上角创建</p>
                </div>
            `;
            return;
        }

        listEl.innerHTML = this.plans.map(plan => {
            let daysRemaining = null;
            if (plan.days_remaining !== undefined) {
                daysRemaining = plan.days_remaining;
            } else if (plan.exam_date) {
                daysRemaining = Math.ceil((new Date(plan.exam_date) - new Date()) / (1000 * 60 * 60 * 24));
            }

            const isExpiring = daysRemaining !== null && daysRemaining > 0 && daysRemaining <= 7;
            const status = plan.completed ? '已完成' : (daysRemaining !== null && daysRemaining <= 0 ? '已到期' : (isExpiring ? '即将到期' : '进行中'));
            const statusClass = plan.completed ? 'completed' : (isExpiring ? 'expiring' : 'active');

            return `
                <div class="plan-item ${isExpiring ? 'expiring' : ''}">
                    <div class="plan-item-header">
                        <div class="plan-title">${this.escapeHtml(plan.subject)}</div>
                        <span class="plan-status ${statusClass}">${status}</span>
                    </div>
                    <div class="plan-meta">
                        <div class="plan-meta-item">
                            <span>⏰</span>
                            <span>${plan.daily_hours || 8} 小时/天</span>
                        </div>
                        ${daysRemaining !== null ? `
                        <div class="plan-meta-item">
                            <span>⏳</span>
                            <span>${daysRemaining > 0 ? '剩余 ' + daysRemaining + ' 天' : '已到期'}</span>
                        </div>
                        ` : ''}
                    </div>
                    ${plan.tasks && plan.tasks.length > 0 ? `
                    <div class="plan-progress mt-3">
                        <div class="text-xs text-muted mb-1">计划任务 (${plan.tasks.length})</div>
                        <div class="text-sm">${plan.tasks.slice(0, 2).map(t => `• ${this.escapeHtml(typeof t === 'string' ? t : (t.phase || t.task || ''))}`).join('<br>')}</div>
                    </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }

    renderEmpty() {
        const totalEl = document.getElementById('plans-total');
        const expiringEl = document.getElementById('plans-expiring');
        const listEl = document.getElementById('plans-list');

        if (totalEl) totalEl.textContent = '0';
        if (expiringEl) expiringEl.textContent = '0';
        if (listEl) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <p>暂无学习计划，点击右上角创建</p>
                </div>
            `;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    refresh() {
        this.loadData();
    }
}

const plansPage = new PlansPage();
export default plansPage;
window.PlansPage = plansPage;
