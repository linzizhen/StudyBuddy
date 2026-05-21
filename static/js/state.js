/**
 * StudyPal 状态管理 v2.0
 * 管理应用全局状态
 */

const State = {
    // ==================== 状态定义 ====================

    _state: {
        // 搭子状态
        buddy: {
            name: '小豆',
            emoji: '🐱',
            emotion: 'idle',
            emotionDesc: '休息中~',
            message: '加载中...',
        },

        // 用户档案
        profile: {
            name: '',
            targetSchool: '',
            targetMajor: '',
            targetScore: 0,
            examDate: null,
            dailyGoalHours: 8,
            daysRemaining: -1,
            currentPhase: '未设置',
            isSetup: false,
        },

        // 学习状态
        study: {
            isStudying: false,
            currentSubject: '数学',
            todayHours: 0,
            streakDays: 0,
            weekHours: 0,
            goalProgress: 0,
            goalReached: false,
        },

        // 日记状态
        diary: {
            hasToday: false,
            todayEmotion: null,
            emotionCurve: [],
        },

        // 关心事件
        caringEvents: [],

        // 记忆统计
        memory: {
            scenes: 0,
            conversations: 0,
        },

        // 成就状态
        achievements: {
            total: 0,
            unlocked: 0,
            points: 0,
            level: {},
        },

        // 聊天状态
        chat: {
            conversationId: null,
            history: [],
            isLoading: false,
        },

        // UI 状态
        ui: {
            currentPage: 'home',
            theme: 'light',
            isLoading: false,
        },

        // 学习计时器
        timer: {
            startTime: null,
            elapsed: 0,
            interval: null,
        },
    },

    // ==================== 状态访问 ====================

    /**
     * 获取状态值
     * @param {string} key - 状态路径，如 'buddy.name'
     */
    get(key) {
        const keys = key.split('.');
        let value = this._state;

        for (const k of keys) {
            if (value === undefined || value === null) return undefined;
            value = value[k];
        }

        return value;
    },

    /**
     * 设置状态值
     * @param {string} key - 状态路径
     * @param {*} value - 新值
     */
    set(key, value) {
        const keys = key.split('.');
        let target = this._state;

        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (typeof target[k] !== 'object') {
                target[k] = {};
            }
            target = target[k];
        }

        const lastKey = keys[keys.length - 1];
        const oldValue = target[lastKey];
        target[lastKey] = value;

        // 触发变更通知
        this._notify(key, value, oldValue);
    },

    /**
     * 批量更新状态
     * @param {Object} updates - 更新对象
     */
    update(updates) {
        for (const [key, value] of Object.entries(updates)) {
            this.set(key, value);
        }
    },

    // ==================== 观察者模式 ====================

    _listeners: new Map(),

    /**
     * 订阅状态变更
     * @param {string} key - 状态路径
     * @param {Function} callback - 回调函数
     * @returns {Function} 取消订阅函数
     */
    subscribe(key, callback) {
        if (!this._listeners.has(key)) {
            this._listeners.set(key, new Set());
        }
        this._listeners.get(key).add(callback);

        // 返回取消订阅函数
        return () => {
            this._listeners.get(key)?.delete(callback);
        };
    },

    /**
     * 通知状态变更
     */
    _notify(key, newValue, oldValue) {
        // 通知精确匹配
        const listeners = this._listeners.get(key);
        if (listeners) {
            listeners.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }

        // 通知通配符匹配（如 'buddy.*'）
        const wildcardKey = key.split('.')[0] + '.*';
        const wildcardListeners = this._listeners.get(wildcardKey);
        if (wildcardListeners) {
            wildcardListeners.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }

        // 通知全局监听
        const allListeners = this._listeners.get('*');
        if (allListeners) {
            allListeners.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }
    },

    // ==================== 计算属性 ====================

    /**
     * 计算属性定义
     */
    computed: {
        /**
         * 是否显示倒计时
         */
        showCountdown(state) {
            return state.profile.daysRemaining >= 0;
        },

        /**
         * 问候语
         */
        greeting(state) {
            const hour = new Date().getHours();
            if (hour < 6) return '夜深了';
            if (hour < 9) return '早上好';
            if (hour < 12) return '上午好';
            if (hour < 14) return '中午好';
            if (hour < 18) return '下午好';
            return '晚上好';
        },

        /**
         * 倒计时文本
         */
        countdownText(state) {
            const days = state.profile.daysRemaining;
            if (days < 0) return '设置目标';
            if (days === 0) return '今天考试！';
            return `考研倒计时 ${days} 天`;
        },

        /**
         * 今日进度文本
         */
        progressText(state) {
            const { study } = state;
            if (study.goalReached) return '目标达成！🎉';
            return `${study.todayHours.toFixed(1)}h / ${study.profile?.dailyGoalHours || 8}h`;
        },

        /**
         * 今日情绪文本
         */
        emotionText(state) {
            if (!state.diary.hasToday) {
                return { label: '记录今日心情', hint: '点击记录今天的感觉' };
            }
            return {
                label: `今日心情：${state.diary.todayEmotion || ''}`,
                hint: '点击查看历史',
            };
        },
    },

    // ==================== 初始化 ====================

    /**
     * 初始化状态
     * @param {Object} initialData - 初始数据
     */
    init(initialData = {}) {
        // 从 localStorage 恢复主题
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this._state.ui.theme = savedTheme;
            document.documentElement.setAttribute('data-theme', savedTheme);
        }

        // 从 API 数据初始化
        if (initialData.buddy) {
            this.update({
                'buddy.name': initialData.buddy.name,
                'buddy.emoji': initialData.buddy.emoji,
                'buddy.emotion': initialData.buddy.emotion,
                'buddy.emotionDesc': initialData.buddy.emotion_desc,
            });
        }

        if (initialData.profile) {
            this.update({
                'profile.targetSchool': initialData.profile.target_school,
                'profile.targetMajor': initialData.profile.target_major,
                'profile.daysRemaining': initialData.profile.days_remaining,
                'profile.currentPhase': initialData.profile.current_phase,
                'profile.isSetup': initialData.profile.is_setup,
            });
        }

        if (initialData.study) {
            this.update({
                'study.isStudying': initialData.study.is_studying,
                'study.todayHours': initialData.study.today_hours,
                'study.streakDays': initialData.study.streak_days,
                'study.weekHours': initialData.study.week_hours,
            });
        }
    },

    // ==================== 持久化 ====================

    /**
     * 保存状态到 localStorage
     * @param {string} key - 状态路径
     */
    persist(key) {
        const value = this.get(key);
        if (value !== undefined) {
            localStorage.setItem(`state_${key}`, JSON.stringify(value));
        }
    },

    /**
     * 从 localStorage 恢复状态
     * @param {string} key - 状态路径
     */
    restore(key) {
        const saved = localStorage.getItem(`state_${key}`);
        if (saved) {
            try {
                this.set(key, JSON.parse(saved));
            } catch (e) {
                console.error('Failed to restore state:', e);
            }
        }
    },

    /**
     * 清除持久化数据
     * @param {string} key - 状态路径
     */
    clearPersist(key) {
        localStorage.removeItem(`state_${key}`);
    },

    // ==================== 工具方法 ====================

    /**
     * 获取计算属性
     * @param {string} name - 计算属性名
     */
    compute(name) {
        const computedFn = this.computed[name];
        if (typeof computedFn === 'function') {
            return computedFn(this._state);
        }
        return undefined;
    },

    /**
     * 重置状态
     */
    reset() {
        this._state = {
            ...this._state,
            buddy: { name: '小豆', emoji: '🐱', emotion: 'idle', emotionDesc: '休息中~', message: '加载中...' },
            study: { isStudying: false, currentSubject: '数学', todayHours: 0, streakDays: 0, weekHours: 0, goalProgress: 0, goalReached: false },
            diary: { hasToday: false, todayEmotion: null, emotionCurve: [] },
            chat: { conversationId: null, history: [], isLoading: false },
        };
        this._notify('*', null, null);
    },
};

// 导出为全局变量
window.State = State;
