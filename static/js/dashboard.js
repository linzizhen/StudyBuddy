/**
 * StudyPal Dashboard - 纯 JS 版本
 *
 * 严格按 dashboard-app 的 React 版 1:1 翻译为原生 JS
 * - 7 个页面：仪表盘、番茄专注、待办任务、学习日记、学习搭子、数据统计、考研目标
 * - 右侧栏根据当前页面动态切换内容
 * - 主题切换、跨页面状态共享、ECharts 图表
 * - 完整对接后端 /api/*
 */

(function () {
    'use strict';

    // ==================== 图标库（Lucide 风格内联 SVG） ====================
    const ICONS = {
        dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>',
        timer: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2"/><path d="M5 3 2 6"/><path d="m22 6-3-3"/><path d="M6.38 18.7 4 21"/><path d="M17.64 18.67 20 21"/></svg>',
        check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
        book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
        message: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
        chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
        target: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
        play: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>',
        pause: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
        plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
        clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        trending: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
        users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        fire: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
        arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
        search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        bulb: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2v.3a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1V17a3 3 0 0 1 1-2A7 7 0 0 0 12 2z"/></svg>',
        refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
        moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
        sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
        settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
        graduation: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>',
        cherry: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c-1 0-1.5.5-2 1 .5.5 1 1 2 1s1.5-.5 2-1c-.5-.5-1-1-2-1zm-3 4c-1 0-1.5.5-2 1 .5.5 1 1 2 1s1.5-.5 2-1c-.5-.5-1-1-2-1zm6 0c-1 0-1.5.5-2 1 .5.5 1 1 2 1s1.5-.5 2-1c-.5-.5-1-1-2-1zm-3 4c-2 0-4 1.5-4 3.5S9 17 12 17s4-1.5 4-3.5S14 10 12 10z"/></svg>',
        save: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
        send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
        award: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
        trophy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>',
        calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
        back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
        edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
        cpu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
        user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        bell: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    };

    function renderIcons() {
        document.querySelectorAll('[data-icon]').forEach(el => {
            const name = el.getAttribute('data-icon');
            if (ICONS[name]) el.innerHTML = ICONS[name];
        });
    }

    // ==================== 主题 ====================
    const THEME_KEY = 'studypal-theme';

    function getTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved) return saved;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
        const btn = document.getElementById('btn-theme-toggle');
        if (btn) {
            const isDark = theme === 'dark';
            const iconEl = btn.querySelector('[data-icon]');
            const textEl = btn.querySelector('.bottom-row-text');
            if (iconEl) iconEl.setAttribute('data-icon', isDark ? 'sun' : 'moon');
            if (textEl) textEl.textContent = isDark ? '浅色' : '深色';
            renderIcons();
        }
        // 同步右侧栏主题按钮
        const rsBtn = document.getElementById('rs-btn-theme-toggle');
        if (rsBtn) {
            const isDark = theme === 'dark';
            const iconEl = rsBtn.querySelector('[data-icon]');
            const textEl = rsBtn.querySelector('.rs-action-text');
            if (iconEl) iconEl.setAttribute('data-icon', isDark ? 'sun' : 'moon');
            if (textEl) textEl.textContent = isDark ? '浅色' : '深色';
            renderIcons();
        }
        // 主题切换后重新渲染图表（深浅配色不同）
        renderAllCharts();
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        applyTheme(current === 'light' ? 'dark' : 'light');
    }

    // ==================== 设置弹窗 ====================
    let settingsModal = null;

    function ensureSettingsModal() {
        if (settingsModal) return settingsModal;
        const wrap = document.createElement('div');
        wrap.id = 'settings-modal';
        wrap.className = 'modal-overlay hidden';
        wrap.innerHTML = `
            <div class="modal-card">
                <div class="modal-header">
                    <h3>设置</h3>
                    <button class="modal-close" id="settings-close" aria-label="关闭">✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-row">
                        <label class="form-label">座右铭</label>
                        <input type="text" id="settings-motto" class="form-input" placeholder="一句话激励自己...">
                    </div>
                    <div class="form-row">
                        <label class="form-label">番茄默认时长（分钟）</label>
                        <input type="number" id="settings-pomo-default" class="form-input" min="5" max="60" step="5">
                    </div>
                    <div class="form-row">
                        <label class="form-label">今日目标（小时）</label>
                        <input type="number" id="settings-hours-target" class="form-input" min="0.5" max="12" step="0.5">
                    </div>
                    <div class="form-row">
                        <label class="form-label">今日目标（番茄数）</label>
                        <input type="number" id="settings-pomo-target" class="form-input" min="1" max="20">
                    </div>
                    <div class="form-row">
                        <label class="form-label">今日目标（任务数）</label>
                        <input type="number" id="settings-tasks-target" class="form-input" min="1" max="20">
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-ghost" id="settings-cancel">取消</button>
                    <button class="btn-primary" id="settings-save">保存</button>
                </div>
            </div>
        `;
        document.body.appendChild(wrap);
        settingsModal = wrap;

        wrap.querySelector('#settings-close').addEventListener('click', closeSettings);
        wrap.querySelector('#settings-cancel').addEventListener('click', closeSettings);
        wrap.addEventListener('click', e => { if (e.target === wrap) closeSettings(); });
        wrap.querySelector('#settings-save').addEventListener('click', saveSettings);

        return wrap;
    }

    function openSettings() {
        const m = ensureSettingsModal();
        // 回填当前值
        const motto = localStorage.getItem('studypal-motto') || (document.getElementById('user-motto')?.textContent || '');
        const pomo = localStorage.getItem('studypal-pomo-default') || '25';
        const h = localStorage.getItem('studypal-hours-target') || '2';
        const p = localStorage.getItem('studypal-pomo-target') || '6';
        const t = localStorage.getItem('studypal-tasks-target') || '3';
        const set = (id, v) => { const el = m.querySelector('#' + id); if (el) el.value = v; };
        set('settings-motto', motto === '准备学习中~' ? '' : motto);
        set('settings-pomo-default', pomo);
        set('settings-hours-target', h);
        set('settings-pomo-target', p);
        set('settings-tasks-target', t);
        m.classList.remove('hidden');
    }

    function closeSettings() {
        if (settingsModal) settingsModal.classList.add('hidden');
    }

    async function saveSettings() {
        const m = settingsModal;
        if (!m) return;
        const motto = m.querySelector('#settings-motto').value.trim();
        const pomo = parseInt(m.querySelector('#settings-pomo-default').value) || 25;
        const h = parseFloat(m.querySelector('#settings-hours-target').value) || 2;
        const p = parseInt(m.querySelector('#settings-pomo-target').value) || 6;
        const t = parseInt(m.querySelector('#settings-tasks-target').value) || 3;

        localStorage.setItem('studypal-motto', motto);
        localStorage.setItem('studypal-pomo-default', String(pomo));
        localStorage.setItem('studypal-hours-target', String(h));
        localStorage.setItem('studypal-pomo-target', String(p));
        localStorage.setItem('studypal-tasks-target', String(t));

        // 立即刷新显示
        const mottoEl = document.getElementById('user-motto');
        if (mottoEl) mottoEl.textContent = motto || '准备学习中~';

        // 同步到前端变量
        pomoDuration = pomo;
        if (!pomoRunning) {
            pomoTimeLeft = pomo * 60;
            const input = document.getElementById('pomo-duration-input');
            if (input) input.value = pomo;
            setText('pomo-duration-text', pomo);
            updatePomoRing();
        }

        // 尝试同步到后端
        try { await API.setMotto(motto); } catch (e) { /* local only */ }

        // 重新渲染 dashboard 让目标数更新
        renderDashboard();

        const saveBtn = m.querySelector('#settings-save');
        if (saveBtn) {
            const old = saveBtn.textContent;
            saveBtn.textContent = '已保存 ✓';
            setTimeout(() => { saveBtn.textContent = old; }, 1500);
        }
        setTimeout(closeSettings, 600);
    }

    // ==================== 搜索 ====================
    function handleSearch(query) {
        const q = (query || '').trim();
        if (!q) return;
        // 跳到搭子页并发送
        switchPage('buddy');
        setTimeout(() => {
            const input = document.getElementById('chat-input');
            if (input) {
                input.value = q;
                sendChat();
            }
        }, 120);
        // 清空搜索框
        const si = document.getElementById('search-input');
        if (si) si.value = '';
    }

    // ==================== 页面路由 ====================
    const PAGES = ['dashboard', 'pomodoro', 'tasks', 'diary', 'buddy', 'stats', 'goal', 'settings'];
    let currentPage = 'dashboard';
    let _pendingRenders = []; // 跟踪 switchPage 产生的 setTimeout，防止泄漏

    function switchPage(page) {
        if (!PAGES.includes(page)) return;
        if (page === currentPage) return;
        currentPage = page;

        // 清理旧 setTimeout（防内存泄漏）
        _pendingRenders.forEach(clearTimeout);
        _pendingRenders = [];

        // 切换主视图
        document.querySelectorAll('.page-view').forEach(el => el.classList.remove('active'));
        const view = document.getElementById('view-' + page);
        if (view) view.classList.add('active');
        // 切换右栏
        document.querySelectorAll('.rs-view').forEach(el => el.classList.remove('active'));
        const rs = document.getElementById('rs-' + page);
        if (rs) rs.classList.add('active');
        // 高亮导航
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-page') === page);
        });
        // 按需渲染（只渲染当前页 + 右栏，不渲染全部 7 个页面）
        const renderMap = {
            'stats':    renderStatsView,
            'pomodoro': renderPomodoroView,
            'buddy':    renderBuddyView,
            'goal':     renderGoalView,
            'tasks':    renderTasksView,
            'diary':    renderDiaryView,
            'settings': renderSettingsView,
        };
        const fn = renderMap[page];
        if (fn) {
            const t = setTimeout(fn, 50);
            _pendingRenders.push(t);
        }
        // dashboard 页切走时也刷新一次（数据可能变了）
        if (page !== 'dashboard') renderDashboard();
    }

    // ==================== 全局状态 ====================
    const State = {
        studyStats: null,
        tasks: [],
        diaryEntries: [],
        buddyProfile: null,
        studyPlans: [],
        todayDiary: null,
        selectedTags: [],
        moodLevel: 6,
        conversationId: null,
        chatHistory: [],
        taskFilter: 'all',
        showDiaryList: false,
    };

    // ==================== 数据加载 ====================
    async function loadAll() {
        await Promise.all([
            loadStudyStats(),
            loadTasks(),
            loadBuddy(),
            loadDiary(),
            loadPlans(),
        ]);
        // 只渲染初始可见的 Dashboard，其他页面按需渲染
        renderDashboard();
        // 图表在 Dashboard 渲染时已经包含，无需额外处理
    }

    async function loadStudyStats() {
        try {
            const res = await API.getStudyStats();
            if (res && res.success) {
                const s = res.stats || {};
                State.studyStats = {
                    ...s,
                    total_hours: s.total_hours ?? s.week_hours ?? 0,
                    total_pomodoros: s.total_pomodoros ?? s.total_sessions ?? 0,
                };
            }
        } catch (e) { /* silent */ }
    }

    async function loadTasks() {
        try {
            const res = await API.getTasks('all');
            if (res && res.success) {
                State.tasks = res.tasks || [];
            }
        } catch (e) { /* silent */ }
    }

    async function loadBuddy() {
        try {
            const [statusRes, profileRes, currentRoleRes] = await Promise.all([
                API.getBuddyStatus(),
                API.getBuddyProfile(),
                API.currentRole ? API.currentRole() : Promise.resolve(null),
            ]);
            const status = statusRes?.success ? statusRes.status : null;
            const profile = profileRes?.success ? profileRes.profile : null;
            const currentRole = currentRoleRes?.success ? currentRoleRes.role : null;
            const buddy = status?.buddy || {};
            const study = status?.study || {};
            const user = profile?.user || profile || {};
            State.buddyProfile = {
                name: currentRoleRes?.success ? currentRoleRes.name : (buddy.name || user.buddy_name || '小豆'),
                emoji: currentRoleRes?.success ? currentRoleRes.emoji : (buddy.emoji || '💪'),
                trait: currentRoleRes?.success ? currentRoleRes.trait : (buddy.trait || '温暖鼓励型'),
                level: user.level || 1,
                status: study.is_studying ? '休息中' : '在线',
                message: buddy.emotion_desc || '今天也要加油哦~',
                userName: user.name || user.nickname || '',
                role_key: currentRole || 'xiaodou',
            };
            // 更新用户名
            const userNameEl = document.getElementById('user-name');
            if (userNameEl) userNameEl.textContent = State.buddyProfile.userName || '学习战士';
            // 等级显示
            const levelEl = document.getElementById('user-level');
            if (levelEl) levelEl.textContent = 'Lv.' + State.buddyProfile.level;
        } catch (e) { /* silent */ }
    }

    async function loadDiary() {
        try {
            const res = await API.getDiaries(30);
            if (res && res.success) {
                State.diaryEntries = res.entries || [];
            }
            const today = await API.getTodayDiary();
            if (today && today.success) {
                State.todayDiary = today.entry || null;
            }
        } catch (e) { /* silent */ }
    }

    async function loadPlans() {
        try {
            const res = await API.getStudyPlans();
            if (res && res.success) {
                State.studyPlans = res.active_plans || [];
            }
        } catch (e) { /* silent */ }
    }

    // ==================== 渲染：所有页面 ====================
    function renderAll() {
        renderDashboard();
        renderPomodoroView();
        renderTasksView();
        renderDiaryView();
        renderBuddyView();
        renderStatsView();
        renderGoalView();
    }

    // ==================== 仪表盘 ====================
    function getGreeting() {
        const h = new Date().getHours();
        if (h < 12) return '早上好';
        if (h < 18) return '下午好';
        return '晚上好';
    }

    function renderDashboard() {
        const greetingEl = document.getElementById('greeting');
        if (greetingEl) greetingEl.textContent = getGreeting() + '，学习战士';

        // 4 个统计
        const stats = State.studyStats || {};
        const completedTasks = State.tasks.filter(t => t.status === 'completed').length;
        setText('stat-hours', (stats.today_hours || 0).toFixed(1));
        setText('stat-pomodoros', stats.total_pomodoros || 0);
        setText('stat-tasks-done', completedTasks);
        setText('stat-days', stats.streak_days || 0);

        // 今日目标进度（目标值优先取设置，缺省 2/6/3）
        const hoursT = parseFloat(localStorage.getItem('studypal-hours-target') || '2');
        const pomoT = parseInt(localStorage.getItem('studypal-pomo-target') || '6');
        const taskT = parseInt(localStorage.getItem('studypal-tasks-target') || '3');
        const hours = stats.today_hours || 0;
        const pomodoros = stats.total_pomodoros || 0;
        const hProg = Math.min((hours / hoursT) * 100, 100);
        const pProg = Math.min((pomodoros / pomoT) * 100, 100);
        const tProg = Math.min((completedTasks / taskT) * 100, 100);
        const todayProgress = Math.round((hProg + pProg + tProg) / 3);

        const bar = document.getElementById('progress-bar-fill');
        if (bar) bar.style.width = todayProgress + '%';
        setText('progress-percent', todayProgress + '%');
        setText('progress-streak-text', (stats.streak_days || 0) + '天连续');
        setText('bd-hours', `${hours.toFixed(1)}/${hoursT}h`);
        setText('bd-pomodoros', `${pomodoros}/${pomoT}个`);
        setText('bd-tasks', `${completedTasks}/${taskT}项`);
        setText('bd-diary', State.todayDiary ? '已记录' : '未记录');

        // 目标信息
        const mainPlan = State.studyPlans[0];
        const user = (State.buddyProfile && (State.buddyProfile._user || {})) || {};
        setText('goal-title', mainPlan?.subject || '考研目标');
        // 院校/专业/分数优先取 profile，缺省用占位
        // 由于现有 API 限制，使用占位
        // 剩余天数
        let daysLeft = '';
        if (mainPlan?.exam_date) {
            const diff = Math.ceil((new Date(mainPlan.exam_date).getTime() - Date.now()) / 86400000);
            daysLeft = (diff > 0 ? diff : 0) + ' 天';
            setText('goal-school', mainPlan.school || '--');
            setText('goal-major', mainPlan.subject || '--');
        } else {
            daysLeft = '-- 天';
            setText('goal-school', '--');
            setText('goal-major', '--');
        }
        setText('goal-days-left', daysLeft);
        setText('goal-score', (mainPlan?.target_score || mainPlan?.total_hours || 380) + ' 分');

        // 待办时间线
        const pending = State.tasks.filter(t => t.status !== 'completed').slice(0, 5);
        const timelineEl = document.getElementById('timeline-list');
        if (timelineEl) {
            if (pending.length === 0) {
                timelineEl.innerHTML = '<div class="timeline-empty">今日任务都完成啦 🎉</div>';
            } else {
                timelineEl.innerHTML = pending.map(t => `
                    <div class="timeline-item">
                        <div class="timeline-time">${formatTime(t.deadline)}</div>
                        <div class="timeline-dot"></div>
                        <div class="timeline-content">
                            <div class="timeline-title">${escapeHtml(t.title || '')}</div>
                            <div class="timeline-desc">1个番茄 · 学习中</div>
                        </div>
                    </div>
                `).join('');
            }
        }

        // 右栏 - 搭子卡
        const buddy = State.buddyProfile || {};
        setText('rs-buddy-name', buddy.name || '小豆');
        setText('rs-buddy-status', buddy.status || '在线');
        setText('rs-buddy-msg', buddy.message || '今天也要加油哦~');
        const avEl = document.getElementById('rs-buddy-avatar');
        if (avEl) avEl.textContent = buddy.emoji || '💪';
        // 搭子页大头像
        const avLg = document.getElementById('rs-buddy-page-avatar-lg');
        if (avLg) avLg.textContent = buddy.emoji || '💪';
        const rsBuddyPageName = document.getElementById('rs-buddy-page-name');
        if (rsBuddyPageName) rsBuddyPageName.textContent = buddy.name || '小豆';
        const rsBuddyPageTrait = document.getElementById('rs-buddy-page-trait');
        if (rsBuddyPageTrait) rsBuddyPageTrait.textContent = buddy.trait || '温暖鼓励型';

        // 右栏 - 今日待办
        const rsTodoEl = document.getElementById('rs-todo-list');
        if (rsTodoEl) {
            const todoPending = State.tasks.filter(t => t.status !== 'completed').slice(0, 3);
            if (todoPending.length === 0) {
                rsTodoEl.innerHTML = '<div class="timeline-empty">暂无待办任务</div>';
            } else {
                rsTodoEl.innerHTML = todoPending.map(t => `
                    <div class="rs-todo-item" data-task-id="${t.id}">
                        <div class="rs-todo-check" data-task-id="${t.id}"></div>
                        <div class="rs-todo-text">${escapeHtml(t.title || '')}</div>
                    </div>
                `).join('');
                rsTodoEl.querySelectorAll('.rs-todo-check').forEach(c => {
                    c.addEventListener('click', e => {
                        e.stopPropagation();
                        completeTask(c.getAttribute('data-task-id'), c);
                    });
                });
            }
        }

        // 右栏统计（番茄专注数据）
        const pomoSessions = pomoHistory.length;
        const pomoTotal = pomoHistory.reduce((a, s) => a + s.minutes, 0);
        setText('pomo-rs-done', pomoSessions);
        setText('pomo-rs-minutes', pomoTotal);
        setText('pomo-rs-avg', pomoSessions > 0 ? Math.round(pomoTotal / pomoSessions) : 25);
    }

    // ==================== 番茄页 ====================
    let pomoInterval = null;
    let pomoTimeLeft = (parseInt(localStorage.getItem('studypal-pomo-default') || '25')) * 60;
    let pomoRunning = false;
    let pomoDuration = parseInt(localStorage.getItem('studypal-pomo-default') || '25');
    let pomoHistory = []; // 本地会话

    function renderPomodoroView() {
        // 更新右栏统计
        const sessions = pomoHistory.length;
        const totalMin = pomoHistory.reduce((a, s) => a + s.minutes, 0);
        const avg = sessions > 0 ? Math.round(totalMin / sessions) : 25;
        setText('pomo-rs-done', sessions);
        setText('pomo-rs-minutes', totalMin);
        setText('pomo-rs-avg', avg);

        // 本周柱图（调用真实 API）
        const barEl = document.getElementById('rs-pomo-week');
        if (barEl) {
            barEl.innerHTML = '<div class="timeline-empty">暂无本周数据</div>';
        }

        // 完成历史
        const histEl = document.getElementById('pomo-history');
        if (histEl) {
            if (pomoHistory.length === 0) {
                histEl.innerHTML = '<div class="timeline-empty">还没有完成记录</div>';
            } else {
                histEl.innerHTML = pomoHistory.slice().reverse().map(h => `
                    <div class="pomo-history-item">
                        <span class="text-sm">${h.time} · ${h.subject || '学习中'}</span>
                        <span class="text-emerald-500 text-sm font-semibold">+${h.minutes}分钟</span>
                    </div>
                `).join('');
            }
        }

        // 番茄环
        updatePomoRing();
    }

    function updatePomoRing() {
        const total = pomoDuration * 60;
        const progress = ((total - pomoTimeLeft) / total) * 100;
        const circumference = 2 * Math.PI * 108;
        const offset = circumference - (progress / 100) * circumference;
        const ring = document.getElementById('pomo-ring-fill');
        if (ring) ring.setAttribute('stroke-dashoffset', offset);
        setText('pomo-time', formatPomoTime(pomoTimeLeft));
        setText('pomo-status', pomoRunning ? '专注中...' : '准备开始');
        setText('pomo-toggle-label', pomoRunning ? '暂停' : '开始');
        const toggleBtn = document.getElementById('btn-pomo-toggle');
        if (toggleBtn) {
            const iconEl = toggleBtn.querySelector('[data-icon]');
            if (iconEl) iconEl.setAttribute('data-icon', pomoRunning ? 'pause' : 'play');
            renderIcons();
        }
    }

    function formatPomoTime(s) {
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    }

    async function togglePomodoro() {
        if (!pomoRunning) {
            // 开始
            try { await API.startStudy('番茄专注'); } catch (e) { /* silent */ }
            pomoRunning = true;
            pomoTimeLeft = pomoDuration * 60;
            pomoInterval = setInterval(() => {
                pomoTimeLeft--;
                if (pomoTimeLeft <= 0) {
                    completePomodoro();
                } else {
                    updatePomoRing();
                }
            }, 1000);
        } else {
            // 暂停
            pomoRunning = false;
            if (pomoInterval) clearInterval(pomoInterval);
            updatePomoRing();
        }
    }

    async function completePomodoro() {
        if (pomoInterval) clearInterval(pomoInterval);
        pomoRunning = false;
        try {
            const res = await API.stopStudy('番茄专注');
            const dur = Math.round(res?.duration || pomoDuration);
            pomoHistory.push({
                time: new Date().toTimeString().slice(0, 5),
                minutes: dur,
                subject: '学习中',
            });
            renderPomodoroView();
        } catch (e) { /* silent */ }
        pomoTimeLeft = pomoDuration * 60;
        updatePomoRing();
        // 刷新统计
        await loadStudyStats();
        renderDashboard();
    }

    function resetPomodoro() {
        if (pomoInterval) clearInterval(pomoInterval);
        pomoRunning = false;
        pomoTimeLeft = pomoDuration * 60;
        updatePomoRing();
    }

    // ==================== 任务页 ====================
    function renderTasksView() {
        const pending = State.tasks.filter(t => t.status !== 'completed').length;
        const completed = State.tasks.filter(t => t.status === 'completed').length;
        setText('tasks-pending-count', pending + ' 待完成');
        setText('tasks-completed-count', completed + ' 已完成');

        const list = State.tasks.filter(t => {
            if (State.taskFilter === 'all') return true;
            return t.status === State.taskFilter;
        });

        const listEl = document.getElementById('task-list');
        if (listEl) {
            if (list.length === 0) {
                listEl.innerHTML = '<div class="timeline-empty">暂无任务</div>';
            } else {
                listEl.innerHTML = list.map(t => `
                    <div class="task-item ${t.status === 'completed' ? 'completed' : ''}">
                        <div class="task-check ${t.status === 'completed' ? 'checked' : ''}" data-task-id="${t.id}"></div>
                        <div class="task-content">
                            <div class="task-title">${escapeHtml(t.title || '')}</div>
                            ${t.description ? `<div class="task-desc">${escapeHtml(t.description)}</div>` : ''}
                            ${t.deadline ? `<div class="task-deadline">📅 ${formatDateTime(t.deadline)}</div>` : ''}
                        </div>
                        <button class="task-delete" data-task-id="${t.id}">
                            <span class="nav-icon" data-icon="trash"></span>
                        </button>
                    </div>
                `).join('');
                renderIcons();
                listEl.querySelectorAll('.task-check').forEach(c => {
                    c.addEventListener('click', () => completeTask(c.getAttribute('data-task-id'), c));
                });
                listEl.querySelectorAll('.task-delete').forEach(c => {
                    c.addEventListener('click', () => deleteTask(c.getAttribute('data-task-id')));
                });
            }
        }

        // 同步右栏
        setText('rs-task-pending', pending);
        setText('rs-task-completed', completed);
        const total = pending + completed || 1;
        const rate = Math.round(completed / total * 100);
        setText('rs-task-advice', `今日任务已完成 ${rate}%，继续加油！`);

        // 同步 dashboard 渲染
        renderDashboard();
    }

    async function completeTask(taskId, checkEl) {
        if (!taskId) return;
        try {
            checkEl.classList.add('checked');
            const textEl = checkEl.parentElement && checkEl.parentElement.querySelector('.rs-todo-text, .task-title');
            if (textEl) textEl.classList.add('checked');
            await API.completeTask(taskId);
            await loadTasks();
            // 精确刷新受影响的部分，不重渲染全部 7 个页面
            renderDashboard();
            if (currentPage === 'tasks') renderTasksView();
        } catch (err) {
            console.error('完成任务失败:', err);
            checkEl.classList.remove('checked');
        }
    }

    async function deleteTask(taskId) {
        if (!confirm('确定删除这个任务？')) return;
        try {
            await API.deleteTask(taskId);
            await loadTasks();
            renderDashboard();
            if (currentPage === 'tasks') renderTasksView();
        } catch (err) {
            console.error('删除任务失败:', err);
        }
    }

    async function addTask() {
        const input = document.getElementById('new-task-input');
        if (!input) return;
        const title = input.value.trim();
        if (!title) return;
        try {
            await API.addTask({ title });
            input.value = '';
            await loadTasks();
            renderDashboard();
            if (currentPage === 'tasks') renderTasksView();
        } catch (err) {
            console.error('添加任务失败:', err);
        }
    }

    // ==================== 日记页 ====================
    function renderDiaryView() {
        // 加载今日日记
        if (State.todayDiary) {
            const t = State.todayDiary;
            const titleEl = document.getElementById('diary-title');
            const contentEl = document.getElementById('diary-content');
            if (titleEl && !titleEl.value) titleEl.value = t.title || '';
            if (contentEl && !contentEl.value) contentEl.value = t.content || '';
            if (t.emotion_level) {
                State.moodLevel = t.emotion_level;
                document.querySelectorAll('.mood-btn').forEach(b => {
                    b.classList.toggle('selected', parseInt(b.getAttribute('data-level')) === t.emotion_level);
                });
            }
            if (Array.isArray(t.tags)) {
                State.selectedTags = t.tags;
                document.querySelectorAll('.tag-btn').forEach(b => {
                    b.classList.toggle('selected', State.selectedTags.includes(b.textContent));
                });
            }
        }
        updateWordCount();

        // 右栏本月统计
        const thisMonth = State.diaryEntries.filter(e => {
            const d = new Date(e.date);
            const now = new Date();
            return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
        });
        const totalWords = thisMonth.reduce((a, e) => a + (e.content?.length || 0), 0);
        const avg = thisMonth.length > 0 ? Math.round(totalWords / thisMonth.length) : 0;
        setText('diary-rs-days', thisMonth.length);
        setText('diary-rs-words', totalWords);
        setText('diary-rs-avg', avg);

        // 历史日记
        const histEl = document.getElementById('diary-history-list');
        if (histEl) {
            if (State.diaryEntries.length === 0) {
                histEl.innerHTML = '<div class="timeline-empty">还没有日记</div>';
            } else {
                histEl.innerHTML = State.diaryEntries.slice(0, 20).map(e => {
                    const emoji = e.emotion_emoji || '😐';
                    return `
                        <div class="diary-history-item" data-entry-id="${e.id}">
                            <div class="diary-history-row">
                                <span class="diary-history-emoji">${emoji}</span>
                                <div>
                                    <div class="diary-history-title">${escapeHtml(e.title || '无标题')}</div>
                                    <div class="diary-history-date">${e.date || ''}</div>
                                </div>
                            </div>
                            <div class="diary-history-content">${escapeHtml((e.content || '').slice(0, 100))}</div>
                        </div>
                    `;
                }).join('');
                histEl.querySelectorAll('.diary-history-item').forEach(it => {
                    it.addEventListener('click', () => loadDiaryIntoEditor(it.getAttribute('data-entry-id')));
                });
            }
        }
    }

    function loadDiaryIntoEditor(entryId) {
        const e = State.diaryEntries.find(x => x.id === entryId);
        if (!e) return;
        document.getElementById('diary-title').value = e.title || '';
        document.getElementById('diary-content').value = e.content || '';
        if (e.emotion_level) {
            State.moodLevel = e.emotion_level;
            document.querySelectorAll('.mood-btn').forEach(b => {
                b.classList.toggle('selected', parseInt(b.getAttribute('data-level')) === e.emotion_level);
            });
        }
        if (Array.isArray(e.tags)) {
            State.selectedTags = e.tags;
            document.querySelectorAll('.tag-btn').forEach(b => {
                b.classList.toggle('selected', State.selectedTags.includes(b.textContent));
            });
        }
        toggleDiaryList(false);
        updateWordCount();
    }

    function toggleDiaryList(force) {
        State.showDiaryList = force !== undefined ? force : !State.showDiaryList;
        const editor = document.getElementById('diary-editor');
        const history = document.getElementById('diary-history');
        if (State.showDiaryList) {
            editor.classList.add('hidden');
            history.classList.remove('hidden');
        } else {
            editor.classList.remove('hidden');
            history.classList.add('hidden');
        }
    }

    function updateWordCount() {
        const content = document.getElementById('diary-content')?.value || '';
        setText('diary-word-count', content.length);
    }

    async function saveDiary() {
        const title = document.getElementById('diary-title')?.value || '';
        const content = document.getElementById('diary-content')?.value || '';
        if (!content.trim()) {
            alert('请输入日记内容');
            return;
        }
        const saveLabel = document.getElementById('diary-save-label');
        const oldText = saveLabel?.textContent;
        if (saveLabel) saveLabel.textContent = '保存中...';
        try {
            await API.saveDiary({
                title: title.trim() || `日记 - ${new Date().toLocaleDateString()}`,
                content: content.trim(),
                emotion_level: State.moodLevel,
                tags: State.selectedTags,
            });
            if (saveLabel) saveLabel.textContent = '已保存 ✓';
            setTimeout(() => { if (saveLabel) saveLabel.textContent = oldText || '保存日记'; }, 2000);
            await loadDiary();
            renderDiaryView();
        } catch (err) {
            console.error('保存失败:', err);
            if (saveLabel) saveLabel.textContent = '保存失败';
            setTimeout(() => { if (saveLabel) saveLabel.textContent = oldText || '保存日记'; }, 2000);
        }
    }

    // ==================== 搭子页 ====================
    function renderBuddyView() {
        const b = State.buddyProfile || {};
        setText('buddy-page-name', b.name || '小豆');
        setText('buddy-page-trait', (b.trait || '温暖鼓励型') + ' · Lv.' + (b.level || 1));
        const avEl = document.getElementById('buddy-page-avatar');
        if (avEl) avEl.textContent = b.emoji || '💪';

        // 右栏搭子信息（考研目标页右栏也会用到）
        setText('rs-buddy-page-name', b.name || '小豆');
        setText('rs-buddy-page-trait', b.trait || '温暖鼓励型');
        setText('rs-buddy-level', 'Lv.' + (b.level || 1));
        const avLg = document.getElementById('rs-buddy-page-avatar-lg');
        if (avLg) avLg.textContent = b.emoji || '💪';
    }

    function appendChat(role, content) {
        const wrap = document.getElementById('chat-messages');
        if (!wrap) return;
        const div = document.createElement('div');
        div.className = 'chat-bubble ' + role;
        const avatar = role === 'user' ? '👤' : (State.buddyProfile?.emoji || '💪');
        div.innerHTML = `
            <div class="chat-avatar">${avatar}</div>
            <div class="chat-content">${escapeHtml(content)}</div>
        `;
        wrap.appendChild(div);
        wrap.scrollTop = wrap.scrollHeight;
    }

    function resetChat() {
        const wrap = document.getElementById('chat-messages');
        if (wrap) {
            wrap.innerHTML = `
                <div class="chat-bubble assistant">
                    <div class="chat-avatar">💪</div>
                    <div class="chat-content">嗨！我是你的学习搭子，今天有什么想聊的？</div>
                </div>
            `;
        }
        State.conversationId = null;
        State.chatHistory = [];
    }

    async function sendChat() {
        const input = document.getElementById('chat-input');
        if (!input) return;
        const msg = input.value.trim();
        if (!msg) return;
        input.value = '';
        appendChat('user', msg);
        const sendBtn = document.getElementById('btn-chat-send');
        if (sendBtn) sendBtn.disabled = true;
        try {
            const res = await API.buddyChat(msg, State.conversationId || undefined);
            if (res && res.success) {
                if (res.conversation_id) State.conversationId = res.conversation_id;
                appendChat('assistant', res.reply || '我遇到了一些问题，请稍后再试~');
                loadBuddy();
            } else {
                appendChat('assistant', '抱歉，我遇到了一些问题。');
            }
        } catch (err) {
            console.error('Chat error:', err);
            appendChat('assistant', '网络异常，请稍后再试~');
        } finally {
            if (sendBtn) sendBtn.disabled = false;
            input.focus();
        }
    }

    // ==================== 统计页 ====================
    function renderStatsView() {
        const stats = State.studyStats || {};
        setText('stats-week-hours', (stats.week_hours || 0).toFixed(1));
        setText('stats-streak', stats.streak_days || 0);
        setText('stats-total-pomodoros', stats.total_pomodoros || 0);

        const completed = State.tasks.filter(t => t.status === 'completed').length;
        const total = State.tasks.length || 1;
        const rate = Math.round(completed / total * 100);
        setText('stats-completion-rate', rate + '%');

        setText('stats-month-label', new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' }));

        // 本月统计
        const thisMonth = State.diaryEntries.filter(e => {
            const d = new Date(e.date);
            const now = new Date();
            return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
        });
        const totalWords = thisMonth.reduce((a, e) => a + (e.content?.length || 0), 0);
        const avgEmotion = thisMonth.length > 0
            ? (thisMonth.reduce((a, e) => a + (e.emotion_level || 0), 0) / thisMonth.length).toFixed(1)
            : '0';

        const monthEl = document.getElementById('stats-month-summary');
        if (monthEl) {
            monthEl.innerHTML = `
                <div class="month-row"><span>日记篇数</span><b class="text-emerald-500">${thisMonth.length}</b></div>
                <div class="month-row"><span>平均情绪</span><b class="text-blue-500">${avgEmotion}/10</b></div>
                <div class="month-row"><span>日记字数</span><b class="text-amber-500">${totalWords}</b></div>
            `;
        }

        // 各科进度（调用真实数据）
        const subjEl = document.getElementById('stats-subject-progress');
        if (subjEl) {
            subjEl.innerHTML = '<div class="timeline-empty">暂无学习进度数据</div>';
        }

        // 累计成就 - 右栏
        setText('rs-ach-hours', Math.round(stats.total_hours || 0));
        setText('rs-ach-pomodoros', stats.total_pomodoros || 0);
        setText('rs-ach-days', stats.streak_days || 0);
        setText('rs-ach-rate', rate + '%');

        // 图表
        renderStatsCharts();
    }

    // ==================== 目标页 ====================
    function renderGoalView() {
        const mainPlan = State.studyPlans[0];

        // 倒计时
        const targetDate = mainPlan?.exam_date || '2026-12-21';
        const diff = Math.ceil((new Date(targetDate).getTime() - Date.now()) / 86400000);
        const days = diff > 0 ? diff : 0;
        setText('countdown-days', days);
        setText('rs-goal-days', days);

        // 各科进度
        const spEl = document.getElementById('goal-subject-progress');
        if (spEl) {
            spEl.innerHTML = '<div class="timeline-empty">暂无科目数据</div>';
        }
        const rsSpEl = document.getElementById('rs-goal-subjects');
        if (rsSpEl) {
            rsSpEl.innerHTML = '<div class="timeline-empty">暂无</div>';
        }

        // 历年分数线
        const slEl = document.getElementById('goal-score-lines');
        if (slEl) {
            slEl.innerHTML = '<div class="timeline-empty">暂无分数线数据</div>';
        }

        // 重要节点
        const msEl = document.getElementById('goal-milestones');
        if (msEl) {
            if (mainPlan?.exam_date) {
                msEl.innerHTML = `
                    <div class="milestone-card important">
                        <div class="milestone-row">
                            <span class="milestone-name" style="color:var(--color-amber-500);">考研初试</span>
                            <span class="badge-outline">${days}天</span>
                        </div>
                        <div class="milestone-date">${mainPlan.exam_date}</div>
                    </div>
                `;
            } else {
                msEl.innerHTML = '<div class="timeline-empty">暂无重要节点</div>';
            }
        }
    }

    // ==================== 设置页 ====================
    function renderSettingsView() {
        const buddy = State.buddyProfile || {};
        setText('settings-buddy-name', buddy.name || '小豆');
        setText('settings-buddy-trait', buddy.trait || '温暖鼓励型');
        const avEl = document.getElementById('settings-buddy-avatar');
        if (avEl) avEl.textContent = buddy.emoji || '💪';
        const h = localStorage.getItem('studypal-hours-target') || '2';
        const p = localStorage.getItem('studypal-pomo-target') || '6';
        const dur = localStorage.getItem('studypal-pomo-default') || '25';
        const motto = localStorage.getItem('studypal-motto') || '';
        const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
        set('settings-hours-target', h);
        set('settings-pomo-target', p);
        set('settings-pomo-duration', dur);
        set('settings-motto', motto === '准备学习中~' ? '' : motto);
    }

    function switchRole() {
        const modal = ensureBuddyRoleModal();
        modal.classList.remove('hidden');
        loadBuddyRoles();
    }

    let buddyRoleModal = null;

    function ensureBuddyRoleModal() {
        if (buddyRoleModal) return buddyRoleModal;
        const wrap = document.createElement('div');
        wrap.id = 'buddy-role-modal';
        wrap.className = 'modal-overlay hidden';
        wrap.innerHTML = `
            <div class="modal-card modal-lg">
                <div class="modal-header">
                    <h3>选择学习搭子</h3>
                    <button class="modal-close" id="buddy-role-close" aria-label="关闭">✕</button>
                </div>
                <div class="modal-body">
                    <div class="buddy-role-grid" id="buddy-role-grid"></div>
                </div>
            </div>
        `;
        document.body.appendChild(wrap);
        buddyRoleModal = wrap;

        wrap.querySelector('#buddy-role-close').addEventListener('click', () => {
            buddyRoleModal.classList.add('hidden');
        });
        wrap.addEventListener('click', e => {
            if (e.target === wrap) buddyRoleModal.classList.add('hidden');
        });

        return wrap;
    }

    async function loadBuddyRoles() {
        const grid = document.getElementById('buddy-role-grid');
        if (!grid) return;
        try {
            const res = await API.getBuddyRoles();
            if (res && res.success) {
                const currentRole = State.buddyProfile?.role_key || 'xiaodou';
                grid.innerHTML = res.roles.map(role => `
                    <div class="buddy-role-card ${role.id === currentRole ? 'active' : ''}" data-role="${role.id}">
                        <div class="buddy-role-emoji">${role.emoji}</div>
                        <div class="buddy-role-name">${role.name}</div>
                        <div class="buddy-role-trait">${role.personality}</div>
                        <div class="buddy-role-desc">${role.description}</div>
                        ${role.id === currentRole ? '<div class="buddy-role-current">当前搭子</div>' : ''}
                    </div>
                `).join('');
                grid.querySelectorAll('.buddy-role-card').forEach(card => {
                    card.addEventListener('click', () => selectBuddyRole(card.getAttribute('data-role')));
                });
            }
        } catch (e) {
            grid.innerHTML = '<div class="timeline-empty">加载失败</div>';
        }
    }

    async function selectBuddyRole(roleKey) {
        try {
            const res = await API.switchBuddyRole(roleKey);
            if (res && res.success) {
                // 更新所有搭子相关显示
                const currentRes = await API.currentRole();
                if (currentRes?.success) {
                    State.buddyProfile = {
                        ...State.buddyProfile,
                        name: currentRes.name || '小豆',
                        emoji: currentRes.emoji || '🌸',
                        trait: currentRes.trait || '温暖鼓励型',
                        role_key: currentRes.role || roleKey,
                    };
                }
                renderBuddyView();
                renderSettingsView();
                renderDashboard();
                // 更新右侧栏搭子显示
                const rsAvatar = document.getElementById('rs-buddy-avatar');
                if (rsAvatar) rsAvatar.textContent = State.buddyProfile.emoji || '🌸';
                const rsName = document.getElementById('rs-buddy-name');
                if (rsName) rsName.textContent = State.buddyProfile.name || '小豆';
                buddyRoleModal?.classList.add('hidden');
            }
        } catch (e) {
            console.error('切换搭子失败:', e);
        }
    }

    function openBuddyDesigner() {
        alert('搭子设计器功能开发中...');
    }

    function showModelConfig() {
        const modal = ensureModelConfigModal();
        modal.classList.remove('hidden');
        loadModelConfig();
    }

    let modelConfigModal = null;

    function ensureModelConfigModal() {
        if (modelConfigModal) return modelConfigModal;
        const wrap = document.createElement('div');
        wrap.id = 'model-config-modal';
        wrap.className = 'modal-overlay hidden';
        wrap.innerHTML = `
            <div class="modal-card">
                <div class="modal-header">
                    <h3>AI模型配置</h3>
                    <button class="modal-close" id="model-config-close" aria-label="关闭">✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-row">
                        <label class="form-label">AI服务商</label>
                        <select class="form-input" id="model-provider">
                            <option value="openai">OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                            <option value="ollama">Ollama</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <label class="form-label">模型名称</label>
                        <input type="text" class="form-input" id="model-name" placeholder="如：gpt-3.5-turbo">
                    </div>
                    <div class="form-row">
                        <label class="form-label">温度参数 (0-1)</label>
                        <input type="number" class="form-input" id="model-temperature" min="0" max="1" step="0.1" value="0.7">
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-ghost" id="model-config-cancel">取消</button>
                    <button class="btn-primary" id="model-config-save">保存</button>
                </div>
            </div>
        `;
        document.body.appendChild(wrap);
        modelConfigModal = wrap;

        wrap.querySelector('#model-config-close').addEventListener('click', () => {
            modelConfigModal.classList.add('hidden');
        });
        wrap.querySelector('#model-config-cancel').addEventListener('click', () => {
            modelConfigModal.classList.add('hidden');
        });
        wrap.addEventListener('click', e => {
            if (e.target === wrap) modelConfigModal.classList.add('hidden');
        });
        wrap.querySelector('#model-config-save').addEventListener('click', saveModelConfig);

        return wrap;
    }

    async function loadModelConfig() {
        try {
            const res = await API.getModelConfig();
            if (res && res.success) {
                const cfg = res.config;
                const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
                set('model-provider', cfg.provider || 'openai');
                set('model-name', cfg.model || 'gpt-3.5-turbo');
                set('model-temperature', cfg.temperature || 0.7);
            }
        } catch (e) {
            console.error('加载模型配置失败:', e);
        }
    }

    async function saveModelConfig() {
        const provider = document.getElementById('model-provider')?.value;
        const model = document.getElementById('model-name')?.value;
        const temperature = parseFloat(document.getElementById('model-temperature')?.value || '0.7');
        try {
            await API.updateModelConfig({ provider, model, temperature });
            modelConfigModal?.classList.add('hidden');
            alert('配置已保存');
        } catch (e) {
            console.error('保存模型配置失败:', e);
        }
    }

    // ==================== 图表 ====================
    let weeklyChart = null;
    let statsLineChart = null;
    let statsPieChart = null;

    function getChartTheme() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        return {
            textColor: isDark ? '#cbd5e1' : '#64748b',
            tooltipBg: isDark ? '#1e293b' : '#fff',
            splitLine: isDark ? '#334155' : '#e2e8f0',
        };
    }

    function getWeeklyData() {
        // 调用真实 API 获取本周学习数据
        return [];
    }

    function renderWeeklyChart() {
        const el = document.getElementById('rs-weekly-chart');
        if (!el || !window.echarts) return;
        const theme = getChartTheme();
        if (!weeklyChart) weeklyChart = echarts.init(el);

        weeklyChart.setOption({
            grid: { top: 6, left: 28, right: 4, bottom: 18 },
            tooltip: {
                trigger: 'axis',
                backgroundColor: theme.tooltipBg,
                borderColor: 'transparent',
                textStyle: { color: theme.textColor, fontSize: 12 },
                formatter: p => `${p[0].name}<br/>学习 <b>${p[0].value.toFixed(1)}h</b>`,
            },
            xAxis: {
                type: 'category',
                data: getWeeklyData().map(d => d.day),
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { color: theme.textColor, fontSize: 10 },
            },
            yAxis: { type: 'value', show: false },
            series: [{
                type: 'line',
                data: getWeeklyData().map(d => d.hours),
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: { color: '#10b981', width: 2 },
                itemStyle: { color: '#10b981' },
            }],
        });
    }

    function renderStatsCharts() {
        const lineEl = document.getElementById('stats-line-chart');
        const pieEl = document.getElementById('stats-pie-chart');
        if (!lineEl || !pieEl || !window.echarts) return;
        const theme = getChartTheme();

        if (!statsLineChart) statsLineChart = echarts.init(lineEl);
        statsLineChart.setOption({
            grid: { top: 6, left: 32, right: 8, bottom: 22 },
            tooltip: {
                trigger: 'axis',
                backgroundColor: theme.tooltipBg,
                borderColor: 'transparent',
                textStyle: { color: theme.textColor, fontSize: 12 },
            },
            xAxis: {
                type: 'category',
                data: getWeeklyData().map(d => d.day),
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { color: theme.textColor, fontSize: 12 },
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { color: theme.textColor, fontSize: 12 },
                splitLine: { lineStyle: { color: theme.splitLine } },
            },
            series: [{
                type: 'line',
                data: getWeeklyData().map(d => d.hours),
                smooth: true,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: { color: '#10b981', width: 3 },
                itemStyle: { color: '#10b981' },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgba(16, 185, 129, 0.25)' },
                            { offset: 1, color: 'rgba(16, 185, 129, 0)' },
                        ],
                    },
                },
            }],
        });

        if (!statsPieChart) statsPieChart = echarts.init(pieEl);
        const emotionData = [
            { name: '很开心', value: 35, color: '#10b981' },
            { name: '还好', value: 40, color: '#3b82f6' },
            { name: '一般', value: 15, color: '#94a3b8' },
            { name: '有点丧', value: 8, color: '#f59e0b' },
            { name: '很难过', value: 2, color: '#ef4444' },
        ];
        statsPieChart.setOption({
            tooltip: {
                backgroundColor: theme.tooltipBg,
                borderColor: 'transparent',
                textStyle: { color: theme.textColor, fontSize: 12 },
            },
            series: [{
                type: 'pie',
                radius: ['50%', '80%'],
                center: ['50%', '50%'],
                data: emotionData,
                label: { show: false },
                itemStyle: { borderColor: theme.tooltipBg, borderWidth: 2 },
            }],
        });

        // 图例
        const legendEl = document.getElementById('stats-pie-legend');
        if (legendEl) {
            legendEl.innerHTML = emotionData.map(d => `
                <div class="pie-legend-item">
                    <span class="pie-legend-dot" style="background:${d.color}"></span>
                    <span>${d.name}</span>
                </div>
            `).join('');
        }
    }

    function renderAllCharts() {
        renderWeeklyChart();
        if (currentPage === 'stats') renderStatsCharts();
    }

    // ==================== 工具 ====================
    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatTime(deadline) {
        if (!deadline) return '--:--';
        try {
            const d = new Date(deadline.replace(' ', 'T'));
            if (isNaN(d.getTime())) return '--:--';
            return d.toTimeString().slice(0, 5);
        } catch (e) { return '--:--'; }
    }

    function formatDateTime(dt) {
        if (!dt) return '';
        try {
            const d = new Date(dt.replace(' ', 'T'));
            if (isNaN(d.getTime())) return dt;
            return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
        } catch (e) { return dt; }
    }

    // ==================== 事件绑定 ====================
    function bindEvents() {
        // 主题
        document.getElementById('btn-theme-toggle')?.addEventListener('click', toggleTheme);

        // 导航
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.addEventListener('click', () => switchPage(item.getAttribute('data-page')));
        });

        // 卡片 clickable
        document.querySelectorAll('.card.clickable').forEach(card => {
            card.addEventListener('click', () => switchPage(card.getAttribute('data-page')));
        });

        // btn-ghost-tiny 跳转
        document.querySelectorAll('.btn-ghost-tiny[data-page]').forEach(b => {
            b.addEventListener('click', () => switchPage(b.getAttribute('data-page')));
        });

        // 仪表盘：开始学习 → 番茄
        document.getElementById('btn-start-study')?.addEventListener('click', () => switchPage('pomodoro'));

        // 搜索框：Enter 跳搭子页并发送
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('keydown', e => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSearch(searchInput.value);
                }
            });
            // 搜索图标点击也触发
            const searchBox = document.getElementById('search-box');
            if (searchBox) {
                searchBox.addEventListener('click', e => {
                    // 点击图标时聚焦到 input
                    if (e.target.closest('.nav-icon')) {
                        searchInput.focus();
                    }
                });
            }
        }
        // 一键番茄
        document.getElementById('btn-quick-pomodoro')?.addEventListener('click', () => {
            switchPage('pomodoro');
            setTimeout(() => { if (!pomoRunning) togglePomodoro(); }, 100);
        });
        // 看板 4 个统计卡：hover 效果 + 跳到 stats
        ['stat-hours-card', 'stat-pomo-card', 'stat-tasks-card', 'stat-days-card'].forEach(id => {
            const card = document.getElementById(id);
            if (card) {
                card.classList.add('clickable');
                card.addEventListener('click', () => switchPage('stats'));
            }
        });
        // 设置
        document.getElementById('btn-settings')?.addEventListener('click', openSettings);
        document.getElementById('rs-btn-settings')?.addEventListener('click', openSettings);

        // 主题（右侧栏按钮）
        document.getElementById('rs-btn-theme-toggle')?.addEventListener('click', toggleTheme);

        // 番茄：开关 / 重置 / 时长
        document.getElementById('btn-pomo-toggle')?.addEventListener('click', togglePomodoro);
        document.getElementById('btn-pomo-reset')?.addEventListener('click', resetPomodoro);
        const durInput = document.getElementById('pomo-duration-input');
        if (durInput) {
            durInput.addEventListener('input', e => {
                pomoDuration = parseInt(e.target.value);
                setText('pomo-duration-text', pomoDuration);
                if (!pomoRunning) pomoTimeLeft = pomoDuration * 60;
                updatePomoRing();
            });
        }

        // 任务
        document.getElementById('btn-add-task')?.addEventListener('click', addTask);
        document.getElementById('new-task-input')?.addEventListener('keydown', e => {
            if (e.key === 'Enter') addTask();
        });
        document.querySelectorAll('.filter-tab').forEach(t => {
            t.addEventListener('click', () => {
                State.taskFilter = t.getAttribute('data-filter');
                document.querySelectorAll('.filter-tab').forEach(x => x.classList.toggle('active', x === t));
                renderTasksView();
            });
        });

        // 日记
        document.getElementById('btn-save-diary')?.addEventListener('click', saveDiary);
        document.getElementById('btn-toggle-diary-list')?.addEventListener('click', () => toggleDiaryList());
        document.getElementById('diary-content')?.addEventListener('input', updateWordCount);
        document.querySelectorAll('.mood-btn').forEach(b => {
            b.addEventListener('click', () => {
                State.moodLevel = parseInt(b.getAttribute('data-level'));
                document.querySelectorAll('.mood-btn').forEach(x => x.classList.toggle('selected', x === b));
            });
        });
        document.querySelectorAll('.tag-btn').forEach(b => {
            b.addEventListener('click', () => {
                const tag = b.textContent;
                if (State.selectedTags.includes(tag)) {
                    State.selectedTags = State.selectedTags.filter(t => t !== tag);
                    b.classList.remove('selected');
                } else {
                    State.selectedTags.push(tag);
                    b.classList.add('selected');
                }
            });
        });

        // 搭子
        document.getElementById('btn-chat-send')?.addEventListener('click', sendChat);
        document.getElementById('chat-input')?.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
        });
        document.getElementById('btn-buddy-new-chat')?.addEventListener('click', resetChat);
        document.querySelectorAll('.quick-reply').forEach(b => {
            b.addEventListener('click', () => {
                const input = document.getElementById('chat-input');
                if (input) {
                    input.value = b.getAttribute('data-reply');
                    sendChat();
                }
            });
        });
        document.getElementById('rs-buddy-chat')?.addEventListener('click', () => switchPage('buddy'));

        // 目标
        document.getElementById('btn-add-goal')?.addEventListener('click', () => {
            document.getElementById('goal-form-card')?.classList.toggle('hidden');
        });
        document.getElementById('btn-cancel-goal')?.addEventListener('click', () => {
            document.getElementById('goal-form-card')?.classList.add('hidden');
        });
        document.getElementById('btn-save-goal')?.addEventListener('click', async () => {
            const subject = document.getElementById('goal-subject')?.value.trim();
            const exam_date = document.getElementById('goal-exam-date')?.value;
            const target_score = document.getElementById('goal-target-score')?.value;
            const daily_hours = parseFloat(document.getElementById('goal-daily-hours')?.value || '2');
            if (!subject || !exam_date || !target_score) {
                alert('请填写完整科目信息');
                return;
            }
            try {
                await API.createStudyPlan({
                    subject,
                    exam_date,
                    target_score: parseInt(target_score),
                    daily_hours,
                });
                document.getElementById('goal-form-card')?.classList.add('hidden');
                document.getElementById('goal-subject').value = '';
                document.getElementById('goal-exam-date').value = '';
                document.getElementById('goal-target-score').value = '';
                await loadPlans();
                renderGoalView();
            } catch (err) {
                alert('保存失败：' + err.message);
            }
        });

        // 设置页
        document.getElementById('btn-switch-buddy')?.addEventListener('click', switchRole);
        document.getElementById('btn-buddy-designer')?.addEventListener('click', openBuddyDesigner);
        document.getElementById('btn-model-config')?.addEventListener('click', showModelConfig);
        document.getElementById('btn-save-preferences')?.addEventListener('click', () => {
            const h = document.getElementById('settings-hours-target')?.value;
            const p = document.getElementById('settings-pomo-target')?.value;
            const dur = document.getElementById('settings-pomo-duration')?.value;
            if (h) localStorage.setItem('studypal-hours-target', h);
            if (p) localStorage.setItem('studypal-pomo-target', p);
            if (dur) localStorage.setItem('studypal-pomo-default', dur);
            alert('偏好设置已保存');
            renderDashboard();
        });
        document.getElementById('btn-save-profile')?.addEventListener('click', async () => {
            const motto = document.getElementById('settings-motto')?.value.trim();
            localStorage.setItem('studypal-motto', motto);
            const mottoEl = document.getElementById('user-motto');
            if (mottoEl) mottoEl.textContent = motto || '准备学习中~';
            try { await API.setMotto(motto); } catch (e) { /* silent */ }
            alert('个人信息已保存');
        });
        document.getElementById('btn-save-notifications')?.addEventListener('click', () => {
            alert('通知设置已保存');
        });

        // 窗口 resize 防抖重渲染图表
        let _resizeTimer = null;
        window.addEventListener('resize', () => {
            clearTimeout(_resizeTimer);
            _resizeTimer = setTimeout(() => {
                weeklyChart?.resize();
                statsLineChart?.resize();
                statsPieChart?.resize();
            }, 150);
        });
    }

    // ==================== 初始化 ====================
    function init() {
        // 1. 主题
        applyTheme(getTheme());

        // 2. 渲染所有图标
        renderIcons();

        // 3. 绑定事件
        bindEvents();

        // 4. 加载数据
        loadAll();

        // 5. 周期性刷新（60s）——不 fire-and-forget，不重渲染全部页面
        let _refreshTimer = null;
        function scheduleRefresh() {
            _refreshTimer = setTimeout(async () => {
                try {
                    await loadStudyStats();
                    await loadTasks();
                } catch (e) { /* silent */ }
                // 只刷新数据关联的页面
                renderDashboard();
                if (currentPage === 'tasks') renderTasksView();
                // 页面可见时继续调度，否则暂停
                if (!document.hidden) scheduleRefresh();
            }, 60000);
        }
        // 页面重新可见时立即刷新一次
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                clearTimeout(_refreshTimer);
                scheduleRefresh();
            }
        });
        scheduleRefresh();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
