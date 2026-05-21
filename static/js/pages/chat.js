/**
 * StudyPal 聊天页面模块 v2.0
 * 有情绪的聊天搭子体验
 */

class ChatPage {
    constructor() {
        this.container = null;
        this.history = [];
        this.conversationId = null;
        this.currentEmotion = 'idle';
        this.isTyping = false;
    }

    mount(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        const pageEl = document.getElementById('page-chat');
        if (pageEl) {
            pageEl.classList.add('active');
        }
        this.loadHistory();
        this.updateBuddyEmotion();
        setTimeout(() => {
            document.getElementById('chat-input')?.focus();
        }, 100);
    }

    unmount() {
        const pageEl = document.getElementById('page-chat');
        if (pageEl) {
            pageEl.classList.remove('active');
        }
    }

    updateBuddyEmotion(emotion = 'idle') {
        this.currentEmotion = emotion;
        const avatar = document.getElementById('chat-buddy-avatar');
        if (avatar) {
            avatar.textContent = this.getEmotionEmoji(emotion);
            avatar.className = `chat-header-avatar emotion-${emotion}`;
        }
    }

    getEmotionEmoji(emotion) {
        const emotions = {
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
        return emotions[emotion] || '😊';
    }

    getEmotionColor(emotion) {
        const colors = {
            idle: 'var(--primary)',
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
        return colors[emotion] || 'var(--primary)';
    }

    loadHistory() {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        if (this.history.length === 0) {
            const buddyMsg = State?.get('buddy.message') || '你好！我是小豆，今天感觉怎么样？';
            const emotion = State?.get('buddy.emotion') || 'idle';
            container.innerHTML = `
                <div class="message buddy emotion-${emotion}">
                    <div class="msg-avatar emotion-${emotion}">${this.getEmotionEmoji(emotion)}</div>
                    <div class="msg-content">
                        <div class="msg-bubble emotion-bubble emotion-${emotion}">${buddyMsg}</div>
                        <div class="msg-time">${this.formatTime(new Date())}</div>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.history.map(msg => `
            <div class="message ${msg.role} emotion-${msg.emotion || 'idle'}">
                <div class="msg-avatar ${msg.role === 'buddy' ? 'emotion-' + (msg.emotion || 'idle') : ''}">${msg.role === 'buddy' ? this.getEmotionEmoji(msg.emotion || 'idle') : '我'}</div>
                <div class="msg-content">
                    <div class="msg-bubble emotion-bubble emotion-${msg.emotion || 'idle'}">${msg.content}</div>
                    <div class="msg-time">${msg.time}</div>
                </div>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    }

    addMessage(role, content, emotion = 'idle', time = null) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const t = time || this.formatTime(new Date());
        this.history.push({ role, content, emotion, time: t });

        const msgEl = document.createElement('div');
        msgEl.className = `message ${role} emotion-${emotion}`;
        msgEl.innerHTML = `
            <div class="msg-avatar ${role === 'buddy' ? 'emotion-' + emotion : ''}">${role === 'buddy' ? this.getEmotionEmoji(emotion) : '我'}</div>
            <div class="msg-content">
                <div class="msg-bubble emotion-bubble emotion-${emotion}">${content}</div>
                <div class="msg-time">${t}</div>
            </div>
        `;
        container.appendChild(msgEl);
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }

    showTyping(emotion = 'thinking') {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        let typingEl = container.querySelector('.message.typing');
        if (typingEl) {
            typingEl.querySelector('.msg-avatar').textContent = this.getEmotionEmoji(emotion);
            return;
        }

        typingEl = document.createElement('div');
        typingEl.className = `message buddy typing emotion-${emotion}`;
        typingEl.innerHTML = `
            <div class="msg-avatar emotion-${emotion}">${this.getEmotionEmoji(emotion)}</div>
            <div class="msg-content">
                <div class="msg-bubble emotion-bubble emotion-${emotion}">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(typingEl);
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }

    hideTyping() {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const typingEl = container.querySelector('.message.typing');
        if (typingEl) typingEl.remove();
    }

    updateLastMessageEmotion(emotion) {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const lastBuddyMsg = container.querySelector('.message.buddy:last-child');
        if (lastBuddyMsg) {
            lastBuddyMsg.className = `message buddy emotion-${emotion}`;
            const avatar = lastBuddyMsg.querySelector('.msg-avatar');
            if (avatar) {
                avatar.textContent = this.getEmotionEmoji(emotion);
                avatar.className = `msg-avatar emotion-${emotion}`;
            }
            const bubble = lastBuddyMsg.querySelector('.msg-bubble');
            if (bubble) {
                bubble.className = `msg-bubble emotion-bubble emotion-${emotion}`;
            }
        }
    }

    showSuggestions(suggestions) {
        const container = document.getElementById('chat-suggestions');
        if (!container || !suggestions || suggestions.length === 0) return;

        container.innerHTML = suggestions.map(s => `
            <button class="chat-suggestion-btn" onclick="App.sendSuggestion('${s.replace(/'/g, "\\'")}')">${s}</button>
        `).join('');
    }

    formatTime(date) {
        const h = String(date.getHours()).padStart(2, '0');
        const m = String(date.getMinutes()).padStart(2, '0');
        return `${h}:${m}`;
    }

    refresh() {
        this.loadHistory();
    }

    clear() {
        this.history = [];
        const container = document.getElementById('chat-messages');
        if (container) {
            container.innerHTML = '';
        }
    }
}

const chatPage = new ChatPage();
export default chatPage;
window.ChatPage = chatPage;
