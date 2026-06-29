/**
 * StudyPal "我的挑战" 页面模块
 * 支持小学/初中/高中三阶段差异化挑战体系
 */

const GRADE_LABELS_CN = {
    primary: '小学',
    middle: '初中',
    high: '高中',
};

const TIMELINE_ICONS = {
    exam: '📝',
    quiz: '🧪',
    activity: '🎉',
    deadline: '⏰',
    custom: '📌',
};

class ChallengePage {
    constructor() {
        this.data = null;                  // 完整 challenges.json
        this.activeChallenge = null;       // 当前激活的挑战
        this.gradeMode = 'middle';         // 当前学段
        this.iconLibrary = [];             // 图标库
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-challenges');
        if (pageEl) pageEl.classList.add('active');
        this._tryMigrate();
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-challenges');
        if (pageEl) pageEl.classList.remove('active');
    }

    async _tryMigrate() {
        try {
            const res = await API.migrateChallengeData();
            if (res && res.migrated && window.showToast) {
                showToast('已迁移旧版考研目标数据', 'success');
            }
        } catch (e) { /* 静默失败，不影响主流程 */ }
    }

    async loadData() {
        try {
            const [dataRes, iconRes] = await Promise.all([
                API.getChallenges(),
                API.getIconLibrary(),
            ]);
            this.iconLibrary = (iconRes && iconRes.icons) || [];
            if (dataRes && dataRes.success) {
                this.data = dataRes.data || { user_grade_mode: 'middle', challenges: [] };
                this.gradeMode = this.data.user_grade_mode || 'middle';
                this._resolveActiveChallenge();
                this.render();
            }
        } catch (err) {
            if (window.showToast) showToast('加载挑战数据失败', 'error');
        }
    }

    _resolveActiveChallenge() {
        if (!this.data || !this.data.challenges || !this.data.challenges.length) {
            this.activeChallenge = null;
            return;
        }
        const id = this.data.active_challenge_id;
        if (id) {
            this.activeChallenge = this.data.challenges.find(c => c.id === id) || this.data.challenges[0];
        } else {
            this.activeChallenge = this.data.challenges[0];
        }
    }

    // ====================== 主渲染 ======================

    render() {
        if (!this.data || !this.activeChallenge) {
            this.renderEmptyState();
            return;
        }
        this.renderTopBar();
        switch (this.gradeMode) {
            case 'primary': this.renderPrimary(); break;
            case 'middle':  this.renderMiddle();  break;
            case 'high':    this.renderHigh();    break;
            default:        this.renderMiddle();
        }
    }

    renderEmptyState() {
        const mainEl = document.getElementById('challenges-main');
        const sideEl = document.getElementById('challenges-sidebar');
        if (mainEl) {
            mainEl.innerHTML = `
                <div class="challenge-empty">
                    <div class="challenge-empty-icon">🎯</div>
                    <div class="challenge-empty-title">还没有设置学习挑战</div>
                    <div class="challenge-empty-desc">去创建一个吧，让努力看得见</div>
                    <button class="challenge-btn-primary" onclick="ChallengePage.openGradeModal()">+ 新建挑战</button>
                </div>
            `;
        }
        if (sideEl) sideEl.innerHTML = '';
    }

    renderTopBar() {
        const barEl = document.getElementById('challenges-topbar');
        if (!barEl) return;
        const all = this.data.challenges;
        const activeId = this.activeChallenge ? this.activeChallenge.id : '';
        const gradeLabel = GRADE_LABELS_CN[this.activeChallenge ? this.activeChallenge.grade_mode : this.gradeMode] || '初中';
        const options = all.map(c => `
            <option value="${c.id}" ${c.id === activeId ? 'selected' : ''}>${this._escape(c.name)}</option>
        `).join('');

        barEl.innerHTML = `
            <div class="challenge-topbar">
                <select class="challenge-select" id="challenge-switcher" onchange="ChallengePage.switchChallenge(this.value)">
                    ${options}
                </select>
                <span class="challenge-grade-tag">${gradeLabel}</span>
                <div class="challenge-topbar-actions">
                    <button class="challenge-btn-primary" onclick="ChallengePage.openGradeModal()">+ 新建挑战</button>
                    <button class="challenge-btn-ghost" onclick="ChallengePage.openSettingsModal()">⚙ 设置</button>
                </div>
            </div>
        `;
    }

    // ====================== 小学（探险模式） ======================

    renderPrimary() {
        this.renderOverview();
        this.renderSubjects();
        this.renderMilestones();
        this.renderTimeline();
        this.renderParentPanel();
    }

    renderParentPanel() {
        const el = document.getElementById('challenges-parent');
        if (!el) return;
        el.innerHTML = `
            <div class="challenge-card challenge-parent-panel">
                <div class="challenge-card-header">
                    <div class="challenge-card-title">👨‍👩‍👧 家长看板</div>
                    <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.openParentModal()">详情</button>
                </div>
                <div class="challenge-parent-stats">
                    <div class="challenge-parent-stat">
                        <div class="challenge-parent-stat-val" id="parent-stat-hours">2.5</div>
                        <div class="challenge-parent-stat-label">今日学习小时</div>
                    </div>
                    <div class="challenge-parent-stat">
                        <div class="challenge-parent-stat-val" id="parent-stat-levels">3</div>
                        <div class="challenge-parent-stat-label">已完成关卡</div>
                    </div>
                </div>
                <div class="challenge-parent-suggest">💡 今晚陪孩子做 2 道数学题吧！</div>
            </div>
        `;
    }

