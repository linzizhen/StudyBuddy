/**
 * 任务管理页面模块
 */

class TasksPage {
    constructor() {
        this.container = null;
        this.tasks = [];
        window.tasksPageInstance = this;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-tasks');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-tasks');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadData() {
        try {
            const res = await fetch('/api/tasks').then(r => r.json());
            this.tasks = res.tasks || res || [];
            this.render();
        } catch (e) {
            console.error('加载任务失败:', e);
        }
    }

    render() {
        const totalEl = document.getElementById('tasks-total');
        const completedEl = document.getElementById('tasks-completed');
        const listEl = document.getElementById('tasks-list');

        if (totalEl) totalEl.textContent = this.tasks.length;
        if (completedEl) completedEl.textContent = this.tasks.filter(t => t.completed).length;

        if (!listEl) return;

        if (this.tasks.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <p>暂无任务，点击右上角添加</p>
                </div>
            `;
            return;
        }

        const priorityMap = { high: '高', medium: '中', low: '低' };

        listEl.innerHTML = this.tasks.map(task => {
            const priorityClass = task.priority || 'medium';
            const priorityLabel = priorityMap[priorityClass] || '中';

            return `
                <div class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
                    <div class="task-checkbox ${task.completed ? 'checked' : ''}" onclick="App.toggleTask(${task.id}, ${!task.completed})">
                        ${task.completed ? '✓' : ''}
                    </div>
                    <div class="task-content">
                        <div class="task-title">${this.escapeHtml(task.title)}</div>
                        <div class="task-meta">
                            <span class="task-tag ${priorityClass}">${priorityLabel}</span>
                            ${task.subject ? `<span class="task-tag">${this.escapeHtml(task.subject)}</span>` : ''}
                            ${task.deadline ? `<span>📅 ${task.deadline}</span>` : ''}
                        </div>
                    </div>
                    <div class="task-actions">
                        <button class="task-delete" onclick="App.deleteTask(${task.id})" title="删除">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');
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

const tasksPage = new TasksPage();
export default tasksPage;
window.TasksPage = tasksPage;
