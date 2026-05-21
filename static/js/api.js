/**
 * StudyPal API 调用层 v2.0
 * 封装所有后端 API 调用
 */

const API = {
    baseURL: '/api',

    /**
     * 通用请求方法
     * @param {string} endpoint - API 端点
     * @param {Object} options - 请求选项
     * @returns {Promise<Object>} 响应数据
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

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
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    /**
     * GET 请求
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    },

    /**
     * POST 请求
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, { method: 'POST', body: data });
    },

    /**
     * PUT 请求
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, { method: 'PUT', body: data });
    },

    /**
     * DELETE 请求
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // ==================== 首页 API ====================

    /**
     * 获取首页数据
     */
    async getHomeData() {
        return this.get('/home');
    },

    // ==================== 搭子 API ====================

    /**
     * 获取搭子状态
     */
    async getBuddyStatus() {
        return this.get('/buddy/status');
    },

    /**
     * 搭子对话
     * @param {string} message - 用户消息
     * @param {string} conversationId - 对话 ID
     */
    async buddyChat(message, conversationId = null) {
        return this.post('/buddy/chat', { message, conversation_id: conversationId });
    },

    /**
     * 获取搭子档案
     */
    async getBuddyProfile() {
        return this.get('/buddy/profile');
    },

    /**
     * 更新搭子档案
     * @param {Object} profile - 档案数据
     */
    async updateBuddyProfile(profile) {
        return this.put('/buddy/profile', profile);
    },

    /**
     * 获取搭子记忆
     * @param {string} topic - 搜索话题
     */
    async getBuddyMemory(topic = null) {
        return topic ? this.get('/buddy/memory', { topic }) : this.get('/buddy/memory');
    },

    /**
     * 添加搭子记忆
     * @param {Object} memory - 记忆数据
     */
    async addBuddyMemory(memory) {
        return this.post('/buddy/memory', memory);
    },

    /**
     * 获取主动关心事件
     */
    async getCaringEvents() {
        return this.get('/buddy/caring');
    },

    // ==================== 日记 API ====================

    /**
     * 获取日记列表
     * @param {number} limit - 返回数量
     */
    async getDiaries(limit = 30) {
        return this.get('/diary', { limit });
    },

    /**
     * 获取今日日记
     */
    async getTodayDiary() {
        return this.get('/diary/today');
    },

    /**
     * 保存日记
     * @param {Object} diary - 日记数据
     */
    async saveDiary(diary) {
        return this.post('/diary', diary);
    },

    /**
     * 获取情绪曲线
     * @param {number} days - 天数
     */
    async getEmotionCurve(days = 7) {
        return this.get('/diary/emotions', { days });
    },

    // ==================== 学习打卡 API ====================

    /**
     * 开始学习
     * @param {string} subject - 学习科目
     */
    async startStudy(subject = '学习') {
        return this.post('/study/start', { subject });
    },

    /**
     * 结束学习
     * @param {string} subject - 学习科目
     */
    async stopStudy(subject = '学习') {
        return this.post('/study/stop', { subject });
    },

    /**
     * 获取学习统计
     */
    async getStudyStats() {
        return this.get('/study/stats');
    },

    // ==================== 任务 API ====================

    /**
     * 获取任务列表
     * @param {string} status - 任务状态
     */
    async getTasks(status = 'all') {
        return this.get('/tasks', { status });
    },

    /**
     * 添加任务
     * @param {Object} task - 任务数据
     */
    async addTask(task) {
        return this.post('/tasks', task);
    },

    /**
     * 更新任务
     * @param {number} taskId - 任务 ID
     * @param {Object} task - 任务数据
     */
    async updateTask(taskId, task) {
        return this.put(`/tasks/${taskId}`, task);
    },

    /**
     * 完成任务
     * @param {number} taskId - 任务 ID
     */
    async completeTask(taskId) {
        return this.post(`/tasks/${taskId}/complete`);
    },

    /**
     * 删除任务
     * @param {number} taskId - 任务 ID
     */
    async deleteTask(taskId) {
        return this.delete(`/tasks/${taskId}`);
    },

    /**
     * 获取任务统计
     */
    async getTaskStats() {
        return this.get('/tasks/stats');
    },

    // ==================== 成就 API ====================

    /**
     * 获取成就数据
     */
    async getAchievements() {
        return this.get('/achievements');
    },

    // ==================== 计划 API ====================

    /**
     * 获取学习计划列表
     */
    async getStudyPlans() {
        return this.get('/plans');
    },

    /**
     * 创建学习计划
     * @param {Object} plan - 计划数据
     */
    async createStudyPlan(plan) {
        return this.post('/plans', plan);
    },

    // ==================== 用户设置 API ====================

    /**
     * 获取座右铭
     */
    async getMotto() {
        return this.get('/motto');
    },

    /**
     * 设置座右铭
     * @param {string} motto - 座右铭
     */
    async setMotto(motto) {
        return this.post('/motto', { motto });
    },

    // ==================== AI 对话 API ====================

    /**
     * AI 问答
     * @param {string} question - 问题
     * @param {string} conversationId - 对话 ID
     */
    async askAI(question, conversationId = null) {
        return this.post('/ask', { question, conversation_id: conversationId });
    },

    /**
     * 获取 AI 对话历史
     */
    async getAIHistory() {
        return this.get('/ai/history');
    },

    // ==================== 通知设置 API ====================

    /**
     * 获取通知设置
     */
    async getNotificationSettings() {
        return this.get('/notification/settings');
    },

    /**
     * 设置通知选项
     * @param {Object} settings - 通知设置
     */
    async setNotificationSettings(settings) {
        return this.post('/notification/settings', settings);
    },

    // ==================== 数据管理 API ====================

    /**
     * 导出所有数据（下载 ZIP 文件）
     */
    async exportData() {
        try {
            const response = await fetch(`${this.baseURL}/data/export`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/zip',
                }
            });

            if (!response.ok) {
                throw new Error('导出失败');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `studypal_backup_${new Date().toISOString().slice(0,10).replace(/-/g,'')}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            return { success: true };
        } catch (error) {
            console.error('导出失败:', error);
            throw error;
        }
    },
    // ==================== 洞察 API ====================

    /**
     * 获取搭子周记
     */
    async getWeeklyInsight() {
        return this.get('/insights/weekly-insight');
    },

    /**
     * 获取月度报告
     */
    async getMonthlyReport() {
        return this.get('/insights/monthly-report');
    },

    /**
     * 获取洞察摘要
     */
    async getInsightSummary() {
        return this.get('/insights/insight-summary');
    },
};

// 导出为全局变量
window.API = API;
