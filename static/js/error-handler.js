/**
 * StudyPal 前端错误处理与降级模块
 * 统一处理网络错误、AI 服务异常和降级策略
 */

// ==================== Toast 通知增强 ====================

const Toast = {
    queue: [],
    current: null,

    show(message, type = 'info', duration = 3000) {
        const id = `toast_${Date.now()}`;
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        const icons = {
            success: '\u2714',
            error: '\u2716',
            warning: '\u26A0',
            info: '\u2139'
        };

        toast.innerHTML = `<span class="toast-icon">${icons[type] || icons.info}</span> ${message}`;

        // 移除旧 Toast
        document.querySelectorAll('.toast').forEach(t => t.remove());

        document.body.appendChild(toast);

        // 触发重绘
        toast.offsetHeight;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return id;
    },

    success(message, duration) {
        return this.show(message, 'success', duration);
    },

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// 暴露到全局
window.Toast = Toast;


// ==================== 统一错误处理 ====================

const ErrorHandler = {
    // 错误类型
    ErrorTypes: {
        NETWORK: 'network',
        TIMEOUT: 'timeout',
        SERVER: 'server',
        AI_SERVICE: 'ai_service',
        VALIDATION: 'validation',
        UNKNOWN: 'unknown'
    },

    // 解析错误类型
    parseError(error) {
        const message = error?.message || String(error);

        if (message.includes('fetch') || message.includes('Failed to fetch') || message.includes('NetworkError')) {
            return this.ErrorTypes.NETWORK;
        }
        if (message.includes('timeout') || message.includes('Timeout')) {
            return this.ErrorTypes.TIMEOUT;
        }
        if (message.includes('Ollama') || message.includes('AI')) {
            return this.ErrorTypes.AI_SERVICE;
        }
        if (message.includes('status code') || message.includes('500') || message.includes('502')) {
            return this.ErrorTypes.SERVER;
        }
        if (message.includes('validate') || message.includes('required')) {
            return this.ErrorTypes.VALIDATION;
        }
        return this.ErrorTypes.UNKNOWN;
    },

    // 获取友好的错误消息
    getFriendlyMessage(errorType, originalMessage = '') {
        const messages = {
            [this.ErrorTypes.NETWORK]: '网络连接失败，请检查网络后重试',
            [this.ErrorTypes.TIMEOUT]: '请求超时，请稍后重试',
            [this.ErrorTypes.SERVER]: '服务器出错了，请稍后重试',
            [this.ErrorTypes.AI_SERVICE]: 'AI 服务暂时不可用，请稍后再试',
            [this.ErrorTypes.VALIDATION]: originalMessage || '输入有误，请检查后重试',
            [this.ErrorTypes.UNKNOWN]: '操作失败，请稍后重试'
        };
        return messages[errorType] || messages[this.ErrorTypes.UNKNOWN];
    },

    // 处理错误
    handle(error, context = '') {
        const errorType = this.parseError(error);
        const friendlyMessage = this.getFriendlyMessage(errorType, error?.message);

        console.error(`[ErrorHandler${context ? `][${context}]` : ''}`, {
            type: errorType,
            original: error,
            message: friendlyMessage
        });

        // 显示 Toast
        Toast.error(friendlyMessage);

        return {
            type: errorType,
            message: friendlyMessage,
            handled: true
        };
    }
};

window.ErrorHandler = ErrorHandler;


// ==================== 安全请求封装 ====================

async function safeRequest(requestFn, options = {}) {
    const {
        retries = 2,
        delay = 1000,
        context = '',
        showError = true
    } = options;

    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            return await requestFn();
        } catch (error) {
            const errorType = ErrorHandler.parseError(error);
            const isRetryable = [
                ErrorHandler.ErrorTypes.NETWORK,
                ErrorHandler.ErrorTypes.TIMEOUT,
                ErrorHandler.ErrorTypes.SERVER
            ].includes(errorType);

            // 最后一次尝试或不可重试的错误
            if (attempt === retries || !isRetryable) {
                if (showError) {
                    ErrorHandler.handle(error, context);
                }
                return null;
            }

            // 等待后重试（指数退避）
            const waitTime = delay * Math.pow(2, attempt);
            console.warn(`[safeRequest] Retry ${attempt + 1}/${retries} after ${waitTime}ms`);
            await new Promise(resolve => setTimeout(resolve, waitTime));
        }
    }

    return null;
}


// ==================== AI 服务降级策略 ====================

const AIFallback = {
    // 预设回复模板
    templates: {
        greeting: [
            '你好！今天学习状态怎么样？',
            '嗨！我在这里陪你一起加油~',
            '来啦！有什么想聊的吗？'
        ],
        encouragement: [
            '别急，慢慢来，你可以的！',
            '坚持就是胜利，继续加油！',
            '每一步都在靠近目标，再坚持一下！'
        ],
        rest: [
            '学累了就休息一下，效率比时长更重要~',
            '适当休息也是学习的一部分哦',
            '休息是为了走更远的路~'
        ],
        emotion: [
            '有什么心事可以和我聊聊',
            '我在这里听着呢',
            '不管怎样，我都陪着你'
        ],
        generic: [
            '嗯嗯，我理解',
            '继续说，我听着',
            '好的，我知道了'
        ]
    },

    // 根据关键词选择回复
    getFallbackResponse(message) {
        const msg = message.toLowerCase();

        if (/累|休息|停/.test(msg)) {
            return this.randomPick(this.templates.rest);
        }
        if (/难|不会|不懂/.test(msg)) {
            return this.randomPick(this.templates.encouragement);
        }
        if (/开心|好|棒|完成/.test(msg)) {
            return this.randomPick(this.templates.greeting);
        }
        if (/难过|伤心|沮丧/.test(msg)) {
            return this.randomPick(this.templates.emotion);
        }

        return this.randomPick(this.templates.generic);
    },

    randomPick(array) {
        return array[Math.floor(Math.random() * array.length)];
    }
};

window.AIFallback = AIFallback;


// ==================== 全局未处理异常捕获 ====================

window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason;
    const errorType = ErrorHandler.parseError(error);

    // 不显示重复的网络错误
    if (errorType === ErrorHandler.ErrorTypes.NETWORK) {
        Toast.error('网络连接失败，请检查网络后重试', 5000);
    } else if (errorType === ErrorHandler.ErrorTypes.AI_SERVICE) {
        Toast.error('AI 服务暂时不可用', 4000);
    }

    console.error('[Unhandled Promise Rejection]', error);
    event.preventDefault();
});

window.addEventListener('error', (event) => {
    // 忽略资源加载失败（如字体）
    const target = event.target;
    if (target && (target.tagName === 'LINK' || target.tagName === 'IMG')) {
        return;
    }
    console.error('[Global Error]', event.error);
});


// ==================== 导出 ====================

window.safeRequest = safeRequest;
