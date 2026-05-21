/**
 * 首页页面模块
 */

// constants.js 已通过全局方式加载，无需 import

class HomePage {
    constructor() {
        this.container = null;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-home');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadData();
    }

    unmount() {
        const pageEl = document.getElementById('page-home');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    async loadData() {
        try {
            const res = await fetch('/api/home').then(r => r.json());
            if (!res.success) return;

            const data = res.data;

            // 更新搭子信息
            this._updateBuddy(data.buddy);
            // 更新倒计时
            this._updateCountdown(data.profile);
            // 更新搭子消息
            this._updateBuddyMessage(data);
            // 更新关心事件
            this._updateCaring(data.caring_events);
            // 更新学习统计
            this._updateStats(data.study);
            // 更新进度
            this._updateProgress(data.study);
            // 更新今日情绪
            this._updateEmotion(data.diary);

        } catch (e) {
            console.error('加载首页数据失败', e);
        }
    }

    _updateBuddy(buddy) {
        if (!buddy) return;
        const setText = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setText('buddy-avatar', buddy.role_emoji || buddy.emoji);
        setText('buddy-name', buddy.name);
        setText('buddy-emotion-emoji', buddy.emoji);
        setText('buddy-emotion-desc', buddy.emotion_desc);
        setText('chat-buddy-avatar', buddy.role_emoji || buddy.emoji);
        setText('chat-buddy-name', buddy.name);

        // 更新搭子等级
        if (buddy.level !== undefined) {
            setText('buddy-level-badge', `Lv.${buddy.level}`);
            setText('buddy-level-name', buddy.level_name || '初级搭子');
        }

        // 更新聊天页面角色信息
        setText('chat-buddy-personality', buddy.personality || '在线');

        // 更新行动按钮文字
        const actionText = document.getElementById('buddy-action-text');
        if (actionText) actionText.textContent = `🌟 和${buddy.name}聊聊`;
    }

    _updateCountdown(profile) {
        const el = document.getElementById('countdown');
        if (!el) return;
        if (profile.days_remaining >= 0) {
            el.textContent = `考研倒计时 ${profile.days_remaining} 天`;
            el.style.color = 'var(--primary)';
        } else {
            el.textContent = '设置目标';
            el.style.color = 'var(--text-muted)';
        }
    }

    _updateBuddyMessage(data) {
        const hour = new Date().getHours();
        const study = data.study;
        let msg = '感觉怎么样？今天有什么计划？';

        if (hour >= 22 || hour < 6) {
            if (study.today_hours > 8) {
                msg = '已经这么晚了，你今天学习很久了，早点休息吧~';
            } else {
                msg = '夜深了，还在学习吗？注意身体哦。';
            }
        } else if (!study.is_studying && study.today_hours === 0) {
            if (hour < 9) msg = '新的一天开始了，今天有什么学习计划吗？';
            else msg = '今天还没开始学习呢，要开始了吗？';
        } else if (study.is_studying) {
            msg = '加油！你在学习中，我会一直陪着你。';
        } else if (study.goal_progress?.reached) {
            msg = '今天的任务完成了！你真的很棒~';
        } else if (study.today_hours > 5) {
            msg = `今天已经学习了 ${study.today_hours.toFixed(1)} 小时，辛苦了！`;
        }

        const el = document.getElementById('buddy-message');
        if (el) el.textContent = msg;
    }

    _updateCaring(events) {
        const section = document.getElementById('caring-section');
        const msgEl = document.getElementById('caring-message');
        if (!section) return;

        if (events && events.length > 0) {
            const event = events[0];
            if (msgEl) msgEl.textContent = event.message || event;
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    }

    _updateStats(study) {
        if (!study) return;
        const setText = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };
        setText('stat-today-hours', study.today_hours.toFixed(1) + 'h');
        setText('stat-streak', study.streak_days);
        setText('stat-week-hours', study.week_hours.toFixed(0) + 'h');
    }

    _updateProgress(study) {
        if (!study) return;
        const progress = study.goal_progress;
        if (!progress) return;

        const progressPct = Math.round(progress.progress);
        const fill = document.getElementById('progress-fill');
        const value = document.getElementById('progress-value');
        const label = document.getElementById('progress-label');

        if (fill) fill.style.width = `${progressPct}%`;
        if (value) value.textContent = `${progressPct}%`;
        if (label) {
            label.textContent = progress.reached ? '目标达成！🎉' : `${progress.today_minutes.toFixed(0)} / ${progress.goal_minutes} 分钟`;
        }
    }

    _updateEmotion(diary) {
        if (!diary) return;
        if (diary.has_today && diary.today_emotion) {
            const emojiEl = document.getElementById('emotion-emoji');
            const labelEl = document.getElementById('emotion-label');
            const hintEl = document.getElementById('emotion-hint');

            if (emojiEl) emojiEl.textContent = getEmotionEmojiByLabel(diary.today_emotion);
            if (labelEl) labelEl.textContent = `今日心情：${diary.today_emotion}`;
            if (hintEl) hintEl.textContent = '点击查看历史';
        }
    }

    refresh() {
        this.loadData();
    }
}

const homePage = new HomePage();
export default homePage;
window.HomePage = homePage;