    // ====================== 初中（成长模式） ======================

    renderMiddle() {
        this.renderOverview();
        this.renderSubjects();
        this.renderMilestones();
        this.renderTimeline();
        this.renderCompanionPanel();
    }

    renderCompanionPanel() {
        const el = document.getElementById('challenges-companion');
        if (!el) return;
        el.innerHTML = `
            <div class="challenge-card challenge-companion-panel">
                <div class="challenge-card-header">
                    <div class="challenge-card-title">👥 学习小组</div>
                    <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.openCompanionModal()">邀请</button>
                </div>
                <div class="challenge-companion-list">
                    <div class="challenge-companion-tip">本周小组累计学习 28 小时，离目标还差 22 小时</div>
                </div>
            </div>
        `;
    }

    // ====================== 高中（冲刺模式） ======================

    renderHigh() {
        this.renderOverview();
        this.renderSubjects();
        this.renderMilestones();
        this.renderTimeline();
        this.renderStudyDistribution();
        this.renderDailyQuote();
    }

    renderStudyDistribution() {
        const el = document.getElementById('challenges-distribution');
        if (!el) return;
        const subjects = (this.activeChallenge && this.activeChallenge.subjects) || [];
        const data = subjects.slice(0, 6).map(s => ({
            name: s.name,
            icon: s.icon,
            minutes: (s.scores_history && s.scores_history.length) ? Math.round(s.current_score * 0.5) : 0,
        }));
        const max = Math.max(1, ...data.map(d => d.minutes));
        el.innerHTML = `
            <div class="challenge-card">
                <div class="challenge-card-header">
                    <div class="challenge-card-title">📊 本周各科学习分布</div>
                </div>
                <div class="challenge-distribution-list">
                    ${data.map(d => `
                        <div class="challenge-distribution-item">
                            <div class="challenge-distribution-icon">${d.icon}</div>
                            <div class="challenge-distribution-name">${this._escape(d.name)}</div>
                            <div class="challenge-distribution-bar-wrap">
                                <div class="challenge-distribution-bar" style="width:${(d.minutes / max * 100).toFixed(0)}%"></div>
                            </div>
                            <div class="challenge-distribution-val">${d.minutes}m</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderDailyQuote() {
        const el = document.getElementById('challenges-quote');
        if (!el) return;
        const quotes = [
            '每一步都在靠近目标。',
            '保持专注，你已经走了很远。',
            '把大目标拆成小任务，每天推进一点点。',
            '状态好时多学一点，状态差时少学一点。',
            '疲惫时允许自己休息，但不要放弃。',
        ];
        const q = quotes[Math.floor(Math.random() * quotes.length)];
        el.innerHTML = `<div class="challenge-daily-quote">🌿 ${q}</div>`;
    }

    // ====================== 通用：挑战总览 ======================

    renderOverview() {
        const el = document.getElementById('challenges-overview');
        if (!el) return;
        const ch = this.activeChallenge;
        if (!ch) { el.innerHTML = ''; return; }

        const subjects = ch.subjects || [];
        const totalScore = subjects.reduce((acc, s) => acc + (s.current_score || 0), 0);
        const totalTarget = subjects.reduce((acc, s) => acc + (s.target_score || 0), 0);
        const totalFull = subjects.reduce((acc, s) => acc + (s.full_score || 0), 0);
        const overallPercent = totalFull > 0 ? Math.round((totalScore / totalFull) * 100) : 0;

        const titleText = this._overviewTitle();
        const daysToDeadline = this._daysUntil(ch.deadline);
        const countdownText = this._countdownText(daysToDeadline);
        const starsCount = this._starsFor(overallPercent);
        const termProgress = this._termProgress();

        el.innerHTML = `
            <div class="challenge-card challenge-overview">
                <div class="challenge-overview-title">${titleText}</div>
                <div class="challenge-overview-body">
                    <div class="challenge-ring-wrap">
                        <svg class="challenge-ring" width="120" height="120" viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="50" fill="none" stroke="#F0F0F0" stroke-width="10"></circle>
                            <circle cx="60" cy="60" r="50" fill="none" stroke="${this._ringColor(overallPercent)}"
                                stroke-width="10" stroke-linecap="round"
                                stroke-dasharray="${2 * Math.PI * 50}"
                                stroke-dashoffset="${2 * Math.PI * 50 * (1 - overallPercent / 100)}"
                                transform="rotate(-90 60 60)"/>
                            <text x="60" y="68" text-anchor="middle" font-size="28" font-weight="700" fill="#1A1A1A">${overallPercent}%</text>
                        </svg>
                    </div>
                    <div class="challenge-overview-info">
                        <div class="challenge-stars" aria-label="整体星级">${starsCount}</div>
                        <div class="challenge-countdown">${countdownText}</div>
                    </div>
                </div>
                ${termProgress ? `
                    <div class="challenge-term-progress">
                        <div class="challenge-term-progress-track">
                            <div class="challenge-term-progress-fill" style="width:${termProgress.percent}%"></div>
                        </div>
                        <div class="challenge-term-progress-text">${termProgress.text}</div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    _overviewTitle() {
        const mode = this.gradeMode;
        if (mode === 'primary') return '🗺️ 今天的探险地图';
        if (mode === 'middle')  return '⚡ 学科能量站';
        return '📊 学习仪表盘';
    }

    _countdownText(days) {
        const mode = this.gradeMode;
        if (mode === 'primary') {
            if (days <= 0) return '今天是探险日，好好表现哦！';
            if (days > 60) return '期末探险还有很久呢，先享受今天的挑战吧！';
            return `还有 ${days} 天，继续加油！`;
        }
        if (days <= 0) return '今天就是目标日，加油！';
        return `距目标还有 ${days} 天`;
    }

    _starsFor(percent) {
        const max = this.gradeMode === 'primary' ? 5 : 10;
        const filled = Math.round((percent / 100) * max);
        let s = '';
        for (let i = 0; i < filled; i++) s += '⭐';
        for (let i = filled; i < max; i++) s += '☆';
        return s;
    }

    _ringColor(percent) {
        if (percent < 40) return '#FAAD14';
        if (percent < 75) return '#6BCB77';
        return '#4D96FF';
    }

    _termProgress() {
        const ch = this.activeChallenge;
        if (!ch || !ch.deadline) return null;
        const start = ch.created_at ? new Date(ch.created_at) : null;
        const end = new Date(ch.deadline);
        const now = new Date();
        if (!start || isNaN(start.getTime()) || isNaN(end.getTime())) return null;
        const totalWeeks = Math.max(1, Math.ceil((end - start) / (7 * 24 * 3600 * 1000)));
        const passedWeeks = Math.max(0, Math.ceil((now - start) / (7 * 24 * 3600 * 1000)));
        const percent = Math.min(100, Math.round((passedWeeks / totalWeeks) * 100));
        return { percent, text: `第 ${passedWeeks} 周 / 共 ${totalWeeks} 周` };
    }

    _daysUntil(dateStr) {
        if (!dateStr) return 999;
        const target = new Date(dateStr);
        const now = new Date();
        return Math.ceil((target - now) / (24 * 3600 * 1000));
    }

    // ====================== 学科列表（纵向） ======================

    renderSubjects() {
        const el = document.getElementById('challenges-subjects');
        if (!el) return;
        const ch = this.activeChallenge;
        const subjects = (ch && ch.subjects) || [];

        if (!subjects.length) {
            el.innerHTML = `
                <div class="challenge-card">
                    <div class="challenge-card-header">
                        <div class="challenge-card-title">📚 学科${this.gradeMode === 'primary' ? '探险' : '能量'}</div>
                        <button class="challenge-btn-primary challenge-btn-sm" onclick="ChallengePage.openSubjectModal()">+ 添加学科</button>
                    </div>
                    <div class="challenge-empty-state-sm">还没有学科，点击右上角添加吧</div>
                </div>
            `;
            return;
        }

        el.innerHTML = `
            <div class="challenge-card">
                <div class="challenge-card-header">
                    <div class="challenge-card-title">📚 学科${this.gradeMode === 'primary' ? '探险' : '能量'}</div>
                    <button class="challenge-btn-primary challenge-btn-sm" onclick="ChallengePage.openSubjectModal()">+ 添加学科</button>
                </div>
                <div class="challenge-subject-list">
                    ${subjects.map(s => this._renderSubjectCard(s)).join('')}
                </div>
            </div>
        `;
    }

    _renderSubjectCard(s) {
        const percent = s.full_score > 0 ? Math.round((s.current_score / s.full_score) * 100) : 0;
        const stars = s.display_mode === 'star'
            ? this._renderStars(s.current_level, s.max_level)
            : '';
        const scoreLine = s.display_mode === 'star'
            ? `<div class="challenge-subject-stars">${stars}</div>`
            : `<div class="challenge-subject-score">${s.current_score || 0} / ${s.full_score || 0}</div>`;
        const trendTag = this._renderTrend(s);
        const suggestion = this._suggestionFor(s);
        const weakPoints = (s.weak_points && s.weak_points.length)
            ? `<div class="challenge-subject-weak">⚠ ${s.weak_points.join('、')}</div>`
            : '';

        return `
            <div class="challenge-subject-card">
                <div class="challenge-subject-head">
                    <div class="challenge-subject-name">
                        <span class="challenge-subject-icon">${s.icon || '📚'}</span>
                        ${this._escape(s.name)}
                    </div>
                    <div class="challenge-subject-actions">
                        <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.openScoreModal('${s.id}')">记录成绩</button>
                        <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.openSubjectHistoryModal('${s.id}')">查看历史</button>
                        <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.openSubjectModal('${s.id}')">编辑</button>
                    </div>
                </div>
                <div class="challenge-subject-progress-row">
                    <div class="challenge-progress-bar">
                        <div class="challenge-progress-fill" style="width:${percent}%; background:${this._ringColor(percent)};"></div>
                    </div>
                    <span class="challenge-subject-percent">${percent}%</span>
                    ${scoreLine}
                </div>
                <div class="challenge-subject-meta">
                    ${trendTag}
                    ${suggestion ? `<div class="challenge-subject-suggestion">💡 ${suggestion}</div>` : ''}
                    ${weakPoints}
                </div>
            </div>
        `;
    }

    _renderStars(level, max) {
        const safeMax = max || 5;
        const safeLevel = level || 0;
        let html = '';
        for (let i = 0; i < safeLevel; i++) html += '🌟';
        for (let i = safeLevel; i < safeMax; i++) html += '🌑';
        return html;
    }

    _renderTrend(s) {
        const hist = s.scores_history || [];
        if (hist.length < 2) return '';
        const last = hist[hist.length - 1].score;
        const prev = hist[hist.length - 2].score;
        if (last > prev) return '<span class="challenge-tag challenge-tag-up">📈 稳步上升</span>';
        if (last < prev) return '<span class="challenge-tag challenge-tag-warn">📉 需关注</span>';
        return '<span class="challenge-tag challenge-tag-neutral">➡ 保持平稳</span>';
    }

    _suggestionFor(s) {
        const tips = [];
        if (s.weak_points && s.weak_points.length) {
            const firstWeak = s.weak_points[0];
            tips.push(`每天额外练习：${firstWeak}`);
        }
        const hist = s.scores_history || [];
        if (hist.length >= 2) {
            const last = hist[hist.length - 1].score;
            const prev = hist[hist.length - 2].score;
            if (last - prev < 0) tips.push('最近退步了，适当调整节奏');
        }
        return tips.join('；');
    }

    // ====================== 成长对比 ======================

    renderMilestones() {
        const el = document.getElementById('challenges-milestones');
        if (!el) return;
        const ch = this.activeChallenge;
        const all = (ch && ch.milestones) || [];
        const visibleList = all.filter(m => m.visible !== false);

        if (!visibleList.length && !all.length) {
            el.innerHTML = `
                <div class="challenge-card">
                    <div class="challenge-card-header">
                        <div class="challenge-card-title">📈 成长对比</div>
                        <button class="challenge-btn-primary challenge-btn-sm" onclick="ChallengePage.openMilestoneModal()">+ 添加对比项</button>
                    </div>
                    <div class="challenge-empty-state-sm">还没有对比项，添加第一个对比项记录进步</div>
                </div>
            `;
            return;
        }

        const showRank = (this.gradeMode === 'middle' || this.gradeMode === 'high');
        const classAvgItem = all.find(m => m.type === 'class_avg');

        el.innerHTML = `
            <div class="challenge-card">
                <div class="challenge-card-header">
                    <div class="challenge-card-title">📈 成长对比</div>
                    <button class="challenge-btn-primary challenge-btn-sm" onclick="ChallengePage.openMilestoneModal()">+ 添加对比项</button>
                </div>
                <div class="challenge-milestone-list">
                    ${visibleList.map(m => `
                        <div class="challenge-milestone-item">
                            <div class="challenge-milestone-name">${this._escape(m.name)}</div>
                            <div class="challenge-milestone-score">${m.value} / ${m.full_score}</div>
                            <div class="challenge-milestone-text">${this._escape(m.comparison_text || '')}</div>
                            <div class="challenge-milestone-actions">
                                <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.toggleMilestone('${m.id}')">隐藏</button>
                                <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.deleteMilestone('${m.id}')">删除</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                ${showRank && classAvgItem ? `
                    <label class="challenge-toggle-row">
                        <input type="checkbox" id="rank-toggle" ${classAvgItem.visible ? 'checked' : ''} onchange="ChallengePage.toggleRankComparison(this.checked)">
                        <span>显示班级排名</span>
                    </label>
                ` : ''}
            </div>
        `;
    }

    // ====================== 时间线 ======================

    renderTimeline() {
        const el = document.getElementById('challenges-timeline');
        if (!el) return;
        const ch = this.activeChallenge;
        const all = (ch && ch.timeline) || [];

        const list = this.gradeMode === 'primary'
            ? all.filter(n => {
                if (!n.date) return false;
                const diff = (new Date(n.date) - new Date()) / (24 * 3600 * 1000);
                return diff >= -1 && diff <= 3;
            })
            : all;

        if (!list.length) {
            el.innerHTML = `
                <div class="challenge-card">
                    <div class="challenge-card-header">
                        <div class="challenge-card-title">🗓️ ${this.gradeMode === 'primary' ? '活动日历' : '学期路线图'}</div>
                        <button class="challenge-btn-primary challenge-btn-sm" onclick="ChallengePage.openTimelineModal()">+ 添加节点</button>
                    </div>
                    <div class="challenge-empty-state-sm">还没有节点，添加一个吧</div>
                </div>
            `;
            return;
        }

        el.innerHTML = `
            <div class="challenge-card">
                <div class="challenge-card-header">
                    <div class="challenge-card-title">🗓️ ${this.gradeMode === 'primary' ? '活动日历' : '学期路线图'}</div>
                    <button class="challenge-btn-primary challenge-btn-sm" onclick="ChallengePage.openTimelineModal()">+ 添加节点</button>
                </div>
                <div class="challenge-timeline">
                    ${this._renderTimelineTrack(all)}
                    <div class="challenge-timeline-list">
                        ${list.map(n => this._renderTimelineNode(n)).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    _renderTimelineTrack(nodes) {
        if (!nodes.length) return '';
        const dates = nodes.filter(n => n.date).map(n => new Date(n.date).getTime());
        if (!dates.length) return '';
        const min = Math.min(...dates);
        const max = Math.max(...dates);
        const now = Date.now();
        let percent = 0;
        if (max > min) {
            percent = Math.min(100, Math.max(0, ((now - min) / (max - min)) * 100));
        }
        return `
            <div class="challenge-timeline-track">
                <div class="challenge-timeline-progress" style="width:${percent}%"></div>
            </div>
        `;
    }

    _renderTimelineNode(n) {
        const date = n.date || '';
        const dateText = date ? this._formatDate(date) : '';
        let urgencyTag = '';
        if (n.urgency === 'high') urgencyTag = '<span class="challenge-tag challenge-tag-danger">🔴 紧急</span>';
        else if (n.urgency === 'medium') urgencyTag = '<span class="challenge-tag challenge-tag-warn">🟡 注意</span>';
        else if (n.urgency === 'low') urgencyTag = '<span class="challenge-tag challenge-tag-up">🟢 宽松</span>';

        const status = n.completed
            ? '<span class="challenge-tag challenge-tag-up">✓ 已完成</span>'
            : (date && new Date(date) < new Date() ? '<span class="challenge-tag challenge-tag-warn">⚠ 已过期</span>' : '');

        const icon = n.icon || TIMELINE_ICONS[n.type] || '📌';

        return `
            <div class="challenge-timeline-node">
                <div class="challenge-timeline-icon">${icon}</div>
                <div class="challenge-timeline-body">
                    <div class="challenge-timeline-name">${this._escape(n.name)}</div>
                    <div class="challenge-timeline-meta">
                        ${dateText}
                        ${status}
                        ${urgencyTag}
                    </div>
                </div>
                <div class="challenge-timeline-actions">
                    <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.toggleTimelineNode('${n.id}')">${n.completed ? '取消' : '完成'}</button>
                    <button class="challenge-btn-ghost challenge-btn-sm" onclick="ChallengePage.deleteTimelineNode('${n.id}')">删除</button>
                </div>
            </div>
        `;
    }

    _formatDate(dateStr) {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return `${d.getMonth() + 1}月${d.getDate()}日`;
    }

    // ====================== 切换挑战/学段 ======================

    async switchChallenge(challengeId) {
        try {
            const res = await API.activateChallenge(challengeId);
            if (res && res.success) {
                await this.loadData();
                if (window.showToast) showToast('已切换挑战', 'success');
            }
        } catch (e) {
            if (window.showToast) showToast('切换失败', 'error');
        }
    }

    // ====================== 弹窗系统 ======================

    openModal(html) {
        this._closeModal();
        const wrap = document.createElement('div');
        wrap.id = 'challenge-modal-overlay';
        wrap.className = 'challenge-modal';
        wrap.innerHTML = `<div class="challenge-modal-content">${html}</div>`;
        wrap.addEventListener('click', (e) => { if (e.target === wrap) this._closeModal(); });
        document.body.appendChild(wrap);
    }

    _closeModal() {
        const old = document.getElementById('challenge-modal-overlay');
        if (old) old.remove();
    }

    openGradeModal() {
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">选择你的学习阶段</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-grade-options">
                <div class="challenge-grade-option" data-grade="primary" onclick="ChallengePage._selectGrade('primary')">
                    <div class="challenge-grade-option-icon">🎒</div>
                    <div class="challenge-grade-option-name">小学</div>
                    <div class="challenge-grade-option-desc">1-6 年级</div>
                </div>
                <div class="challenge-grade-option" data-grade="middle" onclick="ChallengePage._selectGrade('middle')">
                    <div class="challenge-grade-option-icon">📚</div>
                    <div class="challenge-grade-option-name">初中</div>
                    <div class="challenge-grade-option-desc">7-9 年级</div>
                </div>
                <div class="challenge-grade-option" data-grade="high" onclick="ChallengePage._selectGrade('high')">
                    <div class="challenge-grade-option-icon">🎓</div>
                    <div class="challenge-grade-option-name">高中</div>
                    <div class="challenge-grade-option-desc">10-12 年级</div>
                </div>
            </div>
        `;
        this.openModal(html);
    }

    async _selectGrade(grade) {
        try {
            await API.setGradeMode(grade);
            this.gradeMode = grade;
        } catch (e) {}
        this._closeModal();
        this.openNewChallengeModal(grade);
    }

    openNewChallengeModal(preselectedGrade = null) {
        const grade = preselectedGrade || this.gradeMode;
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">新建挑战</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">挑战名称</label>
                <input type="text" class="challenge-input" id="nc-name" placeholder="例如：${GRADE_LABELS_CN[grade]}上学期">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">学习阶段</label>
                <div class="challenge-grade-pills">
                    ${['primary', 'middle', 'high'].map(g => `
                        <button type="button" class="challenge-grade-pill ${g === grade ? 'active' : ''}" data-grade="${g}" onclick="ChallengePage._pickGrade('${g}')">
                            ${GRADE_LABELS_CN[g]}
                        </button>
                    `).join('')}
                </div>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">挑战类型</label>
                <input type="text" class="challenge-input" id="nc-type" value="学期考试" placeholder="学期考试 / 高考冲刺 / ...自定义">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">截止日期</label>
                <input type="date" class="challenge-input" id="nc-deadline">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">描述（可选）</label>
                <textarea class="challenge-input" id="nc-desc" rows="2" placeholder="简短描述目标"></textarea>
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                <button class="challenge-btn-primary" onclick="ChallengePage.submitNewChallenge()">创建挑战</button>
            </div>
        `;
        // 在新弹窗打开前记录所选 grade
        this._modalGrade = grade;
        this.openModal(html);
    }

    _pickGrade(g) {
        this._modalGrade = g;
        document.querySelectorAll('.challenge-grade-pill').forEach(el => {
            el.classList.toggle('active', el.dataset.grade === g);
        });
    }

    async submitNewChallenge() {
        const name = document.getElementById('nc-name').value.trim();
        const grade = this._modalGrade || this.gradeMode;
        const type = document.getElementById('nc-type').value.trim() || '学期考试';
        const deadline = document.getElementById('nc-deadline').value;
        const description = document.getElementById('nc-desc').value.trim();
        if (!name) {
            showToast('请输入挑战名称', 'warn');
            return;
        }
        try {
            const res = await API.createChallenge({
                name, grade_mode: grade, type, deadline, description
            });
            if (res && res.success) {
                showToast('挑战创建成功', 'success');
                this._closeModal();
                await this.loadData();
            } else {
                showToast((res && res.error) || '创建失败', 'error');
            }
        } catch (e) {
            showToast('创建失败', 'error');
        }
    }

    openSettingsModal() {
        if (!this.activeChallenge) return;
        const ch = this.activeChallenge;
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">挑战设置</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">挑战名称</label>
                <input type="text" class="challenge-input" id="set-name" value="${this._escape(ch.name)}">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">挑战类型</label>
                <input type="text" class="challenge-input" id="set-type" value="${this._escape(ch.type || '')}">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">截止日期</label>
                <input type="date" class="challenge-input" id="set-deadline" value="${ch.deadline || ''}">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">描述</label>
                <textarea class="challenge-input" id="set-desc" rows="2">${this._escape(ch.description || '')}</textarea>
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-danger" onclick="ChallengePage.deleteCurrentChallenge()">删除挑战</button>
                <div>
                    <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                    <button class="challenge-btn-primary" onclick="ChallengePage.submitSettings()">保存</button>
                </div>
            </div>
        `;
        this.openModal(html);
    }

    async submitSettings() {
        if (!this.activeChallenge) return;
        const payload = {
            name: document.getElementById('set-name').value.trim(),
            type: document.getElementById('set-type').value.trim(),
            deadline: document.getElementById('set-deadline').value,
            description: document.getElementById('set-desc').value.trim(),
        };
        try {
            const res = await API.updateChallenge(this.activeChallenge.id, payload);
            if (res && res.success) {
                showToast('已保存', 'success');
                this._closeModal();
                await this.loadData();
            }
        } catch (e) {
            showToast('保存失败', 'error');
        }
    }

    async deleteCurrentChallenge() {
        if (!this.activeChallenge) return;
        if (!confirm(`确认删除挑战 "${this.activeChallenge.name}" 吗？`)) return;
        try {
            await API.deleteChallenge(this.activeChallenge.id);
            showToast('已删除', 'success');
            this._closeModal();
            await this.loadData();
        } catch (e) {
            showToast('删除失败', 'error');
        }
    }

    async openSubjectModal(subjectId = null) {
        if (!this.activeChallenge) return;
        const editSub = subjectId ? this.activeChallenge.subjects.find(s => s.id === subjectId) : null;
        let presets = [];
        try {
            const r = await API.getGradePresets(this.gradeMode);
            presets = (r && r.presets) || [];
        } catch (e) {}

        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">${editSub ? '编辑学科' : '添加学科'}</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">学科名称</label>
                <input type="text" class="challenge-input" id="sub-name" list="sub-presets" value="${editSub ? this._escape(editSub.name) : ''}" placeholder="例如：语文">
                <datalist id="sub-presets">
                    ${presets.map(p => `<option value="${this._escape(p.name)}">`).join('')}
                </datalist>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">图标</label>
                <div class="challenge-icon-grid">
                    ${this.iconLibrary.map(icon => `
                        <button type="button" class="challenge-icon-btn ${editSub && editSub.icon === icon ? 'active' : ''}" data-icon="${icon}" onclick="ChallengePage._pickIcon(this)">${icon}</button>
                    `).join('')}
                </div>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">目标分数</label>
                <div class="challenge-form-inline">
                    <input type="number" class="challenge-input" id="sub-target" value="${editSub ? editSub.target_score : 100}" min="1">
                    <span>/</span>
                    <input type="number" class="challenge-input" id="sub-full" value="${editSub ? editSub.full_score : 150}" min="1">
                </div>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">当前分数（可选）</label>
                <input type="number" class="challenge-input" id="sub-current" value="${editSub ? editSub.current_score : 0}" min="0">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">薄弱点（可选，逗号分隔）</label>
                <input type="text" class="challenge-input" id="sub-weak" value="${editSub ? this._escape((editSub.weak_points || []).join('、')) : ''}" placeholder="例如：文言文、作文立意">
            </div>
            <div class="challenge-form-actions">
                ${editSub ? `<button class="challenge-btn-danger" onclick="ChallengePage.deleteSubject('${editSub.id}')">删除</button>` : ''}
                <div>
                    <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                    <button class="challenge-btn-primary" onclick="ChallengePage.submitSubject('${subjectId || ''}')">${editSub ? '保存' : '添加'}</button>
                </div>
            </div>
        `;
        this._pickedIcon = editSub ? editSub.icon : '';
        this.openModal(html);
    }

    _pickIcon(btn) {
        document.querySelectorAll('.challenge-icon-btn').forEach(el => el.classList.remove('active'));
        btn.classList.add('active');
        this._pickedIcon = btn.dataset.icon;
    }

    async submitSubject(subjectId) {
        if (!this.activeChallenge) return;
        const name = document.getElementById('sub-name').value.trim();
        const target = parseInt(document.getElementById('sub-target').value, 10);
        const full = parseInt(document.getElementById('sub-full').value, 10);
        const current = parseInt(document.getElementById('sub-current').value, 10);
        const weakRaw = document.getElementById('sub-weak').value.trim();
        const weak_points = weakRaw ? weakRaw.split(/[、,，]/).map(s => s.trim()).filter(Boolean) : [];
        if (!name) { showToast('请填写学科名称', 'warn'); return; }

        const payload = {
            name,
            icon: this._pickedIcon || '📚',
            target_score: isNaN(target) ? 100 : target,
            full_score: isNaN(full) ? 100 : full,
            current_score: isNaN(current) ? 0 : current,
            display_mode: this.gradeMode === 'high' ? 'score' : 'star',
            max_level: this.gradeMode === 'primary' ? 5 : 10,
            weak_points,
        };
        try {
            if (subjectId) {
                await API.updateSubject(this.activeChallenge.id, subjectId, payload);
            } else {
                await API.addSubject(this.activeChallenge.id, payload);
            }
            showToast('已保存', 'success');
            this._closeModal();
            await this.loadData();
        } catch (e) {
            showToast('保存失败', 'error');
        }
    }

    async deleteSubject(subjectId) {
        if (!this.activeChallenge || !confirm('确认删除此学科？')) return;
        try {
            await API.deleteSubject(this.activeChallenge.id, subjectId);
            showToast('已删除', 'success');
            this._closeModal();
            await this.loadData();
        } catch (e) {
            showToast('删除失败', 'error');
        }
    }

    openScoreModal(subjectId) {
        if (!this.activeChallenge) return;
        const sub = this.activeChallenge.subjects.find(s => s.id === subjectId);
        if (!sub) return;
        const today = new Date().toISOString().slice(0, 10);
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">记录成绩 - ${this._escape(sub.name)}</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">考试日期</label>
                <input type="date" class="challenge-input" id="score-date" value="${today}">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">考试名称（如"期中考试"）</label>
                <input type="text" class="challenge-input" id="score-name" placeholder="例如：第二次月考">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">得分</label>
                <div class="challenge-form-inline">
                    <input type="number" class="challenge-input" id="score-val" min="0" max="${sub.full_score || 150}" placeholder="得分">
                    <span>/ ${sub.full_score || 150}</span>
                </div>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">备注（可选）</label>
                <input type="text" class="challenge-input" id="score-note" placeholder="想说的话">
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                <button class="challenge-btn-primary" onclick="ChallengePage.submitScore('${subjectId}')">保存记录</button>
            </div>
        `;
        this.openModal(html);
    }

    async submitScore(subjectId) {
        if (!this.activeChallenge) return;
        const sub = this.activeChallenge.subjects.find(s => s.id === subjectId);
        if (!sub) return;
        const date = document.getElementById('score-date').value;
        const exam_name = document.getElementById('score-name').value.trim();
        const score = parseInt(document.getElementById('score-val').value, 10);
        const note = document.getElementById('score-note').value.trim();
        if (isNaN(score)) { showToast('请填写分数', 'warn'); return; }
        try {
            await API.addScoreRecord(this.activeChallenge.id, subjectId, { date, score, exam_name, note });
            showToast('记录成功', 'success');
            this._closeModal();
            await this.loadData();
        } catch (e) {
            showToast('记录失败', 'error');
        }
    }

    openMilestoneModal() {
        if (!this.activeChallenge) return;
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">添加对比项</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">对比名称</label>
                <input type="text" class="challenge-input" id="ms-name" placeholder="如：上次月考">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">对比类型</label>
                <select class="challenge-input" id="ms-type">
                    <option value="self_last">自我对比</option>
                    <option value="class_avg">班级平均</option>
                    <option value="admission_line">录取线</option>
                    <option value="custom">自定义</option>
                </select>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">参考分数</label>
                <div class="challenge-form-inline">
                    <input type="number" class="challenge-input" id="ms-val" placeholder="分数">
                    <span>/</span>
                    <input type="number" class="challenge-input" id="ms-full" value="150">
                </div>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">对比文案</label>
                <input type="text" class="challenge-input" id="ms-text" placeholder="例如：比上次进步了 4 分！">
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                <button class="challenge-btn-primary" onclick="ChallengePage.submitMilestone()">添加</button>
            </div>
        `;
        this.openModal(html);
    }

    async submitMilestone() {
        if (!this.activeChallenge) return;
        const payload = {
            name: document.getElementById('ms-name').value.trim(),
            type: document.getElementById('ms-type').value,
            value: parseInt(document.getElementById('ms-val').value, 10),
            full_score: parseInt(document.getElementById('ms-full').value, 10) || 150,
            comparison_text: document.getElementById('ms-text').value.trim(),
            visible: true,
        };
        if (!payload.name || isNaN(payload.value)) { showToast('请填写完整', 'warn'); return; }
        try {
            await API.addMilestone(this.activeChallenge.id, payload);
            showToast('已添加', 'success');
            this._closeModal();
            await this.loadData();
        } catch (e) {
            showToast('添加失败', 'error');
        }
    }

    openTimelineModal() {
        if (!this.activeChallenge) return;
        const today = new Date().toISOString().slice(0, 10);
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">添加节点</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">节点名称</label>
                <input type="text" class="challenge-input" id="tl-name" placeholder="如：期中考试">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">节点类型</label>
                <select class="challenge-input" id="tl-type">
                    <option value="exam">考试</option>
                    <option value="quiz">测验</option>
                    <option value="activity">活动</option>
                    <option value="deadline">截止</option>
                    <option value="custom">自定义</option>
                </select>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">日期</label>
                <input type="date" class="challenge-input" id="tl-date" value="${today}">
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">紧急度</label>
                <select class="challenge-input" id="tl-urgency">
                    <option value="low">低</option>
                    <option value="medium" selected>中</option>
                    <option value="high">高</option>
                </select>
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                <button class="challenge-btn-primary" onclick="ChallengePage.submitTimelineNode()">添加节点</button>
            </div>
        `;
        this.openModal(html);
    }

    async submitTimelineNode() {
        if (!this.activeChallenge) return;
        const type = document.getElementById('tl-type').value;
        const payload = {
            name: document.getElementById('tl-name').value.trim(),
            type,
            date: document.getElementById('tl-date').value,
            urgency: document.getElementById('tl-urgency').value,
            icon: TIMELINE_ICONS[type] || '📌',
            completed: false,
        };
        if (!payload.name || !payload.date) { showToast('请填写完整', 'warn'); return; }
        try {
            await API.addTimelineNode(this.activeChallenge.id, payload);
            showToast('已添加', 'success');
            this._closeModal();
            await this.loadData();
        } catch (e) {
            showToast('添加失败', 'error');
        }
    }

    async toggleTimelineNode(nodeId) {
        if (!this.activeChallenge) return;
        try {
            await API.toggleTimelineNode(this.activeChallenge.id, nodeId);
            await this.loadData();
        } catch (e) {}
    }

    async deleteTimelineNode(nodeId) {
        if (!this.activeChallenge || !confirm('确认删除此节点？')) return;
        try {
            await API.deleteTimelineNode(this.activeChallenge.id, nodeId);
            await this.loadData();
        } catch (e) {}
    }

    async toggleMilestone(msId) {
        if (!this.activeChallenge) return;
        try {
            await API.toggleMilestone(this.activeChallenge.id, msId);
            await this.loadData();
        } catch (e) {}
    }

    async deleteMilestone(msId) {
        if (!this.activeChallenge || !confirm('确认删除？')) return;
        try {
            await API.deleteMilestone(this.activeChallenge.id, msId);
            await this.loadData();
        } catch (e) {}
    }

    async toggleRankComparison(checked) {
        if (!this.activeChallenge) return;
        const rankItem = (this.activeChallenge.milestones || []).find(m => m.type === 'class_avg');
        if (!rankItem) return;
        try {
            await API.toggleMilestone(this.activeChallenge.id, rankItem.id);
            await this.loadData();
        } catch (e) {}
    }

    openSubjectHistoryModal(subjectId) {
        const sub = this.activeChallenge && this.activeChallenge.subjects.find(s => s.id === subjectId);
        if (!sub) return;
        const hist = sub.scores_history || [];
        const rows = hist.map(h => `
            <tr>
                <td>${this._formatDate(h.date)}</td>
                <td>${this._escape(h.exam_name || '')}</td>
                <td>${h.score} / ${h.full_score}</td>
                <td>${Math.round((h.score / h.full_score) * 100)}%</td>
            </tr>
        `).join('') || '<tr><td colspan="4" style="text-align:center;color:#999;">暂无记录</td></tr>';
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">${this._escape(sub.name)} - 历史记录</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <table class="challenge-history-table">
                <thead><tr><th>日期</th><th>考试</th><th>分数</th><th>百分比</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
            <div class="challenge-form-actions">
                <button class="challenge-btn-primary" onclick="ChallengePage._closeModal()">关闭</button>
            </div>
        `;
        this.openModal(html);
    }

    openParentModal() {
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">👨‍👩‍👧 家长看板</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <div class="challenge-modal-info">这里可以看到孩子今天的学习时长、情绪摘要、完成的关卡数量，以及给家长的小建议。</div>
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-primary" onclick="ChallengePage._closeModal()">了解</button>
            </div>
        `;
        this.openModal(html);
    }

    openCompanionModal() {
        const html = `
            <div class="challenge-modal-header">
                <div class="challenge-modal-title">👥 邀请同学加入学习小组</div>
                <button class="challenge-modal-close" onclick="ChallengePage._closeModal()">×</button>
            </div>
            <div class="challenge-form-row">
                <div class="challenge-modal-info">邀请 3-5 名同学组成学习小组，互相鼓励、共同成长。仅显示学习时长，不显示具体成绩。</div>
            </div>
            <div class="challenge-form-row">
                <label class="challenge-form-label">组员昵称（每行一个）</label>
                <textarea class="challenge-input" id="companion-input" rows="4" placeholder="同学 A&#10;同学 B&#10;同学 C"></textarea>
            </div>
            <div class="challenge-form-actions">
                <button class="challenge-btn-ghost" onclick="ChallengePage._closeModal()">取消</button>
                <button class="challenge-btn-primary" onclick="ChallengePage._closeModal(); showToast && showToast('已发送邀请（模拟）', 'success');">发送邀请</button>
            </div>
        `;
        this.openModal(html);
    }

    // ====================== 工具方法 ======================

    _escape(str) {
        if (str == null) return '';
        return String(str).replace(/[&<>"']/g, (m) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[m]));
    }
}

// 单例暴露
window.ChallengePage = new ChallengePage();
// 兼容别名（提示词约定 ChallengeManager.ChallengePage.openModal）
window.ChallengeManager = window.ChallengePage;