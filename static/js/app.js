/**
 * StudyPal 应用主入口 - 清风版
 * 2026-05-21
 */

const App = {
    currentPage: 'home',
    isStudying: false,
    studyTimer: null,
    studyStartTime: null,
    currentSubject: '数学',
    timerSeconds: 25 * 60,
    timerDuration: 25 * 60,
    chatHistory: [],
    selectedEmotionLevel: 3,
    user: null,
    token: null,
    roles: [],
    currentRole: null,
    dailyGoalHours: 8,
    data: {},
    presetModels: [],
    currentModel: null,
    currentModelMode: 'preset',
    selectedPresetKey: null,

    /* ========== 初始化 ========== */
    async init() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');

        this.applyTheme(localStorage.getItem('theme') || 'light');

        if (!this.token) {
            window.location.href = '/login';
            return;
        }

        this.updateGreeting();
        await this.loadData();
        this.initNav();
        this.initChat();
        this.initTimer();
        this.initDiary();
        this.initTasks();
        this.initSettings();

        setInterval(() => this.updateGreeting(), 60000);
    },

    /* ========== 数据加载 ========== */
    async loadData() {
        try {
            const res = await fetch('/api/buddy/status', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (!res.ok) throw new Error('加载失败');
            const data = await res.json();

            if (data.success) {
                this.data = data.status || {};
            }
        } catch (e) {
            console.warn('数据加载失败，使用默认数据', e);
        }

        try {
            const res2 = await fetch('/api/home', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (res2.ok) {
                const data2 = await res2.json();
                if (data2.success) {
                    this.data = { ...this.data, ...data2.data };
                }
            }
        } catch (e) {}

        try {
            const res3 = await fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (res3.ok) {
                const data3 = await res3.json();
                if (data3.success) {
                    this.user = data3.user;
                    localStorage.setItem('user', JSON.stringify(this.user));
                }
            }
        } catch (e) {}

        this.renderAll();
    },

    renderAll() {
        this.renderBuddy();
        this.renderStats();
        this.renderProfile();
        this.renderGoal();
        this.renderAchievements();
    },

    /* ========== 导航 ========== */
    initNav() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                this.navigate(page);
            });
        });
    },

    navigate(page) {
        this.currentPage = page;

        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
        });
        const target = document.getElementById(`page-${page}`);
        if (target) {
            target.classList.add('active');
            target.style.opacity = '0';
            requestAnimationFrame(() => {
                target.style.opacity = '1';
            });
            if (page === 'challenges' && typeof this.mountChallenges === 'function') {
                setTimeout(() => this.mountChallenges(), 0);
            }
        }

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });
    },

    /* ========== 问候语 ========== */
    updateGreeting() {
        const hour = new Date().getHours();
        let greeting = '晚上好';
        if (hour < 6) greeting = '夜深了';
        else if (hour < 9) greeting = '早上好';
        else if (hour < 12) greeting = '上午好';
        else if (hour < 14) greeting = '中午好';
        else if (hour < 18) greeting = '下午好';

        const el = document.getElementById('greeting-text');
        if (el) el.textContent = greeting;

        const nameEl = document.getElementById('user-name');
        if (nameEl) nameEl.textContent = this.user?.nickname || '考研战士';
    },

    /* ========== 搭子 ========== */
    renderBuddy() {
        const buddy = this.data.buddy || {};
        const name = buddy.name || '小豆';
        const emoji = buddy.emoji || '&#128150;';
        const emotion = buddy.emotion || 'happy';
        const emotionText = buddy.emotion_desc || '心情不错~';
        const message = buddy.message || this._getDefaultMessage();

        const nameEl = document.getElementById('buddy-name');
        if (nameEl) nameEl.textContent = name;

        const avatarEl = document.getElementById('buddy-avatar');
        if (avatarEl) avatarEl.innerHTML = emoji;

        const emotionTextEl = document.getElementById('buddy-emotion-text');
        if (emotionTextEl) emotionTextEl.textContent = emotionText;

        const msgEl = document.getElementById('buddy-msg');
        if (msgEl) msgEl.textContent = message;

        const emotionDotEl = document.getElementById('buddy-emotion-dot');
        if (emotionDotEl) {
            emotionDotEl.style.background = this._getEmotionColor(emotion);
        }

        const chatAvatarEl = document.getElementById('chat-buddy-avatar');
        if (chatAvatarEl) chatAvatarEl.innerHTML = emoji;

        const chatNameEl = document.getElementById('chat-buddy-name');
        if (chatNameEl) chatNameEl.textContent = `和${name}聊天`;
    },

    _getDefaultMessage() {
        const hour = new Date().getHours();
        if (hour >= 22 || hour < 6) return '夜深了，早点休息哦~';
        const todayHours = this.data.study?.today_hours || 0;
        if (todayHours > 0) return `今天学了 ${todayHours.toFixed(1)} 小时，继续加油！`;
        return '今天想学点什么？';
    },

    _getEmotionColor(emotion) {
        const colors = {
            happy: 'var(--emotion-happy)',
            excited: 'var(--sunny)',
            calm: 'var(--emotion-calm)',
            worried: 'var(--emotion-anxious)',
            sad: 'var(--emotion-sad)',
            study: 'var(--sky)',
            idle: 'var(--mint)',
        };
        return colors[emotion] || 'var(--mint)';
    },

    startChat() {
        this.navigate('chat');
    },

    /* ========== 统计 ========== */
    renderStats() {
        const study = this.data.study || {};
        const hours = study.today_hours || 0;
        const sessions = study.today_sessions || 0;
        const streak = study.streak_days || this.user?.current_streak || 0;
        const goal = this.user?.daily_goal_hours || this.dailyGoalHours || 8;
        const progress = Math.min(100, Math.round((hours / goal) * 100));

        const hoursEl = document.getElementById('today-hours');
        if (hoursEl) hoursEl.textContent = hours.toFixed(1);

        const sessionsEl = document.getElementById('today-sessions');
        if (sessionsEl) sessionsEl.textContent = sessions;

        const goalEl = document.getElementById('today-goal');
        if (goalEl) goalEl.textContent = progress + '%';

        const progressBarEl = document.getElementById('today-progress-bar');
        if (progressBarEl) progressBarEl.style.width = progress + '%';

        const streakEl = document.getElementById('streak-num');
        if (streakEl) streakEl.textContent = streak;
    },

    /* ========== 目标 ========== */
    renderProfile() {
        const nameEl = document.getElementById('settings-name');
        if (nameEl) nameEl.textContent = this.user?.nickname || '考研战士';

        const emailEl = document.getElementById('settings-email');
        if (emailEl) emailEl.textContent = this.user?.email || '';

        const avatarEl = document.getElementById('settings-avatar');
        if (avatarEl) avatarEl.textContent = this.user?.avatar || '&#128100;';

        const totalHoursEl = document.getElementById('stat-total-hours');
        if (totalHoursEl) totalHoursEl.textContent = (this.user?.total_study_hours || 0).toFixed(1) + ' 小时';

        const streakEl = document.getElementById('stat-streak');
        if (streakEl) streakEl.textContent = (this.user?.current_streak || 0) + ' 天';

        const longestEl = document.getElementById('stat-longest');
        if (longestEl) longestEl.textContent = (this.user?.longest_streak || 0) + ' 天';

        const schoolEl = document.getElementById('setting-school');
        if (schoolEl) schoolEl.value = this.user?.target_school || '';

        const majorEl = document.getElementById('setting-major');
        if (majorEl) majorEl.value = this.user?.target_major || '';

        const scoreEl = document.getElementById('setting-score');
        if (scoreEl) scoreEl.value = this.user?.target_score || '';

        const goalHoursEl = document.getElementById('setting-goal-hours');
        if (goalHoursEl) {
            goalHoursEl.value = this.user?.daily_goal_hours || 8;
            document.getElementById('goal-hours-val').textContent = goalHoursEl.value;
        }

        const darkToggleEl = document.getElementById('dark-toggle');
        if (darkToggleEl) {
            darkToggleEl.classList.toggle('active', this._currentTheme === 'dark');
        }

        const currentRoleEl = document.getElementById('current-role-name');
        if (currentRoleEl) currentRoleEl.textContent = this.currentRole?.name || '小豆';
    },

    renderGoal() {
        const schoolEl = document.getElementById('goal-school');
        if (schoolEl) schoolEl.textContent = this.user?.target_school || '未设置';
        const majorEl = document.getElementById('goal-major');
        if (majorEl) majorEl.textContent = this.user?.target_major || '未设置';
        const scoreEl = document.getElementById('goal-score');
        if (scoreEl) scoreEl.textContent = this.user?.target_score || '--';
        const daysEl = document.getElementById('goal-days');
        if (daysEl) {
            const days = this._calcDaysRemaining();
            daysEl.textContent = days > 0 ? days : '--';
        }
    },

    _calcDaysRemaining() {
        if (!this.user?.exam_date) return 0;
        const exam = new Date(this.user.exam_date);
        const now = new Date();
        return Math.max(0, Math.ceil((exam - now) / (1000 * 60 * 60 * 24)));
    },

    /* ========== 学习计时 ========== */
    initTimer() {
        document.querySelectorAll('.subject-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.subject-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                this.currentSubject = chip.dataset.subject;
                const subjectEl = document.getElementById('timer-subject');
                if (subjectEl) subjectEl.textContent = this._getSubjectEmoji(this.currentSubject) + ' ' + this.currentSubject;
            });
        });
    },

    _getSubjectEmoji(subject) {
        const map = { '数学': '&#128220;', '英语': '&#128214;', '政治': '&#127963;', '专业课': '&#128218;' };
        return map[subject] || '&#128218;';
    },

    toggleStudy() {
        const card = document.getElementById('study-timer-card');
        if (!card) return;

        if (card.style.display === 'none' || !card.style.display) {
            card.style.display = 'block';
            document.getElementById('btn-start-study').querySelector('.quick-action-label').textContent = '收起计时器';
        } else {
            card.style.display = 'none';
            document.getElementById('btn-start-study').querySelector('.quick-action-label').textContent = '开始学习';
        }
    },

    toggleTimer() {
        if (this.studyTimer) {
            this.stopTimer();
        } else {
            this.startTimer();
        }
    },

    startTimer() {
        if (!this.studyStartTime) {
            this.studyStartTime = Date.now();
        }

        this.studyTimer = setInterval(() => {
            this.timerSeconds--;
            if (this.timerSeconds <= 0) {
                this.timerComplete();
            }
            this.updateTimerDisplay();
        }, 1000);

        const btn = document.getElementById('btn-timer-start');
        if (btn) {
            btn.innerHTML = '&#9646;&#9646; 暂停';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-coral');
        }
    },

    stopTimer() {
        clearInterval(this.studyTimer);
        this.studyTimer = null;
        const btn = document.getElementById('btn-timer-start');
        if (btn) {
            btn.innerHTML = '&#9654; 继续';
            btn.classList.add('btn-primary');
            btn.classList.remove('btn-coral');
        }
    },

    timerComplete() {
        clearInterval(this.studyTimer);
        this.studyTimer = null;
        this.timerSeconds = this.timerDuration;

        this.showToast('&#127881; 番茄完成！休息一下吧~');

        const duration = this.timerDuration / 60;
        this._recordSession(duration);

        this.updateTimerDisplay();
        const btn = document.getElementById('btn-timer-start');
        if (btn) btn.innerHTML = '&#9654; 再来一个';
    },

    async _recordSession(duration) {
        const studyData = this.data.study || {};
        studyData.today_hours = (studyData.today_hours || 0) + duration / 60;
        studyData.today_sessions = (studyData.today_sessions || 0) + 1;
        this.data.study = studyData;
        this.renderStats();

        try {
            await fetch('/api/study/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    subject: this.currentSubject,
                    duration_minutes: Math.round(duration),
                    date: new Date().toISOString().split('T')[0]
                })
            });
        } catch (e) {
            console.warn('记录学习时段失败', e);
        }
    },

    updateTimerDisplay() {
        const minutes = Math.floor(this.timerSeconds / 60);
        const seconds = this.timerSeconds % 60;
        const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        const displayEl = document.getElementById('timer-display');
        if (displayEl) displayEl.textContent = timeStr;

        const ringEl = document.getElementById('timer-ring');
        if (ringEl) {
            const circumference = 364.4;
            const progress = 1 - (this.timerSeconds / this.timerDuration);
            ringEl.style.strokeDashoffset = circumference * (1 - progress);
        }
    },

    /* ========== 聊天 ========== */
    initChat() {
        const input = document.getElementById('chat-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendChat();
            });
        }
    },

    async sendChat() {
        const input = document.getElementById('chat-input');
        if (!input) return;
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        this.addChatBubble(message, 'user');
        this.scrollChat();

        try {
            const res = await fetch('/api/buddy/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ message })
            });

            const data = await res.json();
            if (data.success) {
                this.addChatBubble(data.reply, 'buddy');
                const buddy = this.data.buddy || {};
                if (data.emotion) {
                    buddy.emotion = data.emotion;
                    buddy.emoji = data.emoji || buddy.emoji;
                    this.data.buddy = buddy;
                    this.renderBuddy();
                }
            } else {
                this.addChatBubble('抱歉，' + (data.error || '出了点小问题'), 'buddy');
            }
        } catch (e) {
            this.addChatBubble('网络连接不稳定，稍后再试试吧~', 'buddy');
        }

        this.scrollChat();
    },

    addChatBubble(content, role) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const emptyState = container.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const buddy = this.data.buddy || {};
        const avatar = role === 'buddy' ? (buddy.emoji || '&#128150;') : '&#128100;';

        const wrap = document.createElement('div');
        wrap.className = `chat-bubble-wrap ${role}`;
        wrap.innerHTML = `
            <div class="chat-bubble-avatar">${avatar}</div>
            <div class="chat-bubble">${this._escapeHtml(content)}</div>
        `;
        container.appendChild(wrap);
    },

    scrollChat() {
        const container = document.getElementById('chat-messages');
        if (container) {
            setTimeout(() => container.scrollTop = container.scrollHeight, 50);
        }
    },

    async switchRole() {
        try {
            const res = await fetch('/api/buddy/roles', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();

            if (!data.success) return;

            const roles = data.roles || [];
            const listEl = document.getElementById('role-list');
            if (!listEl) return;

            listEl.innerHTML = roles.map(role => `
                <div class="role-item ${role.id === this.currentRole?.id ? 'active' : ''}"
                     onclick="App.selectRole('${role.id}')" style="
                    display:flex;align-items:center;gap:12px;
                    padding:14px;background:var(--bg-soft);
                    border-radius:var(--border-radius-md);
                    cursor:pointer;
                    border:2px solid ${role.id === this.currentRole?.id ? 'var(--mint)' : 'transparent'};
                    transition:all 150ms ease;
                    margin-bottom:8px;">
                    <div style="font-size:32px;">${role.emoji}</div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:600;font-size:15px;color:var(--text);">${role.name}</div>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">${role.tagline}</div>
                    </div>
                </div>
            `).join('');

            this.openModal('role-modal');
        } catch (e) {
            this.showToast('加载角色列表失败');
        }
    },

    async selectRole(roleId) {
        try {
            const res = await fetch('/api/buddy/role/switch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ role_id: roleId })
            });
            const data = await res.json();
            if (data.success) {
                this.currentRole = data.role;
                this.data.buddy = {
                    name: data.role.name,
                    emoji: data.role.emoji,
                    emotion: 'happy',
                    emotion_desc: '正在认识新搭子'
                };
                this.renderBuddy();
                this.closeRoleModal();
                this.showToast(`已切换到 ${data.role.name}！`);
            }
        } catch (e) {
            this.showToast('切换失败，请重试');
        }
    },

    /* ========== 日记 ========== */
    initDiary() {
        const today = new Date();
        const dateEl = document.getElementById('diary-date');
        if (dateEl) {
            dateEl.textContent = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`;
        }

        document.querySelectorAll('.emotion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.emotion-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.selectedEmotionLevel = parseInt(btn.dataset.level);
            });
        });

        this.loadDiaries();
    },

    async saveDiary() {
        const content = document.getElementById('diary-content')?.value.trim();
        if (!content) {
            this.showToast('写点什么吧~');
            return;
        }

        try {
            const res = await fetch('/api/diary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    content,
                    emotion_level: this.selectedEmotionLevel,
                    emotion_label: ['很难受', '有点丧', '一般', '还好', '很开心'][this.selectedEmotionLevel - 1],
                    date: new Date().toISOString().split('T')[0]
                })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('日记已保存~');
                document.getElementById('diary-content').value = '';
                this.loadDiaries();
            }
        } catch (e) {
            this.showToast('保存失败，请重试');
        }
    },

    async loadDiaries() {
        try {
            const res = await fetch('/api/diary', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.renderDiaryList(data.diaries || []);
            }
        } catch (e) {}
    },

    renderDiaryList(diaries) {
        const container = document.getElementById('diary-list');
        if (!container) return;

        if (!diaries.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">&#128214;</div>
                    <div class="empty-state-title">还没有日记</div>
                    <div class="empty-state-desc">记录每天的心情，搭子会帮你分析</div>
                </div>`;
            return;
        }

        container.innerHTML = diaries.slice(0, 10).map(d => `
            <div class="diary-list-item">
                <div class="diary-list-date">
                    <span>${this._formatDate(d.date)}</span>
                    <span style="font-size:18px;">${this._getEmotionEmoji(d.emotion_level)}</span>
                </div>
                <div class="diary-list-content">${this._escapeHtml(d.content || '')}</div>
            </div>
        `).join('');
    },

    _getEmotionEmoji(level) {
        const map = { 1: '&#128546;', 2: '&#128557;', 3: '&#128528;', 4: '&#128578;', 5: '&#128513;' };
        return map[level] || '&#128528;';
    },

    _formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return `${d.getMonth() + 1}月${d.getDate()}日`;
    },

    /* ========== 任务 ========== */
    initTasks() {
        document.querySelectorAll('.task-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.task-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterTasks(tab.dataset.filter);
            });
        });
        this.loadTasks();
    },

    async loadTasks() {
        try {
            const res = await fetch('/api/tasks', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.tasks = data.tasks || [];
                this.renderTaskList('all');
            }
        } catch (e) {
            this.tasks = [];
        }
    },

    renderTaskList(filter) {
        const container = document.getElementById('task-list');
        if (!container) return;

        let tasks = this.tasks || [];
        if (filter === 'pending') tasks = tasks.filter(t => t.status !== 'completed');
        if (filter === 'completed') tasks = tasks.filter(t => t.status === 'completed');

        if (!tasks.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">&#9745;</div>
                    <div class="empty-state-title">${filter === 'completed' ? '还没有完成的任务' : filter === 'pending' ? '待办已清空' : '任务空空'}</div>
                    <div class="empty-state-desc">点击上方按钮添加任务</div>
                </div>`;
            return;
        }

        container.innerHTML = tasks.map(t => `
            <div class="task-item ${t.status === 'completed' ? 'completed' : ''}" onclick="App.toggleTask(${t.id})">
                <div class="task-check">${t.status === 'completed' ? '&#10003;' : ''}</div>
                <div class="task-item-content">
                    <div class="task-item-title">${this._escapeHtml(t.title)}</div>
                    ${t.subject ? `<div class="task-item-meta">${t.subject}</div>` : ''}
                </div>
            </div>
        `).join('');
    },

    filterTasks(filter) {
        this.renderTaskList(filter);
    },

    async toggleTask(taskId) {
        const task = (this.tasks || []).find(t => t.id === taskId);
        if (!task) return;

        const newStatus = task.status === 'completed' ? 'pending' : 'completed';
        try {
            await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ status: newStatus })
            });
            task.status = newStatus;
            this.renderTaskList(document.querySelector('.task-tab.active')?.dataset.filter || 'all');
        } catch (e) {}
    },

    showAddTask() {
        const title = prompt('输入任务名称:');
        if (!title?.trim()) return;

        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({ title: title.trim() })
        }).then(res => res.json()).then(data => {
            if (data.success) {
                this.tasks = [data.task, ...(this.tasks || [])];
                this.renderTaskList('all');
                this.showToast('任务已添加');
            }
        });
    },

    /* ========== 成就 ========== */
    async renderAchievements() {
        try {
            const res = await fetch('/api/achievements', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                const all = data.achievements || [];
                const unlocked = all.filter(a => a.unlocked_at);

                const unlockedEl = document.getElementById('ach-unlocked');
                if (unlockedEl) unlockedEl.textContent = unlocked.length;

                const totalEl = document.getElementById('ach-total');
                if (totalEl) totalEl.textContent = all.length;

                const pointsEl = document.getElementById('ach-points');
                if (pointsEl) pointsEl.textContent = unlocked.reduce((sum, a) => sum + (a.points || 0), 0);

                const listEl = document.getElementById('ach-list');
                if (listEl) {
                    listEl.innerHTML = all.map(a => `
                        <div class="ach-item ${a.unlocked_at ? '' : 'locked'}">
                            <div class="ach-icon">${a.icon || '&#127942;'}</div>
                            <div class="ach-content">
                                <div class="ach-name">${a.name}</div>
                                <div class="ach-desc">${a.description || ''}</div>
                            </div>
                            <div class="ach-points">+${a.points || 0}</div>
                        </div>
                    `).join('');
                }
            }
        } catch (e) {}
    },

    /* ========== 设置 ========== */
    initSettings() {
        // 设置页面中的保存按钮
    },

    async saveProfile() {
        const school = document.getElementById('setting-school')?.value;
        const major = document.getElementById('setting-major')?.value;
        const score = document.getElementById('setting-score')?.value;
        const examDate = document.getElementById('setting-exam-date')?.value;
        const goalHours = document.getElementById('setting-goal-hours')?.value;

        try {
            const res = await fetch('/api/auth/me', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    target_school: school,
                    target_major: major,
                    target_score: parseInt(score) || 0,
                    exam_date: examDate || null,
                    daily_goal_hours: parseFloat(goalHours) || 8
                })
            });
            const data = await res.json();
            if (data.success) {
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(this.user));
                this.renderGoal();
                this.renderProfile();
                this.showToast('目标已保存！');
            }
        } catch (e) {
            this.showToast('保存失败，请重试');
        }
    },

    /* ========== 主题 ========== */
    _currentTheme: 'light',

    applyTheme(theme) {
        this._currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        const iconEl = document.getElementById('theme-icon');
        if (iconEl) iconEl.innerHTML = theme === 'dark' ? '&#9728;' : '&#127769;';
    },

    toggleTheme() {
        const newTheme = this._currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        const darkToggle = document.getElementById('dark-toggle');
        if (darkToggle) darkToggle.classList.toggle('active', newTheme === 'dark');
    },

    /* ========== Toast ========== */
    showToast(message) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = message;
        container.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add('show'));

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    },

    /* ========== 模态框 ========== */
    openModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    },

    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    },

    closeRoleModal() {
        this.closeModal('role-modal');
    },

    closeAchievement() {
        this.closeModal('achievement-modal');
    },

    /* ========== AI 模型配置 ========== */
    async showModelConfig() {
        this.openModal('model-modal');
        await this.loadPresetModels();
        await this.loadCurrentModel();
        this.renderPresetModelList();
    },

    closeModelModal() {
        this.closeModal('model-modal');
    },

    async loadPresetModels() {
        try {
            const res = await fetch('/api/ai-model/presets');
            const data = await res.json();
            if (data.success) {
                this.presetModels = data.presets || [];
            }
        } catch (e) {
            this.presetModels = [];
        }
    },

    async loadCurrentModel() {
        try {
            const res = await fetch('/api/ai-model/current', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.currentModel = data.model;
                this.currentModelMode = data.mode;
                this.selectedPresetKey = data.model_key;

                const nameEl = document.getElementById('current-model-name');
                if (nameEl) {
                    nameEl.textContent = data.model.name;
                }
            }
        } catch (e) {}
    },

    renderPresetModelList() {
        const container = document.getElementById('preset-model-list');
        if (!container) return;

        const providerMap = {
            'openai': '&#127760; 云端',
            'ollama': '&#128187; 本地'
        };

        container.innerHTML = this.presetModels.map(m => {
            const isSelected = this.currentModelMode === 'preset' && this.selectedPresetKey === m.key;
            return `
                <div class="role-item ${isSelected ? 'active' : ''}"
                     onclick="App.selectPresetModel('${m.key}')" style="
                    display:flex;align-items:center;gap:12px;
                    padding:14px;background:var(--bg-soft);
                    border-radius:var(--border-radius-md);
                    cursor:pointer;
                    border:2px solid ${isSelected ? 'var(--mint)' : 'transparent'};
                    transition:all 150ms ease;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:600;font-size:15px;color:var(--text);">${this._escapeHtml(m.name)}</div>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">${m.model} · ${providerMap[m.provider] || m.provider}</div>
                    </div>
                    ${isSelected ? '<span style="color:var(--mint);font-size:18px;">&#10003;</span>' : ''}
                </div>
            `;
        }).join('');
    },

    switchModelTab(tab) {
        document.querySelectorAll('#model-modal .task-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.filter === tab);
        });

        const presetList = document.getElementById('preset-model-list');
        const customForm = document.getElementById('custom-model-form');
        if (presetList && customForm) {
            presetList.style.display = tab === 'preset' ? 'flex' : 'none';
            customForm.style.display = tab === 'custom' ? 'block' : 'none';
        }
        this.currentModelMode = tab;

        if (tab === 'custom' && this.currentModelMode === 'custom') {
            const config = this.currentModel;
            if (config) {
                document.getElementById('custom-model-name').value = config.name || '';
                document.getElementById('custom-model-url').value = config.base_url || '';
                document.getElementById('custom-model-model').value = config.model || '';
            }
        }
    },

    selectPresetModel(key) {
        this.selectedPresetKey = key;
        this.currentModelMode = 'preset';
        this.renderPresetModelList();
    },

    async testCustomModel() {
        const baseUrl = document.getElementById('custom-model-url')?.value.trim();
        const apiKey = document.getElementById('custom-model-key')?.value.trim();
        const model = document.getElementById('custom-model-model')?.value.trim();
        const resultEl = document.getElementById('test-result');
        const btn = document.getElementById('btn-test-model');

        if (!baseUrl || !apiKey || !model) {
            if (resultEl) {
                resultEl.innerHTML = '<span style="color:var(--coral);">请填写完整的模型配置</span>';
            }
            return;
        }

        if (resultEl) resultEl.innerHTML = '<span style="color:var(--text-muted);">测试连接中...</span>';
        if (btn) btn.disabled = true;

        try {
            const res = await fetch('/api/ai-model/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ base_url: baseUrl, api_key: apiKey, model: model })
            });
            const data = await res.json();
            if (data.success) {
                if (resultEl) resultEl.innerHTML = `<span style="color:var(--mint);">&#10003; 连接成功！</span>`;
            } else {
                if (resultEl) resultEl.innerHTML = `<span style="color:var(--coral);">&#10007; ${this._escapeHtml(data.error || '连接失败')}</span>`;
            }
        } catch (e) {
            if (resultEl) resultEl.innerHTML = `<span style="color:var(--coral);">&#10007; 网络错误</span>`;
        }

        if (btn) btn.disabled = false;
    },

    async saveModelConfig() {
        if (this.currentModelMode === 'preset') {
            if (!this.selectedPresetKey) {
                this.showToast('请选择一个模型');
                return;
            }

            try {
                const res = await fetch('/api/ai-model/preset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({ model_key: this.selectedPresetKey })
                });
                const data = await res.json();
                if (data.success) {
                    const model = this.presetModels.find(m => m.key === this.selectedPresetKey);
                    const nameEl = document.getElementById('current-model-name');
                    if (nameEl && model) nameEl.textContent = model.name;
                    this.closeModelModal();
                    this.showToast('模型已切换');
                }
            } catch (e) {
                this.showToast('保存失败');
            }
        } else {
            const name = document.getElementById('custom-model-name')?.value.trim() || '自定义模型';
            const baseUrl = document.getElementById('custom-model-url')?.value.trim();
            const apiKey = document.getElementById('custom-model-key')?.value.trim();
            const model = document.getElementById('custom-model-model')?.value.trim();

            if (!baseUrl || !apiKey || !model) {
                this.showToast('请填写完整的自定义配置');
                return;
            }

            try {
                const res = await fetch('/api/ai-model/custom', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({ name, base_url: baseUrl, api_key: apiKey, model })
                });
                const data = await res.json();
                if (data.success) {
                    const nameEl = document.getElementById('current-model-name');
                    if (nameEl) nameEl.textContent = name;
                    this.closeModelModal();
                    this.showToast('自定义模型已保存');
                } else {
                    this.showToast(data.error || '保存失败');
                }
            } catch (e) {
                this.showToast('保存失败');
            }
        }
    },

    /* ========== 用户 ========== */
    openProfile() {
        this.navigate('settings');
    },

    logout() {
        if (!confirm('确定要退出登录吗？')) return;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    },

    /* ========== 工具 ========== */
    _escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    /* ========== 数据洞察 ========== */
    async loadInsights(days = 30) {
        try {
            const [overviewRes, studyChartRes, subjectRes, emotionRes] = await Promise.all([
                fetch(`/api/insights/overview?days=${days}`),
                fetch(`/api/insights/study-chart?days=${days}`),
                fetch(`/api/insights/subject-analysis?days=${days}`),
                fetch(`/api/insights/emotion-chart?days=${days}`),
            ]);

            const overview = await overviewRes.json();
            const studyChart = await studyChartRes.json();
            const subjects = await subjectRes.json();
            const emotions = await emotionRes.json();

            if (overview.success) {
                const o = overview.overview;
                document.getElementById('insight-total-hours').textContent = o.total_hours;
                document.getElementById('insight-daily-avg').textContent = o.daily_average;
                document.getElementById('insight-total-sessions').textContent = o.total_sessions;
                document.getElementById('insight-diary-count').textContent = o.total_entries;
            }

            if (studyChart.success) {
                this.renderStudyChart(studyChart.chart_data);
            }

            if (subjects.success) {
                this.renderSubjectAnalysis(subjects.subjects);
            }

            if (emotions.success) {
                this.renderEmotionChart(emotions.chart_data);
            }
        } catch (e) {
            console.error('加载洞察数据失败:', e);
        }
    },

    switchInsightPeriod(days) {
        document.querySelectorAll('.insight-tab').forEach(t => {
            t.classList.toggle('active', parseInt(t.dataset.days) === days);
        });
        this.loadInsights(days);
    },

    renderStudyChart(data) {
        const canvas = document.getElementById('study-canvas');
        const placeholder = document.getElementById('study-chart-placeholder');
        if (!canvas || !placeholder) return;

        // 检查是否有数据
        const hasData = data.some(d => d.hours > 0);
        if (!hasData) {
            canvas.style.display = 'none';
            placeholder.style.display = 'flex';
            return;
        }

        canvas.style.display = 'block';
        placeholder.style.display = 'none';

        // 简单的柱状图渲染
        const ctx = canvas.getContext('2d');
        const width = canvas.width = canvas.offsetWidth * 2;
        const height = canvas.height = 160 * 2;
        ctx.scale(2, 2);

        const w = width / 2;
        const h = height / 2;
        const barWidth = Math.min(20, (w - 40) / data.length);
        const gap = Math.max(2, (w - 40 - barWidth * data.length) / (data.length + 1));
        const maxHours = Math.max(...data.map(d => d.hours), 1);

        ctx.clearRect(0, 0, w, h);

        // 绘制柱状图
        data.forEach((d, i) => {
            const x = 20 + gap * (i + 1) + barWidth * i;
            const barHeight = (d.hours / maxHours) * (h - 40);
            const y = h - 20 - barHeight;

            // 渐变填充
            const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
            gradient.addColorStop(0, '#5BBFAA');
            gradient.addColorStop(1, '#3D9B8D');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.roundRect(x, y, barWidth, barHeight, 4);
            ctx.fill();

            // 数值标签（只显示非零值）
            if (d.hours > 0 && barWidth >= 12) {
                ctx.fillStyle = '#666';
                ctx.font = '10px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(d.hours.toFixed(1), x + barWidth / 2, y - 4);
            }

            // 日期标签（只显示部分）
            if (data.length <= 7 || i % Math.ceil(data.length / 7) === 0) {
                ctx.fillStyle = '#999';
                ctx.font = '9px sans-serif';
                ctx.textAlign = 'center';
                const dateStr = d.date.slice(5); // MM-DD
                ctx.fillText(dateStr, x + barWidth / 2, h - 5);
            }
        });

        // Y 轴网格线
        ctx.strokeStyle = '#eee';
        ctx.setLineDash([2, 2]);
        for (let i = 0; i <= 4; i++) {
            const y = h - 20 - (h - 40) * i / 4;
            ctx.beginPath();
            ctx.moveTo(15, y);
            ctx.lineTo(w - 5, y);
            ctx.stroke();
        }
        ctx.setLineDash([]);
    },

    renderSubjectAnalysis(subjects) {
        const container = document.getElementById('subject-list');
        if (!container) return;

        if (!subjects || subjects.length === 0) {
            container.innerHTML = `
                <div class="empty-state empty-state-sm">
                    <div class="empty-state-title">暂无科目数据</div>
                </div>`;
            return;
        }

        const colors = ['#5BBFAA', '#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3'];
        container.innerHTML = subjects.map((s, i) => `
            <div class="subject-item">
                <div class="subject-color" style="background: ${colors[i % colors.length]}"></div>
                <div class="subject-name">${this._escapeHtml(s.subject)}</div>
                <div class="subject-hours">${s.total_hours}h</div>
                <div class="subject-percent">${s.percentage}%</div>
            </div>
            <div class="subject-bar">
                <div class="subject-bar-fill" style="width: ${s.percentage}%; background: ${colors[i % colors.length]}"></div>
            </div>
        `).join('');
    },

    renderEmotionChart(data) {
        const container = document.getElementById('emotion-list');
        if (!container) return;

        const emotionMap = {
            5: { class: 'emotion-very-good', icon: '&#128513;' },
            4: { class: 'emotion-good', icon: '&#128578;' },
            3: { class: 'emotion-normal', icon: '&#128528;' },
            2: { class: 'emotion-bad', icon: '&#128533;' },
            1: { class: 'emotion-very-bad', icon: '&#128542;' },
        };

        // 只显示最近14天
        const recent = data.slice(-14);
        container.innerHTML = recent.map(d => {
            if (d.level === null) {
                return `<div class="emotion-bar">
                    <div class="emotion-bar-date">${d.date.slice(5)}</div>
                    <div class="emotion-bar-dot emotion-normal" style="opacity:0.3">-</div>
                </div>`;
            }
            const em = emotionMap[d.level] || emotionMap[3];
            return `<div class="emotion-bar">
                <div class="emotion-bar-date">${d.date.slice(5)}</div>
                <div class="emotion-bar-dot ${em.class}">${em.icon}</div>
            </div>`;
        }).join('');
    },

    mountInsights() {
        this.loadInsights(30);
    },

    mountChallenges() {
        if (window.ChallengePage) {
            window.ChallengePage.mount();
        }
    },
};

/* ========== 暴露全局 ========== */
window.App = App;
