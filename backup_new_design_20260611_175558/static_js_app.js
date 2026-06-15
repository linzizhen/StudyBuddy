/**
 * StudyPal 应用主入口 v3.1
 * 现代化应用界面
 */

const App = {
    currentPage: 'home',
    isStudying: false,
    studyTimer: null,
    studyStartTime: null,
    currentSubject: '数学',
    timerSeconds: 25 * 60,
    timerDuration: 25 * 60,
    selectedEmotionLevel: 3,
    user: null,
    token: null,
    roles: [],
    currentRole: null,
    dailyGoalHours: 8,
    data: {},
    currentModel: null,
    currentModelMode: 'default',
    customBuddyEmoji: '\u{1F916}',
    tasks: [],
    _currentTheme: 'light',
    _activeStreamController: null, // 当前流式请求的 AbortController
    _buddyDesignerInitialized: false,
    _diaryReady: false,
    _pageHistory: ['home'],

    async init() {
        // SPA 模式检测：index.html 有 .page 元素
        this._isSPA = !!document.querySelector('.page');

        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');

        this.applyTheme(localStorage.getItem('theme') || 'light');

        // null / 空字符串 / "null" 字符串都视为未登录
        if (!this.token || this.token === 'null' || this.token === 'undefined') {
            window.location.href = '/login';
            return;
        }

        this.updateGreeting();
        await this.loadData();
        this._hideLoading();

        // SPA 模式下注册路由
        if (this._isSPA) {
            this._initRouter();
            this._routerReady = true;
        }

        if (this._isSPA) {
            this.initNav();
            this.initChat();
        }
        this.initTimer();
        this.initTasks();
        this.initSettings();
        this.initBuddyDesigner();

        // DiaryApp 在路由切换到日记页时动态初始化，不在此处调用
        // 防止 SPA 模式下重复初始化

        setTimeout(() => this.updateGreeting(), 60000);

        if (window.__splashStartTime) {
            var elapsed = Date.now() - window.__splashStartTime;
            var delay = Math.max(0, 1500 - elapsed);
            setTimeout(function() {
                var evt = new Event('app-ready');
                window.dispatchEvent(evt);
            }, delay);
        }
    },

    _initRouter() {
        if (!window.router) { return; }

        // 预缓存所有页面元素，减少重复 DOM 查询
        const _pageCache = {};
        const getPage = (name) => {
            if (!_pageCache[name]) {
                _pageCache[name] = document.getElementById('page-' + name);
            }
            return _pageCache[name];
        };

        const register = (name, page) => {
            router.register(name, {
                mount: () => {
                    // 一次性隐藏所有页面（仅在首次执行一次）
                    if (!getPage._allHidden) {
                        document.querySelectorAll('.page').forEach(p => {
                            p.style.display = 'none';
                            p.classList.remove('active');
                        });
                        getPage._allHidden = true;
                    }
                    const el = getPage(name);
                    if (el) {
                        el.style.display = '';
                        el.classList.add('active');
                    }
                    window.App.currentPage = name;
                },
                unmount: () => {
                    const el = getPage(name);
                    if (el) {
                        el.classList.remove('active');
                    }
                }
            });
        };

        // 注册所有页面
        register('home', 'home');
        register('chat', 'chat');
        register('tasks', 'tasks');
        register('settings', 'settings');
        register('insights', 'insights');
        register('achievements', 'achievements');
        register('memory', 'memory');
        register('plans', 'plans');

        // 日记页单独注册，mount 时初始化 DiaryApp
        router.register('diary', {
            mount: () => {
                document.querySelectorAll('.page').forEach(p => {
                    p.style.display = 'none';
                    p.classList.remove('active');
                });
                const el = getPage('diary');
                if (el) {
                    el.style.display = '';
                    el.classList.add('active');
                }
                window.App.currentPage = 'diary';
                // 动态初始化 DiaryApp（仅首次）
                if (!window.diaryApp) {
                    window.diaryApp = new DiaryApp();
                }
            },
            unmount: () => {
                const el = getPage('diary');
                if (el) el.classList.remove('active');
            }
        });

        // 初始化路由（load 时自动导航到正确页面）
        router.navigate('home');
    },

    _hideLoading() {
        const loadingEl = document.getElementById('app-loading');
        if (loadingEl) {
            loadingEl.classList.add('hidden');
            setTimeout(() => loadingEl.style.display = 'none', 300);
        }
    },

    async loadData() {
        const promises = [];

        promises.push(
            fetch('/api/buddy/status', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            }).then(res => res.ok ? res.json() : null).catch(() => null)
        );

        promises.push(
            fetch('/api/home', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            }).then(res => res.ok ? res.json() : null).catch(() => null)
        );

        promises.push(
            fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            }).then(res => res.ok ? res.json() : null).catch(() => null)
        );

        try {
            const results = await Promise.all(promises);

            const statusData = results[0];
            if (statusData?.success) this.data = statusData.status || {};

            const homeData = results[1];
            if (homeData?.success) this.data = { ...this.data, ...homeData.data };

            const userData = results[2];
            if (userData?.success) {
                this.user = userData.user;
                localStorage.setItem('user', JSON.stringify(this.user));
            }

            this.renderAll();
        } catch (e) {
            console.warn('加载数据失败，继续初始化页面', e);
            // 即使数据加载失败，也继续初始化页面功能
        }
    },

    renderAll() {
        try { this.renderBuddy(); } catch(e) { console.warn('renderBuddy error:', e); }
        try { this.renderStats(); } catch(e) { console.warn('renderStats error:', e); }
        try { this.renderProfile(); } catch(e) { console.warn('renderProfile error:', e); }
        try { this.renderGoal(); } catch(e) { console.warn('renderGoal error:', e); }
    },

    initNav() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                this.navigate(page);
            });
        });
    },

    navigate(page) {
        if (!this._isSPA) {
            window.location.href = '/' + page;
            return;
        }
        if (window.router && window.router.routes.has(page)) {
            router.navigate(page);
        } else {
            window.location.href = '/' + page;
        }
    },

    goBack() {
        window.history.back();
    },

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
        if (nameEl) nameEl.textContent = this.user?.nickname || '学习战士';
    },

    renderBuddy() {
        const buddy = this.data.buddy || {};
        const name = buddy.name || '小豆';
        const emoji = buddy.emoji || '\u{1F338}';
        const emotionText = buddy.emotion_desc || '心情不错~';

        const nameEl = document.getElementById('buddy-name');
        if (nameEl) nameEl.textContent = name;

        const avatarEl = document.getElementById('buddy-avatar');
        if (avatarEl) {
            const emojiOrUrl = buddy.emoji || '\u{1F338}';
            if (emojiOrUrl.startsWith('/') || emojiOrUrl.startsWith('http')) {
                avatarEl.innerHTML = `<img src="${emojiOrUrl}" alt="搭子" style="width:100%;height:100%;border-radius:inherit;object-fit:cover;">`;
            } else {
                avatarEl.innerHTML = emojiOrUrl;
            }
        }

        const emotionTextEl = document.getElementById('buddy-emotion-text');
        if (emotionTextEl) emotionTextEl.textContent = emotionText;

        const msgEl = document.getElementById('buddy-msg');
        if (msgEl) msgEl.textContent = this._getDefaultMessage();

        // chat.html 中使用 #chat-buddy-avatar-2 和 #chat-buddy-name-2
        const chatAvatarEl = document.getElementById('chat-buddy-avatar-2');
        if (chatAvatarEl) chatAvatarEl.innerHTML = emoji;

        const chatNameEl = document.getElementById('chat-buddy-name-2');
        if (chatNameEl) chatNameEl.textContent = name;

        const chatEmotionEl = document.getElementById('chat-emotion-desc');
        if (chatEmotionEl) chatEmotionEl.innerHTML = `<span class="db-buddy-status-dot online" id="buddy-status-dot"></span><span id="buddy-status-text">${emotionText}</span>`;

        // 显示当前 AI 模型
        const modelBadge = document.getElementById('chat-model-badge');
        if (modelBadge) {
            const aiModel = this.data.buddy?.ai_model;
            if (aiModel?.name) {
                const shortName = aiModel.name.length > 20 ? aiModel.name.substring(0, 18) + '…' : aiModel.name;
                modelBadge.textContent = '⚡ ' + shortName;
                modelBadge.style.display = '';
            } else {
                modelBadge.style.display = 'none';
            }
        }

        const dsEmptyAvatar = document.getElementById('ds-empty-avatar');
        if (dsEmptyAvatar) dsEmptyAvatar.textContent = emoji;
        const dsEmptyName = document.getElementById('ds-empty-name');
        if (dsEmptyName) dsEmptyName.textContent = name;
    },

    _getDefaultMessage() {
        const hour = new Date().getHours();
        if (hour >= 22 || hour < 6) return '夜深了，早点休息哦~';
        const todayHours = this.data.study?.today_hours || 0;
        if (todayHours > 0) return `今天学了 ${todayHours.toFixed(1)} 小时，继续加油！`;
        return '今天想学点什么？';
    },

    startChat() {
        this.navigate('chat');
    },

    newChat() {
        // 清空聊天记录并刷新页面
        const container = document.getElementById('chat-messages');
        if (container) container.innerHTML = `
            <div class="db-empty" id="chat-empty">
                <div class="db-empty-avatar" id="ds-empty-avatar">&#128150;</div>
                <div class="db-empty-name" id="ds-empty-name">小豆</div>
                <div class="db-empty-tagline">我是你的学习搭子，随时陪你聊聊学习和生活</div>
                <div class="db-empty-suggestions" id="chat-suggestions"></div>
            </div>
            <div class="db-model-guide" id="chat-model-guide">
                <div class="db-model-guide-icon">&#9888;</div>
                <div class="db-model-guide-title">搭子暂时离线</div>
                <div class="db-model-guide-desc">需要先配置 AI 模型，搭子才能上线陪你聊天</div>
                <div class="db-model-guide-steps">
                    <div class="db-model-guide-step">
                        <span class="db-model-guide-num">1</span><span>打开设置页面</span>
                    </div>
                    <div class="db-model-guide-step">
                        <span class="db-model-guide-num">2</span><span>找到「AI 模型配置」</span>
                    </div>
                    <div class="db-model-guide-step">
                        <span class="db-model-guide-num">3</span><span>填写 API 地址和 Key</span>
                    </div>
                </div>
                <button class="db-model-guide-btn" onclick="openModelGuide()">&#9889; 立即配置 AI 模型</button>
                <div class="db-model-guide-hint">推荐使用 <strong>Groq</strong>（免费）或 <strong>DeepSeek</strong>（便宜）</div>
            </div>
        `;
        const input = document.getElementById('chat-input');
        if (input) { input.value = ''; input.style.height = 'auto'; }
        const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
        this._setBuddyStatus('online', emotionText);
        // 重新检测模型配置
        setTimeout(() => { if (window._checkModelConfig) window._checkModelConfig(); }, 50);
    },

    loadChat(id) {
        // 加载指定会话记录
        this.newChat();
        // 关闭移动端侧边栏
        const sidebar = document.getElementById('db-sidebar');
        if (sidebar) sidebar.classList.remove('open');
        const overlay = document.getElementById('db-sidebar-overlay');
        if (overlay) overlay.classList.remove('open');
    },

    toggleSidebar() {
        const sidebar = document.getElementById('db-sidebar');
        const overlay = document.getElementById('db-sidebar-overlay');
        if (sidebar) sidebar.classList.toggle('open');
        if (overlay) overlay.classList.toggle('open');
    },

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

        const goalPctEl = document.getElementById('goal-percent');
        if (goalPctEl) goalPctEl.textContent = progress + '%';

        const progressBarEl = document.getElementById('today-progress-bar');
        if (progressBarEl) progressBarEl.style.width = progress + '%';

        const streakEl = document.getElementById('streak-num');
        if (streakEl) streakEl.textContent = streak;
    },

    renderProfile() {
        const nameEl = document.getElementById('settings-name');
        if (nameEl) nameEl.textContent = this.user?.nickname || '学习战士';

        const emailEl = document.getElementById('settings-email');
        if (emailEl) emailEl.textContent = this.user?.email || '';

        const avatarEl = document.getElementById('settings-avatar');
        if (avatarEl) {
            const avatar = this.user?.avatar;
            if (avatar && (avatar.startsWith('/') || avatar.startsWith('http'))) {
                avatarEl.innerHTML = `<img src="${avatar}" alt="头像" style="width:100%;height:100%;border-radius:inherit;object-fit:cover;">`;
                avatarEl.style.background = 'transparent';
            } else {
                avatarEl.innerHTML = avatar || '\u{1F464}';
                avatarEl.style.background = '';
            }
        }

        const goalHoursEl = document.getElementById('goal-hours-val');
        if (goalHoursEl) goalHoursEl.textContent = this.user?.daily_goal_hours || 8;

        const currentRoleEl = document.getElementById('current-role-name');
        if (currentRoleEl) currentRoleEl.textContent = this.currentRole?.name || this.data.buddy?.name || '小豆';

        const goalDescEl = document.getElementById('settings-goal-desc');
        const school = this.user?.target_school;
        const major = this.user?.target_major;
        if (goalDescEl) {
            goalDescEl.textContent = school && major ? `${school} · ${major}` : '设置目标院校和专业';
        }
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

    initTimer() {
        document.querySelectorAll('.bento-timer-preset-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.bento-timer-preset-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const minutes = parseInt(btn.dataset.minutes);
                if (this.studyTimer) {
                    this.stopTimer();
                }
                this.timerDuration = minutes * 60;
                this.timerSeconds = this.timerDuration;
                this.updateTimerDisplay();
            });
        });
        document.querySelectorAll('.bento-subject-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.bento-subject-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                this.currentSubject = chip.dataset.subject;
                const tagEl = document.getElementById('timer-subject-tag');
                if (tagEl) tagEl.textContent = '\u{1F4DA} ' + this.currentSubject;
            });
        });
    },

    setTimerDuration(minutes) {
        if (this.studyTimer) {
            this.stopTimer();
        }
        this.timerDuration = minutes * 60;
        this.timerSeconds = this.timerDuration;
        this.updateTimerDisplay();
        document.querySelectorAll('.bento-timer-preset-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.minutes) === minutes);
        });
    },

    showCustomTimer() {
        const val = prompt('输入番茄钟时长（分钟，5-120之间）:', '25');
        if (val === null) return;
        const minutes = parseInt(val);
        if (isNaN(minutes) || minutes < 5 || minutes > 120) {
            this.showToast('请输入 5-120 之间的数字');
            return;
        }
        this.setTimerDuration(minutes);
        this.showToast(`已设为 ${minutes} 分钟`);
    },

    toggleStudy() {
        const card = document.getElementById('study-timer-card');
        if (!card) return;
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
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

        const btnText = document.getElementById('timer-btn-text');
        if (btnText) btnText.textContent = '\u{25A0}\u{25A0} 暂停';
    },

    stopTimer() {
        clearInterval(this.studyTimer);
        this.studyTimer = null;
        const btnText = document.getElementById('timer-btn-text');
        if (btnText) btnText.textContent = '\u{25B6} 继续';
    },

    timerComplete() {
        clearInterval(this.studyTimer);
        this.studyTimer = null;
        this.timerSeconds = this.timerDuration;
        this.showToast('\u{1F38A} 番茄完成！休息一下吧~');

        const duration = this.timerDuration / 60;
        this._recordSession(duration);

        this.updateTimerDisplay();
        const btnText = document.getElementById('timer-btn-text');
        if (btnText) btnText.textContent = '\u{25B6} 再来一个';
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
        } catch (e) {}
    },

    updateTimerDisplay() {
        const minutes = Math.floor(this.timerSeconds / 60);
        const seconds = this.timerSeconds % 60;
        const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        const displayEl = document.getElementById('timer-display');
        if (displayEl) displayEl.textContent = timeStr;

        const ringEl = document.getElementById('timer-ring');
        if (ringEl) {
            const circumference = 502.65;
            const progress = 1 - (this.timerSeconds / this.timerDuration);
            ringEl.style.strokeDashoffset = circumference * (1 - progress);
        }
    },

    initChat() {
        const input = document.getElementById('chat-input');
        if (input) {
            // Enter 发送，Shift+Enter 换行
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendChat();
                }
            });
            // 自动高度调整
            input.addEventListener('input', () => {
                input.style.height = 'auto';
                input.style.height = Math.min(input.scrollHeight, 120) + 'px';
            });
        }
        // 检测模型配置状态
        if (window._checkModelConfig) window._checkModelConfig();
    },

    loadChatHistory() {
        const container = document.getElementById('chat-messages');
        const emptyEl = document.getElementById('chat-empty');
        if (!container) return;
        if (emptyEl) emptyEl.style.display = 'none';
    },

    async sendChat() {
        const input = document.getElementById('chat-input');
        if (!input) return;
        const message = input.value.trim();
        if (!message) return;

        // 检查模型是否已配置（通过引导元素的显示状态判断）
        const guide = document.getElementById('chat-model-guide');
        if (guide && guide.classList.contains('visible')) {
            this.showToast('\u26A0 请先配置 AI 模型');
            return;
        }

        // 如果有正在进行的流式请求，先中止
        if (App._activeStreamController) {
            App._activeStreamController.abort();
            App._activeStreamController = null;
            this._removeStreamingBubble();
            this._hideTyping();
        }

        input.value = '';
        this._addChatBubble(message, 'user');
        this._scrollChat();

        const sendBtn = document.getElementById('btn-send');
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.classList.add('sending');
        }

        // 显示思考中状态（搭子正在组织语言）
        this._hideTyping();
        this._showTyping();
        let streamBubble = null;
        let streamReply = '';
        let hasReceivedToken = false;
        let isWaitingForReply = true;
        // 等待回复气泡的超时：5秒后如果还没收到任何 token，创建空气泡
        const replyTimeout = setTimeout(() => {
            if (isWaitingForReply) {
                hasReceivedToken = true;
                this._hideTyping();
                streamBubble = this._createStreamingBubble();
            }
        }, 5000);

        try {
            // 1. 优先使用后端流式代理（安全，API Key 不暴露）
            try {
                const streamRes = await fetch('/api/buddy/chat/stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({ message, conversation_id: '' })
                });

                    if (!streamRes.ok) {
                    clearTimeout(replyTimeout);
                    const errData = await streamRes.json().catch(() => ({}));
                    const limitMatch = errData.error && errData.error.includes('次数');
                    this._hideTyping();
                    this._addChatBubble(
                        limitMatch ? '本月AI次数用完啦，请明天再来或升级会员~' : ('抱歉，' + (errData.error || `请求失败 (${streamRes.status})`)),
                        'buddy'
                    );
                    this._setBuddyStatus('error', '请求失败');
                    setTimeout(() => {
                        const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                        this._setBuddyStatus('online', emotionText);
                    }, 3000);
                    if (sendBtn) {
                        sendBtn.disabled = false;
                        sendBtn.classList.remove('sending');
                    }
                    this._scrollChat();
                    return;
                }

                const reader = streamRes.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let finalError = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';
                    for (const line of lines) {
                        if (line.startsWith('event: done')) {
                            clearTimeout(replyTimeout);
                            streamReply = streamReply.trim().replace(/^[Tt]hinking [Pp]rocess[：:]\s*/gm, '').trim();
                            this._hideTyping();
                            if (streamReply) {
                                if (streamBubble) {
                                    this._finalizeStreamingBubble(streamBubble, streamReply);
                                } else {
                                    this._addChatBubble(streamReply, 'buddy');
                                    const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                                    this._setBuddyStatus('online', emotionText);
                                }
                                await this._postChatProcess(streamReply, message, '');
                            } else {
                                const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                                this._setBuddyStatus('online', emotionText);
                            }
                            this._scrollChat();
                            return;
                        }
                        if (line.startsWith('event: error')) {
                            const dataStr = line.replace('event: error\ndata: ', '').trim();
                            try { finalError = JSON.parse(dataStr).error || ''; } catch {}
                            continue;
                        }
                        if (!line.startsWith('data: ')) continue;
                        const dataStr = line.slice(6).trim();
                        if (!dataStr || dataStr === '{}') continue;
                        try {
                            const parsed = JSON.parse(dataStr);
                            if (parsed.token) {
                                clearTimeout(replyTimeout);
                                isWaitingForReply = false;
                                if (!hasReceivedToken) {
                                    hasReceivedToken = true;
                                    this._hideTyping();
                                    streamBubble = this._createStreamingBubble();
                                }
                                streamReply += parsed.token;
                                this._updateStreamingBubble(streamBubble, streamReply);
                            }
                        } catch {}
                    }
                }

                clearTimeout(replyTimeout);
                streamReply = streamReply.trim().replace(/^[Tt]hinking [Pp]rocess[：:]\s*/gm, '').trim();
                this._hideTyping();
                if (streamReply) {
                    if (streamBubble) {
                        this._finalizeStreamingBubble(streamBubble, streamReply);
                    } else {
                        this._addChatBubble(streamReply, 'buddy');
                        const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                        this._setBuddyStatus('online', emotionText);
                    }
                    await this._postChatProcess(streamReply, message, '');
                } else {
                    const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                    this._setBuddyStatus('online', emotionText);
                }
                this._scrollChat();
                if (finalError) throw new Error(finalError);

            } catch (streamErr) {
                // 后端流式失败，回退到浏览器直调
                clearTimeout(replyTimeout);
                this._hideTyping();
                streamReply = await this._browserDirectChat(message);
                if (streamReply) {
                    this._addChatBubble(streamReply, 'buddy');
                    await this._postChatProcess(streamReply, message, '');
                    const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                    this._setBuddyStatus('online', emotionText);
                }
            }

        } catch (e) {
            clearTimeout(replyTimeout);
            this._hideTyping();
            this._addChatBubble('网络连接不稳定，稍后再试试吧~', 'buddy');
            this._setBuddyStatus('error', '连接异常');
            setTimeout(() => {
                const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
                this._setBuddyStatus('online', emotionText);
            }, 3000);
        } finally {
            clearTimeout(replyTimeout);
            App._activeStreamController = null;
            this._hideTyping();
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.classList.remove('sending');
            }
            const inp = document.getElementById('chat-input');
            if (inp) { inp.value = ''; inp.style.height = 'auto'; }
            this._scrollChat();
        }
    },

    // 后端流式失败时的浏览器直调回退方案
    // 注意：调用方 sendChat 已经显示了 typing dots，这里只负责获取回复
    async _browserDirectChat(message) {
        try {
            // 并行获取模型配置、系统提示词、对话历史（提升回退速度）
            const [modelRes, promptRes] = await Promise.all([
                fetch('/api/ai-model/proxy/chat', {
                    method: 'GET',
                    headers: { 'Authorization': `Bearer ${this.token}` }
                }),
                fetch('/api/buddy/system-prompt', {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                })
            ]);

            const modelData = await modelRes.json();
            if (!modelData.success) return '';

            const promptData = await promptRes.json();
            if (!promptData.success) return '';

            // 获取对话历史
            const histRes = await fetch(`/api/buddy/history?conversation_id=${promptData.conversation_id || ''}`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const histData = await histRes.json();
            const history = histData.messages || [];

            const msgs = [{ role: 'system', content: promptData.system_prompt }];
            for (const msg of history.slice(-5)) {
                msgs.push({ role: msg.role, content: msg.content });
            }
            msgs.push({ role: 'user', content: message });

            let baseUrl = (modelData.base_url || '').replace(/\/+$/, '');
            if (baseUrl.endsWith('/v1')) baseUrl = baseUrl.slice(0, -3);
            const endpoints = [`${baseUrl}/v1/chat/completions`, `${baseUrl}/chat/completions`];

            let reply = '';
            let lastError = '';

            for (const endpoint of endpoints) {
                const controller = new AbortController();
                App._activeStreamController = controller;
                controller.signal.addEventListener('abort', () => {});

                try {
                    const aiRes = await this._fetchWithTimeout(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${modelData.api_key}`
                        },
                        body: JSON.stringify({
                            model: modelData.model,
                            messages: msgs,
                            max_tokens: 512,
                            thinking: null,
                            extra_body: { thinking: null, enable_thinking: false },
                            stream: true
                        }),
                        signal: controller.signal
                    }, 120000);

                    if (!aiRes.ok) {
                        if (aiRes.status === 404) continue;
                        lastError = `请求失败 (${aiRes.status})`;
                        break;
                    }

                    const reader = aiRes.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';
                    const thinkingPrefix = /^[Tt]hinking [Pp]rocess[：:]\s*/;

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        buffer = lines.pop() || '';
                        for (const line of lines) {
                            if (!line.startsWith('data: ')) continue;
                            const data = line.slice(6).trim();
                            if (data === '[DONE]') continue;
                            try {
                                const parsed = JSON.parse(data);
                                const delta = parsed.choices?.[0]?.delta?.content || '';
                                if (delta && !thinkingPrefix.test(delta)) {
                                    reply += delta.replace(thinkingPrefix, '');
                                }
                            } catch {}
                        }
                    }
                    break;
                } catch (e) {
                    lastError = e.name === 'AbortError' ? '' : (e.message || '连接失败');
                }
            }

            reply = reply.trim().replace(/^[Tt]hinking [Pp]rocess[：:]\s*/gm, '').trim();

            if (!reply && lastError) {
                this._addChatBubble('抱歉，' + lastError, 'buddy');
                return '';
            }

            return reply;

        } catch (e) {
            return '';
        }
    },

    // 消息发送后的后处理（保存历史+情绪分析+更新搭子）
    async _postChatProcess(reply, userMessage, convId) {
        try {
            // 保存对话历史
            const convId2 = convId || '';
            await fetch('/api/ai-model/proxy/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
                body: JSON.stringify({ role: 'user', content: userMessage, conversation_id: convId2 })
            });
            await fetch('/api/ai-model/proxy/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
                body: JSON.stringify({ role: 'assistant', content: reply, conversation_id: convId2 })
            });

            // 分析情绪
            const analyzeRes = await fetch('/api/buddy/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
                body: JSON.stringify({ message: userMessage, ai_reply: reply, conversation_id: convId2 })
            });
            const analyzeData = await analyzeRes.json();

            if (analyzeData.success) {
                const buddy = this.data.buddy || {};
                if (analyzeData.emotion) {
                    buddy.emotion = analyzeData.emotion;
                    buddy.emoji = analyzeData.emoji || buddy.emoji;
                    buddy.emotion_desc = analyzeData.emotion_desc || buddy.emotion_desc;
                    this.data.buddy = buddy;
                    this.renderBuddy();
                }
                if (analyzeData.suggestions && analyzeData.suggestions.length) {
                    this.showSuggestions(analyzeData.suggestions);
                }
            }
        } catch (e) { /* 静默失败，不影响用户体验 */ }
    },

    _addChatBubble(content, role) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const empty = document.getElementById('chat-empty');
        if (empty) empty.style.display = 'none';

        const buddy = this.data?.buddy || {};
        const avatar = role === 'buddy' ? (buddy.emoji || '\u{1F338}') : '我';
        const now = new Date();
        const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;

        const wrap = document.createElement('div');
        wrap.className = `db-msg ${role}`;
        wrap.innerHTML = `
            <div class="db-msg-avatar">${avatar}</div>
            <div class="db-msg-body">
                <div class="db-msg-bubble">${this._escapeHtml(content)}</div>
                <div class="db-msg-time">${time}</div>
            </div>
        `;
        container.appendChild(wrap);
    },

    async _fetchWithTimeout(url, options, timeoutMs = 120000) {
        return new Promise((resolve, reject) => {
            const timeoutId = setTimeout(() => {
                reject(new DOMException('Fetch timeout', 'AbortError'));
            }, timeoutMs);

            const controller = options?.signal;
            const onAbort = () => {
                clearTimeout(timeoutId);
                if (controller) controller.removeEventListener('abort', onAbort);
            };
            if (controller) controller.addEventListener('abort', onAbort);

            fetch(url, options)
                .then(res => {
                    clearTimeout(timeoutId);
                    if (controller) controller.removeEventListener('abort', onAbort);
                    resolve(res);
                })
                .catch(err => {
                    clearTimeout(timeoutId);
                    if (controller) controller.removeEventListener('abort', onAbort);
                    reject(err);
                });
        });
    },

    _showTyping() {
        const container = document.getElementById('chat-messages');
        if (!container) return null;

        const empty = document.getElementById('chat-empty');
        if (empty) empty.style.display = 'none';

        const buddyData = this.data?.buddy;
        const avatar = buddyData?.emoji || '\u{1F338}';

        const wrap = document.createElement('div');
        wrap.className = 'db-typing';
        wrap.id = 'chat-typing-indicator';
        wrap.innerHTML = `
            <div class="db-typing-avatar">${avatar}</div>
            <div class="db-typing-dots">
                <div class="db-typing-dots-row">
                    <span></span><span></span><span></span>
                </div>
                <div class="db-typing-label">正在思考...</div>
            </div>
        `;
        container.appendChild(wrap);
        this._scrollChat();
        this._setBuddyStatus('thinking', '正在思考...');
        return wrap;
    },

    _createStreamingBubble() {
        const container = document.getElementById('chat-messages');
        if (!container) return null;

        const buddyData = this.data?.buddy;
        const avatar = buddyData?.emoji || '\u{1F338}';
        const now = new Date();
        const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;

        const wrap = document.createElement('div');
        wrap.className = 'db-msg buddy streaming';
        wrap.id = 'streaming-bubble';
        wrap.innerHTML = `
            <div class="db-msg-avatar">${avatar}</div>
            <div class="db-msg-body">
                <div class="db-msg-bubble" id="streaming-bubble-content"></div>
                <div class="db-typing-progress" id="streaming-progress">
                    <div class="db-typing-progress-bar">
                        <div class="db-typing-progress-fill" id="streaming-progress-fill" style="width:0%"></div>
                    </div>
                    <span id="streaming-char-count">0 字</span>
                </div>
                <div class="db-msg-time streaming-time">${time} <span class="typing-cursor">|</span></div>
            </div>
        `;
        container.appendChild(wrap);
        this._setBuddyStatus('speaking', '正在回复...');

        return {
            el: wrap,
            contentEl: document.getElementById('streaming-bubble-content'),
            progressFill: document.getElementById('streaming-progress-fill'),
            charCount: document.getElementById('streaming-char-count'),
            _charCount: 0
        };
    },

    _updateStreamingBubble(streamBubble, text) {
        if (!streamBubble || !streamBubble.contentEl) return;
        streamBubble.contentEl.innerHTML = this._escapeHtml(text).replace(/\n/g, '<br>');
        // 更新字符计数
        const charLen = text.length;
        if (streamBubble.charCount) {
            streamBubble.charCount.textContent = charLen + ' 字';
        }
        this._scrollChat();
    },

    _finalizeStreamingBubble(streamBubble, text) {
        if (!streamBubble || !streamBubble.el) return;
        streamBubble.el.classList.remove('streaming');
        if (streamBubble.contentEl) {
            streamBubble.contentEl.innerHTML = this._escapeHtml(text).replace(/\n/g, '<br>');
        }
        const cursor = streamBubble.el.querySelector('.typing-cursor');
        if (cursor) cursor.remove();
        const progress = streamBubble.el.querySelector('.db-typing-progress');
        if (progress) progress.style.display = 'none';
        // 回复完成后恢复搭子状态
        const emotionText = this.data?.buddy?.emotion_desc || '随时待命';
        this._setBuddyStatus('online', emotionText);
    },

    _removeStreamingBubble() {
        const el = document.getElementById('streaming-bubble');
        if (el) el.remove();
    },

    _hideTyping() {
        const el = document.getElementById('chat-typing-indicator');
        if (el) el.remove();
    },

    _setBuddyStatus(status, text) {
        const dot = document.getElementById('buddy-status-dot');
        const textEl = document.getElementById('buddy-status-text');
        if (dot) {
            dot.className = 'db-buddy-status-dot ' + status;
        }
        if (textEl) {
            textEl.textContent = text;
        }
    },

    showSuggestions(suggestions) {
        const container = document.getElementById('chat-suggestions');
        if (!container || !suggestions || !suggestions.length) return;
        container.innerHTML = suggestions.map(s =>
            `<button class="db-suggestion-btn" onclick="App.sendSuggestion('${s.replace(/'/g, "\\'")}')">${s}</button>`
        ).join('');
    },

    async sendSuggestion(text) {
        const input = document.getElementById('chat-input');
        if (input) input.value = text;
        const container = document.getElementById('chat-suggestions');
        if (container) container.innerHTML = '';
        await this.sendChat();
    },

    _scrollChat() {
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
                     onclick="App.selectRole('${role.id}')">
                    <div class="role-item-avatar" style="background:linear-gradient(135deg, ${role.color || '#FDE68A'}33, ${role.color || '#FCD34D'}22);">
                        ${role.emoji}
                    </div>
                    <div class="role-item-info">
                        <div class="role-item-name">${this._escapeHtml(role.name)}</div>
                        <div class="role-item-desc">${this._escapeHtml(role.personality || role.description || '')}</div>
                    </div>
                    ${role.id === this.currentRole?.id ? '<div class="role-item-check">\u2713</div>' : ''}
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
                if (!this.data.buddy) this.data.buddy = {};
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

    initDiary() {
        const today = new Date();
        const dateEl = document.getElementById('diary-date');
        if (dateEl) {
            dateEl.textContent = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`;
        }

        // 情绪按钮
        document.querySelectorAll('.diary-emotion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.diary-emotion-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.selectedEmotionLevel = parseInt(btn.dataset.level);
            });
        });

        // 学习感受标签（单选）
        document.querySelectorAll('.diary-feeling-tag').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.classList.contains('active')) {
                    btn.classList.remove('active');
                    btn.dataset.selected = 'false';
                } else {
                    document.querySelectorAll('.diary-feeling-tag').forEach(b => { b.classList.remove('active'); b.dataset.selected = 'false'; });
                    btn.classList.add('active');
                    btn.dataset.selected = 'true';
                }
            });
        });

        // 天气按钮（单选）
        document.querySelectorAll('.diary-weather-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.classList.contains('active')) {
                    btn.classList.remove('active');
                    btn.dataset.selected = 'false';
                } else {
                    document.querySelectorAll('.diary-weather-btn').forEach(b => { b.classList.remove('active'); b.dataset.selected = 'false'; });
                    btn.classList.add('active');
                    btn.dataset.selected = 'true';
                }
            });
        });

        // 初始化完成后才允许交互，防止竞态
        this._diaryReady = false;

        // 加载今日日记（如果有），回填表单
        this._loadTodayDiary().then(() => {
            this._diaryReady = true;
        });

        // 加载历史日记（通过 DiaryPage）
        if (window.DiaryPage && window.DiaryPage.refresh) {
            window.DiaryPage.refresh();
        }
    },

    async _loadTodayDiary() {
        try {
            const res = await fetch('/api/diary/today', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success && data.entry) {
                const entry = data.entry;
                // 只在用户没有手动选择情绪时才回填
                if (this.selectedEmotionLevel === 3) {
                    this.selectedEmotionLevel = entry.emotion_level || 3;
                    document.querySelectorAll('.diary-emotion-btn').forEach(btn => {
                        btn.classList.toggle('active', parseInt(btn.dataset.level) === this.selectedEmotionLevel);
                    });
                }
                // 回填学习感受
                if (entry.study_feeling) {
                    document.querySelectorAll('.diary-feeling-tag').forEach(btn => {
                        const isActive = btn.dataset.feeling === entry.study_feeling;
                        btn.classList.toggle('active', isActive);
                        btn.dataset.selected = isActive ? 'true' : 'false';
                    });
                }
                // 回填今日大事
                const eventEl = document.getElementById('diary-biggest-event');
                if (eventEl) eventEl.value = entry.biggest_event || '';
                // 回填主文本
                const contentEl = document.getElementById('diary-content');
                if (contentEl) contentEl.value = entry.words_to_buddy || '';
                // 回填天气
                if (entry.weather) {
                    document.querySelectorAll('.diary-weather-btn').forEach(btn => {
                        const isActive = btn.dataset.weather === entry.weather;
                        btn.classList.toggle('active', isActive);
                        btn.dataset.selected = isActive ? 'true' : 'false';
                    });
                }
                // 显示已打卡提示
                const badge = document.getElementById('diary-checkin-badge');
                const btnText = document.getElementById('diary-save-btn-text');
                if (badge) {
                    const emojis = ['\u{1F622}', '\u{1F61F}', '\u{1F610}', '\u{1F642}', '\u{1F601}'];
                    badge.textContent = `今日\u2705 已打卡 ${emojis[(this.selectedEmotionLevel || 3) - 1]}`;
                    badge.style.display = '';
                }
                if (btnText) btnText.textContent = '更新日记';
            }
        } catch(e) {}
    },

    async saveDiary() {
        if (!this._diaryReady) {
            this.showToast('\u23f3 \u7b49\u5f85\u52a0\u8f7d\u5b8c\u6210...');
            return;
        }

        const content = document.getElementById('diary-content')?.value.trim();
        const biggestEvent = document.getElementById('diary-biggest-event')?.value.trim();

        if (!content && !biggestEvent) {
            this.showToast('\u2709 \u5199\u70b9\u4ec0\u4e48\u5427~');
            return;
        }

        // 收集学习感受
        const selectedFeeling = document.querySelector('.diary-feeling-tag[data-selected="true"]');
        const studyFeeling = selectedFeeling ? selectedFeeling.dataset.feeling : '';

        // 收集天气
        const selectedWeather = document.querySelector('.diary-weather-btn[data-selected="true"]');
        const weather = selectedWeather ? selectedWeather.dataset.weather : '';

        try {
            const res = await fetch('/api/diary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    words_to_buddy: content,
                    biggest_event: biggestEvent,
                    emotion_level: this.selectedEmotionLevel || 3,
                    emotion_label: ['\u{1F622}', '\u{1F61F}', '\u{1F610}', '\u{1F642}', '\u{1F601}'][(this.selectedEmotionLevel || 3) - 1],
                    study_feeling: studyFeeling,
                    weather: weather,
                    date: new Date().toISOString().split('T')[0]
                })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('\u2705 \u65e5\u8bb0\u5df2\u4fdd\u5b58~');
                // 保留表单内容（不清空），只更新打卡状态
                const badge = document.getElementById('diary-checkin-badge');
                if (badge) {
                    badge.textContent = '\u2705 \u4eca\u65e5\u5df2\u6253\u5361';
                    badge.style.display = '';
                }
                const btnText = document.getElementById('diary-save-btn-text');
                if (btnText) btnText.textContent = '\u66f4\u65b0\u65e5\u8bb0';
                // 刷新情绪日历和历史列表
                if (window.DiaryPage && window.DiaryPage.refresh) {
                    window.DiaryPage.refresh();
                }
                this.loadDiaries();
            } else {
                this.showToast(data.error || '\u4fdd\u5b58\u5931\u8d25');
            }
        } catch (e) {
            this.showToast('\u4fdd\u5b58\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5');
        }
    },

    async loadDiaries() {
        // 历史日记已由 DiaryPage 统一加载渲染，此处仅保留用于其他场景
        // 如需刷新，手动调用 DiaryPage.refresh()
    },

    renderDiaryList(diaries) {
        const el = document.getElementById('diary-history');
        if (!el) return;

        if (!diaries.length) {
            el.innerHTML = `
                <div class="diary-empty-state">
                    <div class="diary-empty-icon">&#128221;</div>
                    <div class="diary-empty-title">还没有日记</div>
                    <div class="diary-empty-desc">记录每天的心情，搭子会帮你分析</div>
                </div>`;
            return;
        }

        const getEmoji = (level) => ['\u{1F622}', '\u{1F61F}', '\u{1F610}', '\u{1F642}', '\u{1F601}'][level - 1] || '\u{1F610}';
        const getLabel = (level) => {
            const labels = ['\u{1F622}\u96BE\u53D7', '\u{1F61F}\u6709\u70B9\u4E27', '\u{1F610}\u4E00\u822C', '\u{1F642}\u8FD8\u597D', '\u{1F601}\u5F88\u5F00\u5FC3'];
            return labels[level - 1] || '\u{1F610}\u4E00\u822C';
        };

        el.innerHTML = `
            <div class="diary-history-header-row">
                <span class="diary-history-count">共 ${diaries.length} 篇</span>
            </div>
            ${diaries.map(d => {
                const emoji = getEmoji(d.emotion_level);
                const displayEmoji = d.custom_emotion_image
                    ? `<img src="${d.custom_emotion_image}" class="diary-entry-emoji-img" alt="情绪" style="width:18px;height:18px;border-radius:50%;object-fit:cover;">`
                    : emoji;
                return `
                <div class="diary-entry level-${d.emotion_level || 3}">
                    <div class="diary-entry-header">
                        <span class="diary-entry-date">${d.date}</span>
                        <span class="diary-entry-emotion">
                            <span>${displayEmoji}</span>
                            <span class="diary-entry-emotion-label">${getLabel(d.emotion_level)}</span>
                        </span>
                    </div>
                    ${d.study_feeling ? `<div class="diary-entry-tags"><span class="diary-entry-tag">${d.study_feeling}</span></div>` : ''}
                    ${d.biggest_event ? `<div class="diary-entry-event">&#128205; ${this._escapeHtml(d.biggest_event)}</div>` : ''}
                    ${d.words_to_buddy ? `<div class="diary-entry-content">${this._escapeHtml(d.words_to_buddy)}</div>` : ''}
                </div>`;
            }).join('')}
        `;
    },

    _getEmotionEmoji(level) {
        const map = { 1: '\u{1F622}', 2: '\u{1F61D}', 3: '\u{1F610}', 4: '\u{1F642}', 5: '\u{1F601}' };
        return map[level] || '\u{1F610}';
    },

    _formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return `${d.getMonth() + 1}月${d.getDate()}日`;
    },

    initTasks() {
        document.querySelectorAll('.task-filter-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.task-filter-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.renderTaskList(tab.dataset.filter);
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
                    <div class="empty-icon">\u{2610}</div>
                    <div class="empty-title">${filter === 'completed' ? '还没有完成的任务' : filter === 'pending' ? '待办已清空' : '任务空空'}</div>
                    <div class="empty-desc">点击下方按钮添加任务</div>
                </div>`;
            return;
        }

        container.innerHTML = tasks.map(t => `
            <div class="task-item ${t.status === 'completed' ? 'completed' : ''}" data-task-id="${t.id}" onclick="App.toggleTask('${t.id}')">
                <div class="task-check">${t.status === 'completed' ? '\u2713' : ''}</div>
                <div class="task-content">
                    <div class="task-title">${this._escapeHtml(t.title)}</div>
                    ${t.subject ? `<div class="task-meta">${this._escapeHtml(t.subject)}</div>` : ''}
                </div>
                <button class="task-delete-btn" onclick="event.stopPropagation(); App.deleteTask('${t.id}')" title="删除">&#10005;</button>
            </div>
        `).join('');
    },

    async toggleTask(taskId) {
        const task = (this.tasks || []).find(t => String(t.id) === String(taskId));
        if (!task) return;

        const newStatus = task.status === 'completed' ? 'pending' : 'completed';
        try {
            const res = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ completed: newStatus === 'completed' })
            });
            const data = await res.json();
            if (data.success) {
                task.status = newStatus;
                this.renderTaskList(document.querySelector('.task-filter-tab.active')?.dataset.filter || 'all');
                this.showToast(newStatus === 'completed' ? '\u2705 任务完成！' : '\u{1F504} 已取消完成');
            }
        } catch (e) {
            this.showToast('更新失败，请重试');
        }
    },

    async deleteTask(taskId) {
        if (!confirm('确定要删除这个任务吗？')) return;
        try {
            const res = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                this.tasks = (this.tasks || []).filter(t => String(t.id) !== String(taskId));
                this.renderTaskList(document.querySelector('.task-filter-tab.active')?.dataset.filter || 'all');
                this.showToast('任务已删除');
            }
        } catch (e) {
            this.showToast('删除失败，请重试');
        }
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
            } else {
                this.showToast(data.error || '添加失败');
            }
        });
    },

    initSettings() {},

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

    showGoalForm() {
        this.openModal('goal-modal');
        const schoolInput = document.getElementById('goal-school-input');
        const majorInput = document.getElementById('goal-major-input');
        const scoreInput = document.getElementById('goal-score-input');
        const dateInput = document.getElementById('goal-exam-date-input');
        const hoursRange = document.getElementById('goal-hours-range');
        const hoursDisplay = document.getElementById('goal-hours-display');

        if (schoolInput) schoolInput.value = this.user?.target_school || '';
        if (majorInput) majorInput.value = this.user?.target_major || '';
        if (scoreInput) scoreInput.value = this.user?.target_score || '';
        if (dateInput) dateInput.value = this.user?.exam_date || '';
        const hours = this.user?.daily_goal_hours || 8;
        if (hoursRange) hoursRange.value = hours;
        if (hoursDisplay) hoursDisplay.textContent = hours;

        if (hoursRange && hoursDisplay) {
            hoursRange.oninput = () => {
                hoursDisplay.textContent = hoursRange.value;
            };
        }
    },

    async saveGoalSettings() {
        const school = document.getElementById('goal-school-input')?.value.trim();
        const major = document.getElementById('goal-major-input')?.value.trim();
        const score = document.getElementById('goal-score-input')?.value;
        const examDate = document.getElementById('goal-exam-date-input')?.value;
        const goalHours = parseFloat(document.getElementById('goal-hours-range')?.value) || 8;

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
                    daily_goal_hours: goalHours
                })
            });
            const data = await res.json();
            if (data.success) {
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(this.user));
                this.renderGoal();
                this.renderStats();
                this.renderProfile();
                this.closeModal('goal-modal');
                this.showToast('\u2705 学习目标已保存！');
            } else {
                this.showToast(data.error || '保存失败');
            }
        } catch (e) {
            this.showToast('保存失败，请重试');
        }
    },

    showHoursSlider() {
        this.showGoalForm();
    },

    showExamDatePicker() {
        this.openModal('goal-modal');
        const dateInput = document.getElementById('goal-exam-date-input');
        if (dateInput) dateInput.focus();
    },

    applyTheme(theme) {
        this._currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        const iconEl = document.getElementById('theme-icon');
        if (iconEl) iconEl.innerHTML = theme === 'dark' ? '\u{2600}' : '\u{1F319}';
        const themeIcon = document.getElementById('theme-toggle-icon');
        if (themeIcon) themeIcon.innerHTML = theme === 'dark' ? '\u{2600}' : '\u{1F319}';
        const themeIcon2 = document.getElementById('theme-toggle-icon2');
        if (themeIcon2) themeIcon2.innerHTML = theme === 'dark' ? '\u{2600}' : '\u{1F319}';
        const switchEl = document.getElementById('theme-toggle-switch');
        if (switchEl) switchEl.classList.toggle('active', theme === 'dark');
    },

    toggleTheme() {
        const newTheme = this._currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.showToast(newTheme === 'dark' ? '深色模式已开启' : '浅色模式已开启');
    },

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

    closeRoleModal() { this.closeModal('role-modal'); },
    closeAchievement() { this.closeModal('achievement-modal'); },
    closeModelModal() { this.closeModal('model-modal'); },

    openModelModal() { this.openModal('chat-model-modal'); this.loadChatModelPresets(); },
    closeChatModelModal() { this.closeModal('chat-model-modal'); },

    async loadChatModelPresets() {
        try {
            const res = await fetch('/api/ai-model/presets');
            const data = await res.json();
            if (!data.success) return;
            const container = document.getElementById('chat-model-presets');
            if (!container) return;
            // 只显示推荐的免费模型
            const presets = (data.presets || []).filter(p =>
                ['groq_llama', 'groq_mixtral', 'deepseek_chat', 'deepseek_r1'].includes(p.key)
            );
            if (!presets.length) return;
            container.innerHTML = presets.map(p => `
                <div class="chat-model-preset-item" data-key="${p.key}" data-url="${p.base_url}" data-model="${p.model}" onclick="App.selectChatPreset(this)">
                    <div class="chat-model-preset-icon">${_getPresetIcon(p.provider)}</div>
                    <div class="chat-model-preset-info">
                        <div class="chat-model-preset-name">${p.name}</div>
                        <div class="chat-model-preset-desc">${p.provider === 'ollama' ? '本地部署' : 'API 调用'}</div>
                    </div>
                    <div class="chat-model-preset-check"></div>
                </div>
            `).join('');
        } catch (e) {}
    },

    selectChatPreset(el) {
        document.querySelectorAll('.chat-model-preset-item').forEach(item => item.classList.remove('selected'));
        el.classList.add('selected');
        // 填充表单
        const urlInput = document.getElementById('chat-custom-model-url');
        const modelInput = document.getElementById('chat-custom-model-name2');
        const nameInput = document.getElementById('chat-custom-model-name');
        if (urlInput) urlInput.value = el.dataset.url || '';
        if (modelInput) modelInput.value = el.dataset.model || '';
        if (nameInput) nameInput.value = el.querySelector('.chat-model-preset-name').textContent;
        // 清空 Key（用户需要自己填）
        const keyInput = document.getElementById('chat-custom-model-key');
        if (keyInput) keyInput.value = '';
        const resultEl = document.getElementById('chat-test-result');
        if (resultEl) { resultEl.className = 'model-test-result'; resultEl.textContent = ''; }
    },

    async testChatModel() {
        const baseUrl = document.getElementById('chat-custom-model-url')?.value.trim();
        const apiKey = document.getElementById('chat-custom-model-key')?.value.trim();
        const model = document.getElementById('chat-custom-model-name2')?.value.trim();
        const resultEl = document.getElementById('chat-test-result');
        const btn = document.getElementById('chat-test-model-btn');
        if (!this.token) {
            if (resultEl) { resultEl.className = 'model-test-result error show'; resultEl.textContent = '\u274C 登录已过期'; }
            return;
        }
        if (!baseUrl || !apiKey || !model) {
            if (resultEl) { resultEl.className = 'model-test-result error show'; resultEl.textContent = '\u274C 请填写 API 地址、Key 和模型名称'; }
            return;
        }
        if (resultEl) { resultEl.className = 'model-test-result loading show'; resultEl.textContent = '\u23F3 测试连接中...'; }
        if (btn) btn.disabled = true;
        try {
            const res = await fetch('/api/ai-model/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
                body: JSON.stringify({ base_url: baseUrl, api_key: apiKey, model })
            });
            const data = await res.json();
            if (data.success) {
                if (resultEl) { resultEl.className = 'model-test-result success show'; resultEl.textContent = '\u2705 连接成功！可以保存了'; }
            } else {
                if (resultEl) { resultEl.className = 'model-test-result error show'; resultEl.textContent = '\u274C ' + (data.error || '连接失败'); }
            }
        } catch (e) {
            if (resultEl) { resultEl.className = 'model-test-result error show'; resultEl.textContent = '\u274C 网络错误'; }
        } finally {
            if (btn) btn.disabled = false;
        }
    },

    async saveChatModel() {
        const name = document.getElementById('chat-custom-model-name')?.value.trim() || '自定义模型';
        const baseUrl = document.getElementById('chat-custom-model-url')?.value.trim();
        const apiKey = document.getElementById('chat-custom-model-key')?.value.trim();
        const model = document.getElementById('chat-custom-model-name2')?.value.trim();
        const resultEl = document.getElementById('chat-test-result');
        const btn = document.getElementById('chat-save-model-btn');
        if (!this.token) {
            this.showToast('\u274C 登录已过期');
            return;
        }
        if (!baseUrl || !apiKey || !model) {
            if (resultEl) { resultEl.className = 'model-test-result error show'; resultEl.textContent = '\u274C 请填写完整的配置信息'; }
            return;
        }
        if (btn) { btn.disabled = true; btn.textContent = '\u23F3 保存中...'; }
        try {
            const res = await fetch('/api/ai-model/custom', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
                body: JSON.stringify({ name, base_url: baseUrl, api_key: apiKey, model })
            });
            const data = await res.json();
                if (data.success) {
                    this.closeChatModelModal();
                    // 隐藏引导，显示空状态
                    const guide = document.getElementById('chat-model-guide');
                    const empty = document.getElementById('chat-empty');
                    if (guide) guide.classList.remove('visible');
                    if (empty) empty.style.display = '';
                    // 更新搭子状态
                this._setBuddyStatus('online', '随时待命');
                this.showToast('\u2705 AI 模型配置成功，搭子已上线！');
            } else {
                if (resultEl) { resultEl.className = 'model-test-result error show'; resultEl.textContent = '\u274C ' + (data.error || '保存失败'); }
            }
        } catch (e) {
            this.showToast('\u274C 保存失败');
        } finally {
            if (btn) { btn.disabled = false; btn.textContent = '\u128190 保存并开始聊天'; }
        }
    },
    closeBuddyDesigner() { this.closeModal('buddy-designer-modal'); },
    closeGoalModal() { this.closeModal('goal-modal'); },
    closeAvatarPicker() { this.closeModal('avatar-picker-modal'); },

    // ===== 头像选择器 =====
    _avatarPickerType: 'buddy', // 'buddy' 或 'user'
    _selectedAvatar: '',
    _selectedAvatarFile: null, // 本地图片文件
    _selectedAvatarPreview: null, // 本地图片预览 URL

    _buddyAvatars: [
        '\u{1F916}', '\u{1F47B}', '\u{1F47C}', '\u{1F47D}', '\u{1F9D4}', '\u{1F9D1}', '\u{1F9D3}', '\u{1F9D5}',
        '\u{1F338}', '\u{1F525}', '\u{1F331}', '\u{1F308}', '\u{1F31F}', '\u{1F984}', '\u{1F98B}', '\u{1F43C}', '\u{1F981}',
        '\u{1F985}', '\u{1F389}', '\u{1F3B2}', '\u{1F3A8}', '\u{1F3AF}', '\u{1F3BC}', '\u{1F3C6}', '\u{1F3C7}'
    ],

    _userAvatars: [
        '\u{1F464}', '\u{1F9D4}', '\u{1F9D1}', '\u{1F468}', '\u{1F469}', '\u{1F475}', '\u{1F474}',
        '\u{1F471}', '\u{1F9D0}', '\u{1F9D2}', '\u{1F9D3}', '\u{1F9D5}', '\u{1F9D6}', '\u{1F9D7}', '\u{1F9D8}', '\u{1F9D9}', '\u{1F9DA}',
        '\u{1F393}', '\u{1F3EB}', '\u{1F4BB}', '\u{1F4BC}', '\u{1F4F1}', '\u{1F3A2}', '\u{1F3A4}', '\u{1F3B5}'
    ],

    _getAvatarList(type) {
        return type === 'buddy' ? this._buddyAvatars : this._userAvatars;
    },

    editBuddyAvatar(event) {
        event.stopPropagation();
        this._avatarPickerType = 'buddy';
        const titleEl = document.getElementById('avatar-picker-title');
        if (titleEl) titleEl.textContent = '\u{1F916} 更换搭子头像';
        this._selectedAvatar = this.data.buddy?.emoji || '\u{1F916}';
        this._renderAvatarPicker();
        this.openModal('avatar-picker-modal');
    },

    editUserAvatar(event) {
        event.stopPropagation();
        this._avatarPickerType = 'user';
        const titleEl = document.getElementById('avatar-picker-title');
        if (titleEl) titleEl.textContent = '\u{1F464} 更换头像';
        this._selectedAvatar = this.user?.avatar || '\u{1F464}';
        this._renderAvatarPicker();
        this.openModal('avatar-picker-modal');
    },

    _renderAvatarPicker() {
        const grid = document.getElementById('avatar-picker-grid');
        if (!grid) return;

        const avatars = this._getAvatarList(this._avatarPickerType);
        grid.innerHTML = avatars.map(avatar => `
            <div class="avatar-picker-item ${avatar === this._selectedAvatar ? 'selected' : ''}"
                 data-avatar="${avatar}"
                 onclick="App.selectAvatar('${avatar}')">
                ${avatar}
            </div>
        `).join('');
    },

    selectAvatar(avatar) {
        this._selectedAvatar = avatar;
        this._selectedAvatarFile = null;
        this._selectedAvatarPreview = null;
        document.querySelectorAll('.avatar-picker-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.avatar === avatar);
        });
    },

    handleAvatarFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            this.showToast('请选择图片文件');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            this.showToast('图片大小不能超过 5MB');
            return;
        }

        this._selectedAvatarFile = file;
        this._selectedAvatar = '';
        this._selectedAvatarPreview = URL.createObjectURL(file);

        // 清除 emoji 选择状态
        document.querySelectorAll('.avatar-picker-item').forEach(item => {
            item.classList.remove('selected');
        });

        // 显示预览
        const previewId = this._avatarPickerType === 'user'
            ? 'avatar-upload-preview-settings'
            : 'avatar-upload-preview';
        const previewEl = document.getElementById(previewId);
        if (previewEl) {
            previewEl.className = 'avatar-upload-preview show';
            previewEl.innerHTML = `<img src="${this._selectedAvatarPreview}" alt="预览"> 已选择：${file.name}`;
        }
    },

    async saveAvatar() {
        if (!this._selectedAvatar && !this._selectedAvatarFile) {
            this.showToast('请先选择头像或上传图片');
            return;
        }

        if (this._avatarPickerType === 'buddy') {
            if (this._selectedAvatarFile) {
                await this._updateBuddyAvatarImage(this._selectedAvatarFile);
            } else {
                await this._updateBuddyAvatar(this._selectedAvatar);
            }
        } else {
            if (this._selectedAvatarFile) {
                await this._updateUserAvatarImage(this._selectedAvatarFile);
            } else {
                await this._updateUserAvatar(this._selectedAvatar);
            }
        }

        this._selectedAvatarFile = null;
        if (this._selectedAvatarPreview) {
            URL.revokeObjectURL(this._selectedAvatarPreview);
            this._selectedAvatarPreview = null;
        }
        this.closeModal('avatar-picker-modal');
    },

    async _updateBuddyAvatar(emoji) {
        try {
            const res = await fetch('/api/buddy/avatar', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ emoji })
            });
            const data = await res.json();
            if (data.success) {
                if (!this.data.buddy) this.data.buddy = {};
                this.data.buddy.emoji = emoji;
                this.renderBuddy();
                this.showToast('\u{1F4AA} 搭子头像已更新');
            }
        } catch (e) {
            this.showToast('更新失败，请重试');
        }
    },

    async _updateUserAvatar(avatar) {
        try {
            const res = await fetch('/api/auth/me', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ avatar })
            });
            const data = await res.json();
            if (data.success) {
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(this.user));
                this.renderProfile();
                this.showToast('\u{1F4AA} 头像已更新');
            }
        } catch (e) {
            this.showToast('更新失败，请重试');
        }
    },

    async _updateBuddyAvatarImage(file) {
        try {
            const formData = new FormData();
            formData.append('image', file);
            const res = await fetch('/api/buddy/avatar-image', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` },
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                if (!this.data.buddy) this.data.buddy = {};
                this.data.buddy.emoji = data.emoji;
                this.renderBuddy();
                this.showToast('\u{1F4AA} 搭子头像已更新');
            } else {
                this.showToast(data.error || '上传失败');
            }
        } catch (e) {
            this.showToast('上传失败，请重试');
        }
    },

    async _updateUserAvatarImage(file) {
        try {
            const formData = new FormData();
            formData.append('avatar', file);
            const res = await fetch('/api/auth/avatar', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` },
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(this.user));
                this.renderProfile();
                this.showToast('\u{1F4AA} 头像已更新');
            } else {
                this.showToast(data.error || '上传失败');
            }
        } catch (e) {
            this.showToast('上传失败，请重试');
        }
    },

    async showModelConfig() {
        if (!this.token) {
            this.showToast('\u274C 登录已过期，请重新登录');
            return;
        }
        this.openModal('model-modal');
        await this.loadCurrentModel();
    },

    async loadCurrentModel() {
        if (!this.token) return;
        try {
            const res = await fetch('/api/ai-model/current', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (!data.success && res.status === 401) {
                this.showToast('\u274C 登录已过期，请重新登录');
                return;
            }
            if (data.success) {
                this.currentModel = data.model;
                this.currentModelMode = data.mode;

                const nameEl = document.getElementById('current-model-name');
                if (nameEl) {
                    if (data.mode === 'custom' && data.model?.name) {
                        nameEl.textContent = data.model.name;
                    } else {
                        nameEl.textContent = data.model?.name || '系统默认模型';
                    }
                }

                // 如果是自定义模型，填充表单
                if (data.mode === 'custom' && data.model) {
                    const nameInput = document.getElementById('custom-model-name');
                    const urlInput = document.getElementById('custom-model-url');
                    const modelInput = document.getElementById('custom-model-model');
                    const keyInput = document.getElementById('custom-model-key');
                    if (nameInput && data.model.name) nameInput.value = data.model.name;
                    if (urlInput && data.model.base_url) urlInput.value = data.model.base_url;
                    if (modelInput && data.model.model) modelInput.value = data.model.model;
                    if (keyInput) keyInput.value = '';
                }
            }
        } catch (e) {}
    },

    async testCustomModel() {
        const baseUrl = document.getElementById('custom-model-url')?.value.trim();
        const apiKey = document.getElementById('custom-model-key')?.value.trim();
        const model = document.getElementById('custom-model-model')?.value.trim();
        const resultEl = document.getElementById('test-result');

        if (!this.token) {
            if (resultEl) {
                resultEl.className = 'model-test-result error show';
                resultEl.textContent = '\u274C 登录已过期，请刷新页面或重新登录';
            }
            return;
        }

        if (!baseUrl || !apiKey || !model) {
            if (resultEl) {
                resultEl.className = 'model-test-result error show';
                resultEl.textContent = '\u274C 请填写完整的模型配置（API 地址、Key、模型名称）';
            }
            return;
        }

        if (resultEl) {
            resultEl.className = 'model-test-result loading show';
            resultEl.textContent = '\u23F3 测试连接中...';
        }

        try {
            // 格式化 base_url：去掉尾部斜杠和 /v1 后缀
            let url = baseUrl.replace(/\/+$/, '');
            if (url.endsWith('/v1')) url = url.slice(0, -3);

            const endpoints = [
                `${url}/v1/chat/completions`,
                `${url}/chat/completions`
            ];

            const testPayload = {
                model: model,
                messages: [{ role: "user", content: "Hi, reply with just 'OK'. (3 words max)" }],
                max_tokens: 10,
            };

            let success = false;
            let lastError = '';
            for (const endpoint of endpoints) {
                try {
                    const res = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${apiKey}`
                        },
                        body: JSON.stringify(testPayload)
                    });

                    if (res.ok) {
                        success = true;
                        if (resultEl) {
                            resultEl.className = 'model-test-result success show';
                            resultEl.textContent = '\u2705 连接成功，正在保存...';
                        }
                        // 测试成功后自动保存
                        await this.saveModelConfig(name, baseUrl, apiKey, model, url);
                        return;
                    } else if (res.status === 401) {
                        lastError = 'API Key 无效，请检查';
                        if (resultEl) {
                            resultEl.className = 'model-test-result error show';
                            resultEl.textContent = '\u274C ' + lastError;
                        }
                        return;
                    } else if (res.status === 404) {
                        continue;
                    } else {
                        let errText = '';
                        try { errText = (await res.json()).error?.message || await res.text(); } catch {}
                        lastError = `请求失败 (${res.status}): ${errText || '未知错误'}`;
                    }
                } catch (e) {
                    lastError = e.message || '连接失败';
                }
            }

            if (!success && resultEl) {
                resultEl.className = 'model-test-result error show';
                resultEl.textContent = '\u274C ' + lastError;
            }
        } catch (e) {
            if (resultEl) {
                resultEl.className = 'model-test-result error show';
                resultEl.textContent = '\u274C ' + (e.message || '测试失败');
            }
        }
    },

    async saveModelConfig(name, baseUrl, apiKey, model) {
        // 支持参数调用和表单取值两种模式
        name = name || document.getElementById('custom-model-name')?.value.trim() || '自定义模型';
        baseUrl = baseUrl || document.getElementById('custom-model-url')?.value.trim();
        apiKey = apiKey || document.getElementById('custom-model-key')?.value.trim();
        model = model || document.getElementById('custom-model-model')?.value.trim();

        if (!baseUrl || !apiKey || !model) return;

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
                this.showToast('\u2705 自定义模型已保存');
            } else {
                this.showToast(data.error || '保存失败');
            }
        } catch (e) {
            this.showToast('保存失败，请重试');
        }
    },

    logout() {
        if (!confirm('确定要退出登录吗？')) return;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    },

    _getPresetIcon(provider) {
        const icons = { ollama: '\u{1F4BB}', deepseek: '\u{1F916}', openai: '\u{1F4AC}', groq: '\u{1F524}' };
        return icons[provider] || '\u{1F4AC}';
    },

    _escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    mountInsights() { this.loadInsights(30); },
    mountAchievements() { this.loadAchievements(); },
    mountMemory() { this.loadMemory(); },
    mountPlans() { this.loadPlans(); },

    async loadAchievements() {
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
                    listEl.innerHTML = `
                        <div class="ach-grid">
                            ${all.map(a => `
                                <div class="ach-grid-item ${a.unlocked_at ? '' : 'locked'}">
                                    <div class="ach-grid-icon">${a.icon || '\u{1F3C6}'}</div>
                                    <div class="ach-grid-name">${a.name}</div>
                                    <div class="ach-grid-pts">+${a.points || 0}</div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
            }
        } catch (e) {}
    },

    async loadMemory() {
        try {
            const res = await fetch('/api/buddy/memory', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                const stats = data.stats || {};
                const summaryEl = document.getElementById('memory-summary');
                if (summaryEl) summaryEl.textContent = `搭子已记住 ${stats.total || 0} 件事`;

                const listEl = document.getElementById('memory-list');
                if (listEl && data.recent_scenes?.length > 0) {
                    listEl.innerHTML = data.recent_scenes.map(s => `
                        <div class="mem-card">
                            <div class="mem-card-content">${this._escapeHtml(s.summary || s.details || '')}</div>
                            <div class="mem-card-date">${this._formatDate(s.created_at)}</div>
                        </div>
                    `).join('');
                }
            }
        } catch (e) {}
    },

    async loadPlans() {
        try {
            const res = await fetch('/api/plans', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            if (data.success) {
                const listEl = document.getElementById('plan-list');
                if (listEl) {
                    const plans = data.plans || [];
                    if (!plans.length) {
                        listEl.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-icon">\u{1F4CB}</div>
                                <div class="empty-title">还没有学习计划</div>
                                <div class="empty-desc">制定计划让复习更有条理</div>
                            </div>`;
                    } else {
                        listEl.innerHTML = plans.map(p => `
                            <div class="plan-card">
                                <div class="plan-header">
                                    <div class="plan-subject">${this._escapeHtml(p.subject || '学习计划')}</div>
                                    <div class="plan-status ${p.status}">${p.status === 'active' ? '进行中' : '已完成'}</div>
                                </div>
                                <div class="plan-progress">
                                    <div class="plan-progress-fill" style="width:${p.progress || 0}%"></div>
                                </div>
                                <div class="plan-meta">
                                    <div class="plan-meta-item">\u{1F4C5} ${p.start_date || ''}</div>
                                    <div class="plan-meta-item">\u{1F3AF} ${p.progress || 0}%</div>
                                </div>
                            </div>
                        `).join('');
                    }
                }
            }
        } catch (e) {}
    },

    async loadInsights(days = 30) {
        try {
            const overviewRes = await fetch(`/api/insights/overview?days=${days}`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const overview = await overviewRes.json();
            if (overview.success) {
                const o = overview.overview;
                const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
                setText('insight-total-hours', o.total_hours);
                setText('insight-daily-avg', o.daily_average);
                setText('insight-total-sessions', o.total_sessions);
                setText('insight-diary-count', o.total_entries);
            }
        } catch (e) {}
    },

    switchInsightPeriod(days) {
        document.querySelectorAll('.insight-period-tab').forEach(t => {
            t.classList.toggle('active', parseInt(t.dataset.days) === days);
        });
        this.loadInsights(days);
    },

    // ===== 自定义搭子设计器 =====
    initBuddyDesigner() {
        if (this._buddyDesignerInitialized) return;
        this._buddyDesignerInitialized = true;

        const EMOJIS = [
            '\u{1F916}', '\u{1F47B}', '\u{1F916}', '\u{1F47C}', '\u{1F916}',
            '\u{1F338}', '\u{1F525}', '\u{1F331}', '\u{1F308}', '\u{1F31F}',
            '\u{1F984}', '\u{1F98B}', '\u{1F43C}', '\u{1F981}', '\u{1F42F}',
            '\u{1F985}', '\u{1F986}', '\u{1F989}', '\u{1F312}', '\u{1F303}',
            '\u{1F30D}', '\u{1F30E}', '\u{1F3D7}', '\u{1F3A8}', '\u{1F3EB}',
            '\u{1F4DA}', '\u{1F4D6}', '\u{1F4C5}', '\u{1F3AF}', '\u{1F3B2}',
            '\u{1F3B3}', '\u{1F3AE}', '\u{1F3AC}', '\u{1F3A4}', '\u{1F3B5}',
            '\u{1F3BC}', '\u{1F3A2}', '\u{1F697}', '\u{1F68C}', '\u{2708}',
            '\u{1F680}', '\u{1F4BC}', '\u{1F4BB}', '\u{1F4F1}', '\u{1F4F7}',
            '\u{1F4FA}', '\u{1F3AE}', '\u{1F579}', '\u{1F9D1}', '\u{1F9D4}',
            '\u{1F469}', '\u{1F468}', '\u{1F475}', '\u{1F474}', '\u{1F9D8}',
            '\u{1F9D7}', '\u{1F393}', '\u{1F4E1}', '\u{1F4E0}', '\u{270D}',
        ];

        const picker = document.getElementById('emoji-picker');
        if (picker) {
            picker.innerHTML = EMOJIS.map((e, i) => `
                <div class="emoji-option ${i === 0 ? 'selected' : ''}" data-emoji="${e}" onclick="App.selectBuddyEmoji('${e}', this)">
                    ${e}
                </div>
            `).join('');
        }
    },

    selectBuddyEmoji(emoji, el) {
        this.customBuddyEmoji = emoji;
        document.querySelectorAll('.emoji-option').forEach(opt => opt.classList.remove('selected'));
        el.classList.add('selected');
        this.updateBuddyPreview();
    },

    updateBuddyPreview() {
        const nameEl = document.getElementById('buddy-name');
        const name = nameEl?.value || '我的搭子';

        const personalityEl = document.getElementById('buddy-personality');
        const personality = personalityEl?.value || '自定义学习搭子';

        const previewEmoji = document.getElementById('preview-emoji');
        if (previewEmoji) previewEmoji.innerHTML = this.customBuddyEmoji;

        const previewName = document.getElementById('preview-name');
        if (previewName) previewName.textContent = name || '我的搭子';

        const previewDesc = document.getElementById('preview-desc');
        if (previewDesc) previewDesc.textContent = personality || '自定义学习搭子';
    },

    openBuddyDesigner() {
        this.openModal('buddy-designer-modal');
        if (!this._buddyDesignerInitialized) this.initBuddyDesigner();

        const previewEmoji = document.getElementById('preview-emoji');
        if (previewEmoji) previewEmoji.innerHTML = this.customBuddyEmoji;
    },

    async saveCustomBuddy() {
        const name = document.getElementById('buddy-name')?.value.trim();
        if (!name) {
            this.showToast('请输入搭子名称');
            return;
        }
        if (name.length > 20) {
            this.showToast('搭子名称不能超过20个字符');
            return;
        }

        const config = {
            name: name,
            emoji: this.customBuddyEmoji,
            personality: document.getElementById('buddy-personality')?.value.trim() || '',
            relationship: document.getElementById('buddy-relationship')?.value.trim() || '',
            speaking_style: document.getElementById('buddy-speaking-style')?.value.trim() || '',
            background: document.getElementById('buddy-background')?.value.trim() || '',
            prompt: document.getElementById('buddy-system-prompt')?.value.trim() || undefined,
        };

        try {
            const res = await fetch('/api/buddy/custom/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(config)
            });
            const data = await res.json();
            if (data.success) {
                if (!this.data.buddy) this.data.buddy = {};
                this.data.buddy = {
                    name: data.buddy.name,
                    emoji: data.buddy.emoji,
                    emotion: 'happy',
                    emotion_desc: '正在认识新搭子'
                };
                this.renderBuddy();
                this.closeBuddyDesigner();
                this.showToast(`搭子「${name}」已创建！`);
            } else {
                this.showToast(data.error || '创建失败');
            }
        } catch (e) {
            this.showToast('创建失败，请重试');
        }
    },
};

window.App = App;
