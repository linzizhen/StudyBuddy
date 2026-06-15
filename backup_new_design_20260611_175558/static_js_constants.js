/**
 * StudyPal 常量定义
 * 统一管理所有可复用的常量数据
 */

const EMOTIONS = [
    { level: 1, label: '很难受', emoji: '\u{1F622}', color: '#e74c3c' },
    { level: 2, label: '有点丧', emoji: '\u{1F61D}', color: '#f39c12' },
    { level: 3, label: '一般', emoji: '\u{1F610}', color: '#95a5a6' },
    { level: 4, label: '还好', emoji: '\u{1F642}', color: '#2ecc71' },
    { level: 5, label: '很开心', emoji: '\u{1F601}', color: '#3498db' },
];

const SUBJECTS = [
    { id: '数学', icon: '\u{1F4D0}', name: '数学' },
    { id: '英语', icon: '\u{1F4D6}', name: '英语' },
    { id: '政治', icon: '\u{1F3DB}', name: '政治' },
    { id: '专业课', icon: '\u{1F4DA}', name: '专业课' },
];

const POMODORO_DURATION = 25;

const PRIORITIES = {
    high: { label: '高', color: '#e74c3c' },
    medium: { label: '中', color: '#f39c12' },
    low: { label: '低', color: '#2ecc71' },
};

const NAV_ITEMS = [
    { page: 'home', icon: '\u{1F3E0}', label: '首页' },
    { page: 'chat', icon: '\u{1F4AC}', label: '搭话' },
    { page: 'memory', icon: '\u{1F9E0}', label: '记忆' },
    { page: 'diary', icon: '\u{1F4D6}', label: '日记' },
    { page: 'settings', icon: '\u{2699}', label: '设置' },
];

const GOAL_OPTIONS = [6, 8, 10, 12];

const FEELINGS = ['充实', '疲惫', '焦虑', '麻木', '充实+疲惫'];

function getEmotionEmoji(level) {
    var emotion = EMOTIONS.find(function(e) { return e.level === level; });
    return emotion ? emotion.emoji : '\u{1F4DD}';
}

function getEmotionLabel(level) {
    var emotion = EMOTIONS.find(function(e) { return e.level === level; });
    return emotion ? emotion.label : '一般';
}

function getEmotionEmojiByLabel(label) {
    var map = { '很开心': '\u{1F601}', '还好': '\u{1F642}', '一般': '\u{1F610}', '有点丧': '\u{1F61D}', '很难受': '\u{1F622}' };
    return map[label] || '\u{1F4DD}';
}

function getGreeting() {
    var hour = new Date().getHours();
    if (hour < 6) return '夜深了';
    if (hour < 9) return '早上好';
    if (hour < 12) return '上午好';
    if (hour < 14) return '中午好';
    if (hour < 18) return '下午好';
    return '晚上好';
}

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
