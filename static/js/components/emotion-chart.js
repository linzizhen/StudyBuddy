/**
 * StudyPal 情绪曲线可视化组件
 * 使用 SVG 渲染情绪曲线，支持周/月视图
 */

export class EmotionChart {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = {
            width: options.width || 400,
            height: options.height || 200,
            showLabels: options.showLabels !== false,
            showDots: options.showDots !== false,
            showGradient: options.showGradient !== false,
            animated: options.animated !== false,
            ...options
        };
        this.data = [];
    }

    /**
     * 设置数据
     * @param {Array} data - 情绪数据 [{date, level, label}]
     */
    setData(data) {
        this.data = data;
        this.render();
    }

    /**
     * 渲染图表
     */
    render() {
        if (!this.container || !this.data || this.data.length === 0) return;

        const { width, height, showLabels, showDots, showGradient, animated } = this.options;

        // 计算点位置
        const padding = { top: 20, right: 20, bottom: 30, left: 20 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        const validData = this.data.filter(d => d.level != null);
        if (validData.length < 2) {
            this.renderEmpty();
            return;
        }

        // 计算点坐标
        const points = validData.map((d, i) => {
            const x = padding.left + (i / (validData.length - 1)) * chartWidth;
            const y = padding.top + (1 - (d.level - 1) / 4) * chartHeight;
            return { x, y, ...d };
        });

        // 生成 SVG 路径
        const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
        const areaPath = `${linePath} L ${points[points.length - 1].x} ${height - padding.bottom} L ${padding.left} ${height - padding.bottom} Z`;

        // 颜色映射
        const getColor = (level) => {
            const colors = {
                1: '#e74c3c',
                2: '#f39c12',
                3: '#95a5a6',
                4: '#2ecc71',
                5: '#3498db'
            };
            return colors[level] || '#95a5a6';
        };

        const primaryColor = getColor(Math.round(validData.reduce((s, d) => s + d.level, 0) / validData.length));

        // 生成 SVG
        let svg = `
            <svg viewBox="0 0 ${width} ${height}" class="emotion-chart-svg" ${animated ? 'data-animated="true"' : ''}>
                <defs>
                    <linearGradient id="emotionGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="${primaryColor}" stop-opacity="0.4"/>
                        <stop offset="100%" stop-color="${primaryColor}" stop-opacity="0"/>
                    </linearGradient>
                </defs>
        `;

        // 渐变填充区域
        if (showGradient) {
            svg += `<path d="${areaPath}" fill="url(#emotionGradient)" class="emotion-area"/>`;
        }

        // 线条
        svg += `<path d="${linePath}" fill="none" stroke="${primaryColor}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="emotion-line"/>`;

        // 数据点
        if (showDots) {
            svg += points.map(p => {
                const emoji = this._getEmoji(p.level);
                return `
                    <g class="emotion-point" data-level="${p.level}" data-label="${p.label || ''}">
                        <circle cx="${p.x}" cy="${p.y}" r="6" fill="${getColor(p.level)}" stroke="white" stroke-width="2"/>
                        <text x="${p.x}" y="${p.y + 4}" text-anchor="middle" font-size="8">${emoji}</text>
                    </g>
                `;
            }).join('');
        }

        // 标签
        if (showLabels) {
            svg += points.map((p, i) => {
                const label = p.label || '';
                return `<text x="${p.x}" y="${height - 8}" text-anchor="middle" class="emotion-label">${label}</text>`;
            }).join('');
        }

        svg += '</svg>';

        this.container.innerHTML = svg;

        // 添加动画效果
        if (animated) {
            this._animate();
        }
    }

    /**
     * 渲染空状态
     */
    renderEmpty() {
        this.container.innerHTML = `
            <div class="emotion-chart-empty">
                <span class="empty-icon">📊</span>
                <span class="empty-text">暂无情绪数据</span>
            </div>
        `;
    }

    /**
     * 添加动画
     */
    _animate() {
        const line = this.container.querySelector('.emotion-line');
        const area = this.container.querySelector('.emotion-area');

        if (line) {
            const length = line.getTotalLength ? line.getTotalLength() : 1000;
            line.style.strokeDasharray = length;
            line.style.strokeDashoffset = length;
            line.style.transition = 'stroke-dashoffset 1.5s ease-out';
            requestAnimationFrame(() => {
                line.style.strokeDashoffset = '0';
            });
        }

        if (area) {
            area.style.opacity = '0';
            area.style.transition = 'opacity 1s ease-out 0.5s';
            requestAnimationFrame(() => {
                area.style.opacity = '1';
            });
        }
    }

    /**
     * 根据等级获取 emoji
     */
    _getEmoji(level) {
        const emojis = ['', '😭', '😢', '😐', '😊', '😄'];
        return emojis[level] || '😐';
    }

    /**
     * 更新数据并重新渲染
     */
    update(data) {
        this.setData(data);
    }

    /**
     * 销毁组件
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * 简易版情绪条形图（用于首页展示）
 */
export class EmotionBar {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = {
            barHeight: options.barHeight || 8,
            maxBars: options.maxBars || 7,
            showEmoji: options.showEmoji !== false,
            ...options
        };
        this.data = [];
    }

    setData(data) {
        this.data = data.slice(-this.options.maxBars);
        this.render();
    }

    render() {
        if (!this.container || !this.data || this.data.length === 0) return;

        const { barHeight, showEmoji } = this.options;
        const emojis = ['', '😭', '😢', '😐', '😊', '😄'];

        this.container.innerHTML = this.data.map(d => {
            const level = d.level || 3;
            const emoji = emojis[level] || '😐';
            const label = d.label || '';

            return `
                <div class="emotion-bar-item" title="${label}">
                    <div class="emotion-bar-emoji">${showEmoji ? emoji : ''}</div>
                    <div class="emotion-bar-track">
                        <div class="emotion-bar-fill level-${level}" style="height: ${barHeight}px; width: ${(level / 5) * 100}%"></div>
                    </div>
                    <div class="emotion-bar-date">${this._formatDate(d.date)}</div>
                </div>
            `;
        }).join('');
    }

    _formatDate(dateStr) {
        if (!dateStr) return '';
        const parts = dateStr.split('/');
        if (parts.length >= 2) {
            return `${parts[1]}/${parts[2]}`;
        }
        return dateStr;
    }

    update(data) {
        this.setData(data);
    }

    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}
