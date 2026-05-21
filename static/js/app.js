/**
 * StudyPal 应用主入口 v2.1
 * 有情绪的考研搭子
 */

// 获取全局组件
const HomePage = window.HomePage;
const ChatPage = window.ChatPage;
const DiaryPage = window.DiaryPage;
const MemoryPage = window.MemoryPage;
const TasksPage = window.TasksPage;
const PlansPage = window.PlansPage;
const AchievementsPage = window.AchievementsPage;
const SettingsPage = window.SettingsPage;
const NAV_ITEMS = window.NAV_ITEMS;

// 搭子情绪颜色映射
const EMOTION_COLORS = {
    idle: '#667EEA',
    happy: '#10B981',
    excited: '#F59E0B',
    proud: '#EF4444',
    thinking: '#8B5CF6',
    study: '#3B82F6',
    worried: '#F97316',
    sad: '#6366F1',
    angry: '#EF4444',
    sleepy: '#A855F7'
};

// 搭子情绪emoji映射
const EMOTION_EMOJIS = {
    idle: '😊',
    happy: '😄',
    excited: '🎉',
    proud: '😤',
    thinking: '🤔',
    study: '📚',
    worried: '😟',
    sad: '😢',
    angry: '😡',
    sleepy: '😪'
};

const App = {
    currentSubject: '数学',
    isStudying: false,
    studyTimer: null,
    studyStartTime: null,
    selectedEmotionLevel: 3,
    selectedFeeling: '',
    selectedGoalHours: 8,
    chatConversationId: null,
    chatHistory: [],

    /**
     * 应用初始化
     */
    async init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);

        this._initNavigation();
        await this.loadGlobalData();
        this.updateGreeting();
        this._initChat();

        setInterval(() => {
            if (router.getCurrentPage() === 'home') {
                this.updateGreeting();
            }
        }, 60000);

        State.subscribe('ui.currentPage', (page) => {
            this._updateNavHighlight(page);
        });
    },

    _initNavigation() {
        const nav = document.querySelector('.bottom-nav');
        if (!nav) return;

        nav.innerHTML = NAV_ITEMS.map(item => `
            <div class="nav-item" data-page="${item.page}" onclick="router.navigate('${item.page}')">
                <div class="nav-icon">${item.icon}</div>
                <div class="nav-label">${item.label}</div>
            </div>
        `).join('');
    },

    async loadGlobalData() {
        try {
            const res = await API.getHomeData();
            if (res.success) {
                const data = res.data;
                State.update({
                    'buddy.name': data.buddy?.name,
                    'buddy.emoji': data.buddy?.emoji,
                    'buddy.emotion': data.buddy?.emotion || 'idle',
                    'buddy.emotionDesc': data.buddy?.emotion_desc,
                    'buddy.message': this._generateBuddyMessage(data),
                    'study.isStudying': data.study?.is_studying,
                    'study.todayHours': data.study?.today_hours,
                    'study.streakDays': data.study?.streak_days,
                    'profile.isSetup': data.profile?.is_setup,
                    'profile.name': data.profile?.user?.name,
                    'profile.school': data.profile?.user?.target_school,
                    'profile.daysRemaining': data.profile?.days_remaining,
                });

                this.isStudying = data.study?.is_studying || false;
                this._updateBuddyCard(data);
                this._updateStats(data);

                if (!data.profile?.is_setup) {
                    router.navigate('settings');
                    this.showToast('先设置一下目标吧，让小豆更了解你~');
                }
            }
        } catch (e) {
            console.error('加载全局数据失败', e);
        }
    },

    _generateBuddyMessage(data) {
        const emotion = data.buddy?.emotion || 'idle';
        const hour = new Date().getHours();
        const todayHours = data.study?.today_hours || 0;
        const streak = data.study?.streak_days || 0;
        const hasDiary = data.diary?.has_today;

        if (hour >= 22 || hour < 6) {
            return '夜深了，早点休息哦~';
        }
        if (emotion === 'happy' || emotion === 'excited') {
            return '感觉今天状态不错！';
        }
        if (emotion === 'sad' || emotion === 'worried') {
            return '今天心情不太好？要不要聊聊？';
        }
        if (emotion === 'study') {
            return '学习中...加油！';
        }
        if (todayHours > 0) {
            return `今天学了 ${todayHours.toFixed(1)} 小时，继续保持！`;
        }
        if (streak > 3) {
            return `连续学习 ${streak} 天了，你真的很棒！`;
        }
        if (!hasDiary) {
            return '今天还没记录心情呢~';
        }
        if (hour >= 20) {
            return '晚上好！今天过得怎么样？';
        }
        if (hour >= 12) {
            return '下午好！今天学了什么？';
        }
        if (hour >= 6) {
            return '早上好！准备开始学习了吗？';
        }
        return '你好！今天感觉怎么样？';
    },

    _updateBuddyCard(data) {
        const name = data.buddy?.name || '小豆';
        const emotion = data.buddy?.emotion || 'idle';
        const emotionDesc = data.buddy?.emotion_desc || '';
        const message = State.get('buddy.message') || '';

        const nameEl = document.getElementById('buddy-name');
        if (nameEl) nameEl.textContent = name;

        const emojiEl = document.getElementById('buddy-emotion-emoji');
        if (emojiEl) emojiEl.textContent = EMOTION_EMOJIS[emotion] || '😊';

        const descEl = document.getElementById('buddy-emotion-desc');
        if (descEl) descEl.textContent = emotionDesc;

        const msgEl = document.getElementById('buddy-message');
        if (msgEl) msgEl.textContent = message;

        const avatarEl = document.getElementById('buddy-avatar');
        if (avatarEl) {
            avatarEl.textContent = EMOTION_EMOJIS[emotion] || '😊';
            avatarEl.className = `buddy-card-avatar emotion-${emotion}`;
        }
    },

    _updateStats(data) {
        const todayHours = data.study?.today_hours || 0;
        const streak = data.study?.streak_days || 0;
        const weekHours = data.study?.week_hours || 0;
        const goalHours = data.profile?.user?.daily_goal_hours || 8;

        const todayEl = document.getElementById('stat-today-hours');
        if (todayEl) todayEl.textContent = `${todayHours.toFixed(1)}h`;

        const streakEl = document.getElementById('stat-streak');
        if (streakEl) {
            streakEl.textContent = streak;
            const trendEl = streakEl.closest('.stat-card')?.querySelector('.stat-trend');
            if (trendEl) {
                if (streak >= 7) trendEl.textContent = '太厉害了';
                else if (streak >= 3) trendEl.textContent = '坚持中';
                else trendEl.textContent = streak > 0 ? '刚开始' : '加油';
            }
        }

        const weekEl = document.getElementById('stat-week-hours');
        if (weekEl) weekEl.textContent = `${weekHours.toFixed(1)}h`;

        const progressEl = document.getElementById('progress-value');
        if (progressEl) {
            const pct = Math.min(100, Math.round((todayHours / goalHours) * 100));
            progressEl.textContent = `${pct}%`;
        }

        const countdownEl = document.getElementById('countdown');
        const daysRemaining = data.profile?.days_remaining;
        if (countdownEl && daysRemaining > 0) {
            countdownEl.textContent = `距离考研还有 ${daysRemaining} 天`;
        } else if (countdownEl) {
            countdownEl.textContent = '设置考研目标';
        }

        const ringHoursEl = document.getElementById('ring-hours');
        if (ringHoursEl) ringHoursEl.textContent = goalHours;
        const ringAchievedEl = document.getElementById('ring-achieved');
        if (ringAchievedEl) ringAchievedEl.textContent = todayHours.toFixed(1);
    },

    updateGreeting() {
        const hour = new Date().getHours();
        let greeting = '晚上好';
        if (hour < 6) greeting = '夜深了';
        else if (hour < 9) greeting = '早上好';
        else if (hour < 12) greeting = '上午好';
        else if (hour < 14) greeting = '中午好';
        else if (hour < 18) greeting = '下午好';

        const name = State.get('profile.name');
        const el = document.getElementById('greeting');
        if (el) {
            el.textContent = name ? `${greeting}，${name}` : greeting;
        }
    },

    _initChat() {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    },

    // ==================== 页面切换 ====================

    switchPage(page) {
        router.navigate(page);
    },

    // ==================== 聊天核心 ====================

    async openChatWith(message) {
        router.navigate('chat');
        const input = document.getElementById('chat-input');
        if (input) {
            input.value = message;
            await this.sendMessage();
        }
    },

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input?.value.trim();
        if (!message) return;

        const container = document.getElementById('chat-messages');
        const sendBtn = document.getElementById('chat-send');

        // 用户消息 - 立即显示
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.innerHTML = `
            <div class="msg-avatar">我</div>
            <div class="msg-content">
                <div class="msg-bubble">${this.escapeHtml(message)}</div>
                <div class="msg-time">${this.formatTime(new Date())}</div>
            </div>
        `;
        container?.appendChild(userMsg);
        container?.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        if (input) input.value = '';
        if (sendBtn) sendBtn.disabled = true;

        // 保存到本地历史
        this.chatHistory.push({ role: 'user', content: message, time: this.formatTime(new Date()) });
        chatPage.history = this.chatHistory;

        // 显示搭子正在输入
        chatPage.showTyping('thinking');

        try {
            const res = await API.buddyChat(message, this.chatConversationId);
            chatPage.hideTyping();

            if (res.success) {
                this.chatConversationId = res.conversation_id;
                const emotion = res.emotion || 'idle';

                // 更新搭子头像和状态
                document.getElementById('chat-buddy-avatar').textContent = res.emoji;

                // 显示搭子回复，带情绪气泡
                chatPage.addMessage('buddy', res.reply, emotion);

                // 更新本地历史
                this.chatHistory.push({ role: 'buddy', content: res.reply, emotion, time: this.formatTime(new Date()) });

                // 显示回复建议
                if (res.suggestions && res.suggestions.length > 0) {
                    chatPage.showSuggestions(res.suggestions);
                }
            }
        } catch (e) {
            chatPage.hideTyping();
            const errorMsg = document.createElement('div');
            errorMsg.className = 'message buddy emotion-sad';
            errorMsg.innerHTML = `
                <div class="msg-avatar">${EMOTION_EMOJIS.sad}</div>
                <div class="msg-content">
                    <div class="msg-bubble emotion-bubble emotion-sad">连接失败了...可能是 AI 配置问题，请检查 .env 文件中的 API Key 设置。</div>
                    <div class="msg-time">${this.formatTime(new Date())}</div>
                </div>
            `;
            container?.appendChild(errorMsg);
            container?.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        }

        if (sendBtn) sendBtn.disabled = false;
    },

    async sendSuggestion(text) {
        const input = document.getElementById('chat-input');
        if (input) input.value = text;
        await this.sendMessage();
    },

    handleChatKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    },

    autoResize(el) {
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 120) + 'px';
    },

    // ==================== 工具方法 ====================

    formatTime(date) {
        const h = String(date.getHours()).padStart(2, '0');
        const m = String(date.getMinutes()).padStart(2, '0');
        return `${h}:${m}`;
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        const next = current === 'light' ? 'dark' : 'light';
        this.setTheme(next);
        localStorage.setItem('theme', next);
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const toggle = document.getElementById('theme-toggle');
        if (toggle) toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    },

    dismissCaring() {
        const section = document.getElementById('caring-section');
        if (section) section.style.display = 'none';
    },

    showEmotionChart() {
        const section = document.getElementById('emotion-chart-section');
        section?.scrollIntoView({ behavior: 'smooth' });
    },

    async exportData() {
        this.showToast('正在导出数据...');
        try {
            await API.exportData();
            this.showToast('数据导出成功！');
        } catch (e) {
            this.showToast('导出失败，请重试');
        }
    },

    showToast(msg, type = '') {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.textContent = msg;
            toast.className = `toast show ${type}`;
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2500);
        }
    },

    // ==================== 学习计时 ====================

    selectSubject(el) {
        if (this.isStudying) return;
        document.querySelectorAll('.subject-btn').forEach(b => b.classList.remove('selected'));
        el.classList.add('selected');
        this.currentSubject = el.dataset.subject;
    },

    async toggleStudy() {
        const btn = document.getElementById('study-btn');

        if (!this.isStudying) {
            const res = await API.startStudy(this.currentSubject);
            if (res.success) {
                this.isStudying = true;
                this.studyStartTime = Date.now();
                this.updateStudyUI();
                this.startStudyTimer();
                this.showToast(`开始学习 ${this.currentSubject}，加油！`);

                const avatar = document.getElementById('buddy-avatar');
                if (avatar) {
                    avatar.textContent = '📚';
                    avatar.className = 'buddy-card-avatar emotion-study';
                }
            }
        } else {
            const res = await API.stopStudy(this.currentSubject);
            if (res.success) {
                this.isStudying = false;
                clearInterval(this.studyTimer);
                this.studyTimer = null;
                this.updateStudyUI();
                await this.loadGlobalData();
                this.showToast(`学习了 ${Math.round(res.duration)} 分钟，休息一下吧~`);
            }
        }
    },

    updateStudyUI() {
        const btn = document.getElementById('study-btn');
        const timer = document.getElementById('study-timer');
        const subjects = document.getElementById('study-subjects');
        const avatar = document.getElementById('buddy-avatar');

        if (this.isStudying) {
            if (btn) {
                btn.innerHTML = '<span class="btn-glow-effect"></span><span class="btn-text">⏹️ 结束学习</span>';
                btn.className = 'study-btn stop';
            }
            if (timer) timer.style.display = 'block';
            if (subjects) subjects.style.display = 'none';
            const label = document.getElementById('timer-label');
            if (label) label.textContent = `学习中：${this.currentSubject}`;
            if (avatar) {
                avatar.textContent = '📚';
                avatar.className = 'buddy-card-avatar emotion-study';
            }
        } else {
            if (btn) {
                btn.innerHTML = '<span class="btn-glow-effect"></span><span class="btn-icon-animate">🚀</span><span class="btn-text">开始学习</span>';
                btn.className = 'study-btn start';
            }
            if (timer) timer.style.display = 'none';
            if (subjects) subjects.style.display = 'grid';
            const display = document.getElementById('timer-display');
            if (display) display.textContent = '25:00';
            const emotion = State.get('buddy.emotion') || 'idle';
            if (avatar) {
                avatar.textContent = EMOTION_EMOJIS[emotion] || '😊';
                avatar.className = `buddy-card-avatar emotion-${emotion}`;
            }
        }
    },

    startStudyTimer() {
        this.studyTimer = setInterval(() => {
            if (!this.studyStartTime) return;
            const elapsed = Math.floor((Date.now() - this.studyStartTime) / 1000);
            const remaining = Math.max(0, 25 * 60 - elapsed);
            const m = String(Math.floor(remaining / 60)).padStart(2, '0');
            const s = String(remaining % 60).padStart(2, '0');
            const display = document.getElementById('timer-display');
            if (display) display.textContent = `${m}:${s}`;

            if (remaining === 0) {
                clearInterval(this.studyTimer);
                this.toggleStudy();
                this.showToast('番茄钟完成！休息一下吧~');
            }
        }, 1000);
    },

    // ==================== 日记 ====================

    selectEmotion(level) {
        this.selectedEmotionLevel = level;
        document.querySelectorAll('.emotion-option').forEach(el => {
            el.classList.toggle('selected', parseInt(el.dataset.level) === level);
        });
    },

    selectFeeling(el) {
        document.querySelectorAll('.feeling-tag').forEach(t => t.classList.remove('selected'));
        el.classList.add('selected');
        this.selectedFeeling = el.textContent;
    },

    async saveDiary() {
        const event = document.getElementById('diary-event')?.value.trim();
        const words = document.getElementById('diary-words')?.value.trim();

        try {
            const res = await API.saveDiary({
                emotion_level: this.selectedEmotionLevel,
                study_feeling: this.selectedFeeling,
                biggest_event: event,
                words_to_buddy: words,
            });

            if (res.success) {
                this.showToast('日记已保存~');
                if (document.getElementById('diary-event')) document.getElementById('diary-event').value = '';
                if (document.getElementById('diary-words')) document.getElementById('diary-words').value = '';
                await this.loadGlobalData();
            }
        } catch (e) {
            this.showToast('保存失败，请重试');
        }
    },

    // ==================== 设置 ====================

    selectGoal(el) {
        document.querySelectorAll('.goal-option').forEach(o => o.classList.remove('selected'));
        el.classList.add('selected');
        this.selectedGoalHours = parseInt(el.dataset.hours);
    },

    async saveProfile() {
        const name = document.getElementById('setup-name')?.value.trim();
        const school = document.getElementById('setup-school')?.value.trim();
        const major = document.getElementById('setup-major')?.value.trim();
        const score = document.getElementById('setup-score')?.value.trim();
        const examDate = document.getElementById('setup-exam-date')?.value;

        if (!school || !major) {
            this.showToast('请填写目标院校和专业~');
            return;
        }

        try {
            const res = await API.updateBuddyProfile({
                name,
                target_school: school,
                target_major: major,
                target_score: parseInt(score) || 0,
                exam_date: examDate,
                daily_goal_hours: this.selectedGoalHours,
            });

            if (res.success) {
                this.showToast('设置已保存！');
                State.update({
                    'profile.name': name,
                    'profile.targetSchool': school,
                    'profile.targetMajor': major,
                });
                this.updateGreeting();
                await this.loadGlobalData();
                router.navigate('home');
            }
        } catch (e) {
            this.showToast('保存失败');
        }
    },

    // ==================== 任务 ====================

    taskPriority: 'medium',

    showAddTask() {
        document.getElementById('task-overlay')?.classList.add('visible');
        const titleInput = document.getElementById('task-title');
        if (titleInput) {
            titleInput.value = '';
            titleInput.focus();
        }
    },

    hideAddTask() {
        document.getElementById('task-overlay')?.classList.remove('visible');
    },

    selectTaskPriority(el) {
        document.querySelectorAll('#task-overlay .feeling-tag').forEach(btn => btn.classList.remove('selected'));
        el.classList.add('selected');
        this.taskPriority = el.dataset.priority;
    },

    async addTask() {
        const title = document.getElementById('task-title')?.value.trim();
        const subject = document.getElementById('task-subject')?.value;

        if (!title) {
            this.showToast('请输入任务名称');
            return;
        }

        try {
            await API.addTask({ title, subject, priority: this.taskPriority });
            this.hideAddTask();
            this.showToast('任务添加成功');
            if (window.tasksPageInstance) {
                window.tasksPageInstance.refresh();
            }
        } catch (e) {
            this.showToast('添加失败，请重试');
        }
    },

    async toggleTask(taskId, completed) {
        try {
            await API.completeTask(taskId);
            if (window.tasksPageInstance) {
                window.tasksPageInstance.refresh();
            }
        } catch (e) {
            this.showToast('操作失败');
        }
    },

    async deleteTask(taskId) {
        if (!confirm('确定要删除这个任务吗？')) return;
        try {
            await API.deleteTask(taskId);
            this.showToast('任务已删除');
            if (window.tasksPageInstance) {
                window.tasksPageInstance.refresh();
            }
        } catch (e) {
            this.showToast('删除失败');
        }
    },

    // ==================== 计划 ====================

    showCreatePlan() {
        document.getElementById('plan-overlay')?.classList.add('visible');
        const titleInput = document.getElementById('plan-title');
        if (titleInput) {
            titleInput.value = '';
            titleInput.focus();
        }
    },

    hideCreatePlan() {
        document.getElementById('plan-overlay')?.classList.remove('visible');
    },

    async createPlan() {
        const subject = document.getElementById('plan-title')?.value.trim();
        const duration = parseInt(document.getElementById('plan-duration')?.value) || 30;

        if (!subject) {
            this.showToast('请输入计划名称');
            return;
        }

        try {
            const examDate = new Date();
            examDate.setDate(examDate.getDate() + duration);
            const examDateStr = examDate.toISOString().split('T')[0];

            await API.createStudyPlan({
                subject: subject,
                exam_date: examDateStr,
                daily_hours: parseInt(document.getElementById('plan-hours')?.value) || 8,
                use_ai: false
            });
            this.hideCreatePlan();
            this.showToast('计划创建成功');
            if (window.plansPageInstance) {
                window.plansPageInstance.refresh();
            }
        } catch (e) {
            this.showToast('创建失败，请重试');
        }
    },

    // ==================== 成就 ====================

    showAchievements() {
        router.navigate('achievements');
    },

    showAchievement(data) {
        document.getElementById('achievement-icon').textContent = data.icon || '🏆';
        document.getElementById('achievement-name').textContent = data.name || '成就';
        document.getElementById('achievement-desc').textContent = data.description || '';
        document.getElementById('achievement-reward').textContent = `+${data.reward || 0} 积分`;
        document.getElementById('achievement-overlay').classList.add('visible');
    },

    closeAchievement() {
        document.getElementById('achievement-overlay').classList.remove('visible');
    },

    _updateNavHighlight(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });
    },
};

// 挂载到全局
window.App = App;

// 应用启动
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
