/**
 * 日记页面模块
 */

// constants.js 已通过全局方式加载

class DiaryPage {
    constructor() {
        this.container = null;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-diary');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-diary');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadData() {
        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth() + 1;
        const daysInMonth = new Date(year, month, 0).getDate();

        try {
            const curveRes = await fetch(`/api/diary/emotions?days=${daysInMonth}`).then(r => r.json());
            if (curveRes.success) {
                this.renderEmotionChart(curveRes.curve);
            }
        } catch (e) {}

        try {
            const res = await fetch('/api/diary?limit=30').then(r => r.json());
            if (res.success) {
                this.renderHistory(res.entries);
            }
        } catch (e) {}
    }

    renderEmotionChart(curve) {
        const container = document.getElementById('emotion-chart-section');
        if (!container) return;

        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth();
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月',
                           '七月', '八月', '九月', '十月', '十一月', '十二月'];

        const emojis = ['😭', '😢', '😐', '😊', '😄'];
        const emotionMap = {};
        if (curve && curve.dates) {
            curve.dates.forEach((date, i) => {
                emotionMap[date] = curve.levels[i];
            });
        }

        let calendarHtml = `
            <div class="emotion-chart-card">
                <div class="chart-header">
                    <div class="chart-title">本周情绪曲线</div>
                    <div class="chart-month-nav">
                        <span class="chart-current-month">${year}年 ${monthNames[month]}</span>
                    </div>
                </div>
                <div class="emotion-calendar">
                    <div class="calendar-weekday">日</div>
                    <div class="calendar-weekday">一</div>
                    <div class="calendar-weekday">二</div>
                    <div class="calendar-weekday">三</div>
                    <div class="calendar-weekday">四</div>
                    <div class="calendar-weekday">五</div>
                    <div class="calendar-weekday">六</div>
        `;

        for (let i = 0; i < firstDay; i++) {
            calendarHtml += `<div class="calendar-day empty"><span class="day-number"></span></div>`;
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}/${String(month + 1).padStart(2, '0')}/${String(day).padStart(2, '0')}`;
            const emotionLevel = emotionMap[dateStr];
            const isToday = day === today.getDate();
            const levelClass = emotionLevel ? `level-${emotionLevel}` : '';
            const hasEmotion = emotionLevel ? 'has-emotion' : '';
            const emoji = emotionLevel ? emojis[emotionLevel - 1] : '';

            calendarHtml += `
                <div class="calendar-day ${hasEmotion} ${levelClass} ${isToday ? 'today' : ''}">
                    <span class="day-number">${day}</span>
                    ${emoji ? `<span class="day-emoji">${emoji}</span>` : ''}
                </div>
            `;
        }

        calendarHtml += `
                </div>
                <div class="calendar-legend">
                    <div class="legend-item"><span class="legend-emoji">😭</span> 很差</div>
                    <div class="legend-item"><span class="legend-emoji">😐</span> 一般</div>
                    <div class="legend-item"><span class="legend-emoji">😄</span> 很好</div>
                </div>
                ${curve && curve.analysis ? `<div class="chart-analysis">${curve.analysis}</div>` : '<div class="chart-analysis">还没有情绪记录~</div>'}
            </div>
        `;

        container.innerHTML = calendarHtml;
    }

    renderHistory(entries) {
        const el = document.getElementById('diary-history');
        if (!el) return;

        if (!entries || entries.length === 0) {
            el.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <p>还没有日记，从今天开始记录吧~</p>
                </div>
            `;
            return;
        }

        const getEmoji = (level) => ['😭', '😢', '😐', '😊', '😄'][level - 1] || '📝';
        const getLabel = (level) => ['很难受', '有点丧', '一般', '还好', '很开心'][level - 1] || '一般';

        el.innerHTML = `
            <div class="diary-history-section">
                <div class="diary-history-header">
                    <h3 class="diary-history-title">历史日记</h3>
                    <span class="text-sm text-muted">共 ${entries.length} 篇</span>
                </div>
            </div>
            ${entries.map(entry => `
                <div class="diary-entry level-${entry.emotion_level || 3}">
                    <div class="diary-entry-header">
                        <span class="diary-date">${entry.date}</span>
                        <span class="diary-emotion">
                            <span class="diary-emotion-emoji">${getEmoji(entry.emotion_level)}</span>
                            <span class="diary-emotion-label">${entry.emotion_label || getLabel(entry.emotion_level)}</span>
                        </span>
                    </div>
                    ${entry.biggest_event ? `
                        <div class="diary-content diary-event">
                            <span class="diary-content-label">📌 今日大事</span>
                            ${this.escapeHtml(entry.biggest_event)}
                        </div>
                    ` : ''}
                    ${entry.words_to_buddy ? `
                        <div class="diary-content diary-words">
                            <span class="diary-content-label">💬 对小豆说</span>
                            ${this.escapeHtml(entry.words_to_buddy)}
                        </div>
                    ` : ''}
                    ${entry.study_feeling ? `
                        <div class="diary-feeling-tags">
                            <span class="diary-feeling-tag">${entry.study_feeling}</span>
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        `;
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

const diaryPage = new DiaryPage();
export default diaryPage;
window.DiaryPage = diaryPage;
