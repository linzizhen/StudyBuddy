/**
 * StudyPal 工具函数 v2.0
 */

const Utils = {
    // ==================== 格式化函数 ====================

    /**
     * 格式化时间
     * @param {Date|string|number} date - 日期
     * @param {string} format - 格式
     */
    formatTime(date, format = 'HH:mm') {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';

        const pad = (n) => String(n).padStart(2, '0');

        const tokens = {
            'HH': pad(d.getHours()),
            'mm': pad(d.getMinutes()),
            'ss': pad(d.getSeconds()),
            'YYYY': d.getFullYear(),
            'MM': pad(d.getMonth() + 1),
            'DD': pad(d.getDate()),
            'M': d.getMonth() + 1,
            'D': d.getDate(),
        };

        return format.replace(/HH|mm|ss|YYYY|MM|DD|M|D/g, (match) => tokens[match]);
    },

    /**
     * 获取相对时间描述
     * @param {Date|string|number} date - 日期
     */
    relativeTime(date) {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';

        const now = new Date();
        const diff = now - d;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;
        return this.formatTime(date, 'MM/DD');
    },

    /**
     * 格式化时长（秒转为 mm:ss 或 hh:mm:ss）
     * @param {number} seconds - 秒数
     */
    formatDuration(seconds) {
        if (seconds < 0) seconds = 0;

        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${pad(hours)}:${pad(mins)}:${pad(secs)}`;
        }
        return `${pad(mins)}:${pad(secs)}`;
    },

    /**
     * 格式化小时数
     * @param {number} hours - 小时数
     */
    formatHours(hours) {
        if (hours < 1) {
            return `${Math.round(hours * 60)}分钟`;
        }
        return `${hours.toFixed(1)}小时`;
    },

    /**
     * 格式化日期
     * @param {Date|string|number} date - 日期
     * @param {string} format - 格式
     */
    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';

        const pad = (n) => String(n).padStart(2, '0');

        const tokens = {
            'YYYY': d.getFullYear(),
            'MM': pad(d.getMonth() + 1),
            'DD': pad(d.getDate()),
            'M': d.getMonth() + 1,
            'D': d.getDate(),
        };

        return format.replace(/YYYY|MM|DD|M|D/g, (match) => tokens[match]);
    },

    // ==================== 验证函数 ====================

    /**
     * 验证邮箱
     */
    isEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    /**
     * 验证日期格式
     */
    isDate(str) {
        return /^\d{4}-\d{2}-\d{2}$/.test(str);
    },

    /**
     * 验证非空
     */
    isNotEmpty(value) {
        if (typeof value === 'string') return value.trim().length > 0;
        if (Array.isArray(value)) return value.length > 0;
        return value !== null && value !== undefined;
    },

    // ==================== DOM 操作 ====================

    /**
     * 创建元素
     * @param {string} tag - 标签名
     * @param {Object} attrs - 属性
     * @param {string|Array} children - 子元素
     */
    createElement(tag, attrs = {}, children = []) {
        const el = document.createElement(tag);

        for (const [key, value] of Object.entries(attrs)) {
            if (key === 'className') {
                el.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(el.style, value);
            } else if (key.startsWith('on') && typeof value === 'function') {
                el.addEventListener(key.slice(2).toLowerCase(), value);
            } else if (key === 'dataset') {
                for (const [dataKey, dataValue] of Object.entries(value)) {
                    el.dataset[dataKey] = dataValue;
                }
            } else {
                el.setAttribute(key, value);
            }
        }

        if (typeof children === 'string') {
            el.innerHTML = children;
        } else if (Array.isArray(children)) {
            children.forEach(child => {
                if (typeof child === 'string') {
                    el.appendChild(document.createTextNode(child));
                } else if (child instanceof Node) {
                    el.appendChild(child);
                }
            });
        }

        return el;
    },

    /**
     * 等待元素出现
     * @param {string} selector - 选择器
     * @param {number} timeout - 超时时间
     */
    async waitForElement(selector, timeout = 5000) {
        const element = document.querySelector(selector);
        if (element) return element;

        return new Promise((resolve, reject) => {
            const observer = new MutationObserver((mutations, obs) => {
                const el = document.querySelector(selector);
                if (el) {
                    obs.disconnect();
                    resolve(el);
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
            });

            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
            }, timeout);
        });
    },

    /**
     * 防抖
     * @param {Function} fn - 要防抖的函数
     * @param {number} delay - 延迟时间
     */
    debounce(fn, delay = 300) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn.apply(this, args), delay);
        };
    },

    /**
     * 节流
     * @param {Function} fn - 要节流的函数
     * @param {number} limit - 限制时间
     */
    throttle(fn, limit = 300) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                fn.apply(this, args);
                inThrottle = true;
                setTimeout(() => (inThrottle = false), limit);
            }
        };
    },

    // ==================== 动画工具 ====================

    /**
     * 平滑滚动到元素
     * @param {string|Element} target - 目标元素或选择器
     * @param {number} offset - 偏移量
     */
    scrollTo(target, offset = 0) {
        const el = typeof target === 'string' ? document.querySelector(target) : target;
        if (!el) return;

        const top = el.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
    },

    /**
     * 淡入元素
     * @param {Element} el - 目标元素
     * @param {number} duration - 动画时长
     */
    fadeIn(el, duration = 300) {
        el.style.opacity = 0;
        el.style.display = '';

        let start = null;
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            el.style.opacity = Math.min(progress / duration, 1);

            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    },

    /**
     * 淡出元素
     * @param {Element} el - 目标元素
     * @param {number} duration - 动画时长
     */
    fadeOut(el, duration = 300) {
        el.style.opacity = 1;

        let start = null;
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            el.style.opacity = Math.max(1 - progress / duration, 0);

            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                el.style.display = 'none';
            }
        };
        requestAnimationFrame(animate);
    },

    // ==================== 数据处理 ====================

    /**
     * 深拷贝
     * @param {*} obj - 要拷贝的对象
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj);
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (obj instanceof Object) {
            const copy = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    copy[key] = this.deepClone(obj[key]);
                }
            }
            return copy;
        }
        return obj;
    },

    /**
     * 生成随机 ID
     * @param {number} length - ID 长度
     */
    generateId(length = 8) {
        return Math.random().toString(36).substring(2, 2 + length);
    },

    /**
     * 随机选择数组元素
     * @param {Array} arr - 数组
     */
    randomPick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    },

    /**
     * 打乱数组
     * @param {Array} arr - 数组
     */
    shuffle(arr) {
        const result = [...arr];
        for (let i = result.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [result[i], result[j]] = [result[j], result[i]];
        }
        return result;
    },

    // ==================== 设备检测 ====================

    /**
     * 是否为移动设备
     */
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },

    /**
     * 是否为 iOS
     */
    isIOS() {
        return /iPhone|iPad|iPod/i.test(navigator.userAgent);
    },

    /**
     * 是否支持触摸
     */
    isTouchDevice() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },

    /**
     * 获取安全区域
     */
    getSafeArea() {
        const style = getComputedStyle(document.documentElement);
        return {
            top: parseInt(style.getPropertyValue('--safe-area-top') || '0'),
            bottom: parseInt(style.getPropertyValue('--safe-area-bottom') || '0'),
        };
    },
};

// 辅助函数
function pad(num) {
    return String(num).padStart(2, '0');
}

// 导出为全局变量
window.Utils = Utils;
