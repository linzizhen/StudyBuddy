/**
 * StudyPal API 调用层 v2.0
 * 封装所有后端 API 调用
 */

const API = {
    baseURL: '/api',

    async request(endpoint, options) {
        const url = this.baseURL + endpoint;
        const defaultOptions = {
            headers: { 'Content-Type': 'application/json' }
        };
        const config = Object.assign({}, defaultOptions, options || {});

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || data.message || '请求失败');
            }
            return data;
        } catch (error) {
            console.error('API Error [' + endpoint + ']:', error);
            throw error;
        }
    },

    get: function(endpoint, params) {
        let url = endpoint;
        if (params && typeof params === 'object') {
            const qs = Object.keys(params).map(function(k) {
                return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
            }).join('&');
            if (qs) url = endpoint + '?' + qs;
        }
        return this.request(url, { method: 'GET' });
    },

    post: function(endpoint, data) {
        return this.request(endpoint, { method: 'POST', body: data || {} });
    },

    put: function(endpoint, data) {
        return this.request(endpoint, { method: 'PUT', body: data || {} });
    },

    delete: function(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // 首页数据
    getHomeData: function() { return this.get('/home'); },

    // 搭子
    getBuddyStatus: function() { return this.get('/buddy/status'); },
    buddyChat: function(message, conversationId) {
        return this.post('/buddy/chat', { message: message, conversation_id: conversationId });
    },
    getBuddyProfile: function() { return this.get('/buddy/profile'); },
    updateBuddyProfile: function(profile) { return this.put('/buddy/profile', profile); },
    getBuddyMemory: function(topic) {
        return topic ? this.get('/buddy/memory', { topic: topic }) : this.get('/buddy/memory');
    },
    addBuddyMemory: function(memory) { return this.post('/buddy/memory', memory); },
    getCaringEvents: function() { return this.get('/buddy/caring'); },

    // 日记
    getDiaries: function(limit) {
        return this.get('/diary', { limit: limit || 30 });
    },
    getTodayDiary: function() { return this.get('/diary/today'); },
    saveDiary: function(diary) { return this.post('/diary', diary); },
    getEmotionCurve: function(days) { return this.get('/diary/emotions', { days: days || 7 }); },

    // 学习
    startStudy: function(subject) { return this.post('/study/start', { subject: subject || '学习' }); },
    stopStudy: function(subject) { return this.post('/study/stop', { subject: subject || '学习' }); },
    getStudyStats: function() { return this.get('/study/stats'); },
    getStudySessions: function() { return this.get('/study/sessions'); },

    // 任务
    getTasks: function(status) { return this.get('/tasks', { status: status || 'all' }); },
    addTask: function(task) { return this.post('/tasks', task); },
    updateTask: function(taskId, task) { return this.put('/tasks/' + taskId, task); },
    completeTask: function(taskId) { return this.post('/tasks/' + taskId + '/complete'); },
    deleteTask: function(taskId) { return this.delete('/tasks/' + taskId); },
    getTaskStats: function() { return this.get('/tasks/stats'); },

    // 成就
    getAchievements: function() { return this.get('/achievements'); },

    // 计划
    getStudyPlans: function() { return this.get('/plans'); },
    createStudyPlan: function(plan) { return this.post('/plans', plan); },

    // 洞察
    getInsightSummary: function() { return this.get('/insights/insight-summary'); },
    getInsightOverview: function(days) { return this.get('/insights/overview', { days: days || 30 }); },
    getStudyChart: function(days) { return this.get('/insights/study-chart', { days: days || 30 }); },
    getSubjectAnalysis: function(days) { return this.get('/insights/subject-analysis', { days: days || 30 }); },
    getEmotionChart: function(days) { return this.get('/insights/emotion-chart', { days: days || 30 }); },
    getWeeklyInsight: function() { return this.get('/insights/weekly-insight'); },
    getMonthlyReport: function() { return this.get('/insights/monthly-report'); },

    // 用户
    getMotto: function() { return this.get('/motto'); },
    setMotto: function(motto) { return this.post('/motto', { motto: motto }); },

    // 通知
    getNotificationSettings: function() { return this.get('/notification/settings'); },
    setNotificationSettings: function(settings) { return this.post('/notification/settings', settings); },
};

window.API = API;
