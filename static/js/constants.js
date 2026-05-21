/**
 * StudyPal 常量定义
 * 统一管理所有可复用的常量数据
 */

export const EMOTIONS = [
    { level: 1, label: '很难受', emoji: '😭', color: '#e74c3c' },
    { level: 2, label: '有点丧', emoji: '😢', color: '#f39c12' },
    { level: 3, label: '一般', emoji: '😐', color: '#95a5a6' },
    { level: 4, label: '还好', emoji: '😊', color: '#2ecc71' },
    { level: 5, label: '很开心', emoji: '😄', color: '#3498db' },
];

export const SUBJECTS = [
    { id: '数学', icon: '📐', name: '数学' },
    { id: '英语', icon: '📖', name: '英语' },
    { id: '政治', icon: '🏛️', name: '政治' },
    { id: '专业课', icon: '📚', name: '专业课' },
];

export const POMODORO_DURATION = 25;

export const PRIORITIES = {
    high: { label: '高', color: '#e74c3c' },
    medium: { label: '中', color: '#f39c12' },
    low: { label: '低', color: '#2ecc71' },
};

// 精简版导航：首页、搭话、记忆、日记、设置
export const NAV_ITEMS = [
    { page: 'home', icon: '🏠', label: '首页' },
    { page: 'chat', icon: '💬', label: '搭话' },
    { page: 'memory', icon: '🧠', label: '记忆' },
    { page: 'diary', icon: '📖', label: '日记' },
    { page: 'settings', icon: '⚙️', label: '设置' },
];

export const GOAL_OPTIONS = [6, 8, 10, 12];

export const FEELINGS = ['充实', '疲惫', '焦虑', '麻木', '充实+疲惫'];

/**
 * 根据情绪等级获取 emoji
 */
export function getEmotionEmoji(level) {
    const emotion = EMOTIONS.find(e => e.level === level);
    return emotion ? emotion.emoji : '📝';
}

/**
 * 根据情绪等级获取标签
 */
export function getEmotionLabel(level) {
    const emotion = EMOTIONS.find(e => e.level === level);
    return emotion ? emotion.label : '一般';
}

/**
 * 根据情绪标签获取 emoji
 */
export function getEmotionEmojiByLabel(label) {
    const map = { '很开心': '😄', '还好': '😊', '一般': '😐', '有点丧': '😢', '很难受': '😭' };
    return map[label] || '📝';
}

/**
 * 获取问候语
 */
export function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 6) return '夜深了';
    if (hour < 9) return '早上好';
    if (hour < 12) return '上午好';
    if (hour < 14) return '中午好';
    if (hour < 18) return '下午好';
    return '晚上好';
}

// 全局导出（兼容非模块脚本）
window.EMOTIONS = EMOTIONS;
window.SUBJECTS = SUBJECTS;
window.POMODORO_DURATION = POMODORO_DURATION;
window.PRIORITIES = PRIORITIES;
window.NAV_ITEMS = NAV_ITEMS;
window.GOAL_OPTIONS = GOAL_OPTIONS;
window.FEELINGS = FEELINGS;
window.getEmotionEmoji = getEmotionEmoji;
window.getEmotionLabel = getEmotionLabel;
window.getEmotionEmojiByLabel = getEmotionEmojiByLabel;
window.getGreeting = getGreeting;
