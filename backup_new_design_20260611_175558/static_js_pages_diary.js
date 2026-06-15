/**
 * 日记模块 v5 - 完整重构
 * 采用组件化设计，清晰状态管理
 */

class DiaryApp {
    constructor() {
        // 状态
        this.state = {
            todayEntry: null,
            entries: [],
            tags: [],
            streak: 0,
            currentMood: null,
            selectedTags: [],
            selectedWeather: '',
            images: [],
            isLoading: false,
            isSaving: false,
            filterOpen: false,
            filterEmotion: null,
            filterTag: null,
            searchKeyword: '',
            page: 0,
            hasMore: true
        };

        // 情绪配置
        this.moods = [
            { level: 1, emoji: '😢', label: '难过' },
            { level: 2, emoji: '😔', label: '低落' },
            { level: 3, emoji: '😌', label: '平静' },
            { level: 4, emoji: '🤔', label: '思考' },
            { level: 5, emoji: '😊', label: '愉快' },
            { level: 6, emoji: '😀', label: '开心' },
            { level: 7, emoji: '🥳', label: '兴奋' },
            { level: 8, emoji: '❤️', label: '感恩' },
            { level: 9, emoji: '🌈', label: '希望' },
            { level: 10, emoji: '😴', label: '疲惫' }
        ];

        this.defaultTags = ['学习', '生活', '运动', '旅行', '工作', '朋友', '家庭', '健康', '娱乐', '其他'];

        // 等待 DOM 就绪
        this._waitForDOM();
    }

    _waitForDOM() {
        const tryInit = () => {
            if (document.getElementById('diary-page')) {
                this._init();
            } else {
                setTimeout(tryInit, 30);
            }
        };
        tryInit();
    }

    async _init() {
        await this._loadData();
        this._bindEvents();
        this._render();
    }

    // ==================== 数据加载 ====================

    async _loadData() {
        this._setState({ isLoading: true });

        try {
            const [todayRes, listRes, statsRes, tagsRes] = await Promise.all([
                fetch('/api/diary/today').then(r => r.json()).catch(() => ({ success: true, entry: null, streak: 0 })),
                fetch('/api/diary?limit=20').then(r => r.json()).catch(() => ({ success: true, entries: [], streak: 0 })),
                fetch('/api/diary/stats').then(r => r.json()).catch(() => ({ success: true, streak: 0, tags: [] })),
                fetch('/api/diary/tags').then(r => r.json()).catch(() => ({ success: true, tags: [] }))
            ]);

            const todayEntry = todayRes.entry || null;
            const streak = statsRes.streak || todayRes.streak || 0;

            this._setState({
                todayEntry,
                entries: listRes.entries || [],
                streak,
                tags: tagsRes.tags || this.defaultTags,
                currentMood: todayEntry ? todayEntry.emotion_level : null,
                selectedTags: todayEntry?.tags || [],
                selectedWeather: todayEntry?.weather || '',
                images: todayEntry?.images || [],
                isLoading: false
            });

            // 回填表单
            if (todayEntry) {
                this._backfillForm(todayEntry);
            }
        } catch (e) {
            console.error('[DiaryApp] 加载失败:', e);
            this._setState({ isLoading: false });
            this._toast('加载失败，请刷新重试');
        }
    }

    _backfillForm(entry) {
        const titleEl = document.getElementById('diary-title');
        const contentEl = document.getElementById('diary-content');
        const charCountEl = document.getElementById('char-count');

        if (titleEl) titleEl.value = entry.title || '';
        if (contentEl) {
            contentEl.value = entry.content || '';
            if (charCountEl) charCountEl.textContent = (entry.content || '').length;
        }

        // 回填图片
        this._renderImages();
    }

    // ==================== 事件绑定 ====================

    _bindEvents() {
        // 心情选择
        document.getElementById('mood-grid')?.addEventListener('click', (e) => {
            const item = e.target.closest('.mood-item');
            if (item) {
                this._setMood(parseInt(item.dataset.level));
            }
        });

        // 标题输入
        document.getElementById('diary-title')?.addEventListener('input', (e) => {
            // 标题自动保存到草稿
            this._saveDraft();
        });

        // 内容输入
        document.getElementById('diary-content')?.addEventListener('input', (e) => {
            const charCount = document.getElementById('char-count');
            if (charCount) charCount.textContent = e.target.value.length;
            this._saveDraft();
        });

        // 天气选择
        document.getElementById('weather-selector')?.addEventListener('click', (e) => {
            const item = e.target.closest('.weather-item');
            if (item) {
                const weather = item.dataset.weather;
                this._setWeather(weather === this.state.selectedWeather ? '' : weather);
            }
        });

        // 图片上传
        document.getElementById('add-image-btn')?.addEventListener('click', () => {
            if (this.state.images.length >= 9) {
                this._toast('最多只能上传9张图片');
                return;
            }
            document.getElementById('image-file-input')?.click();
        });

        document.getElementById('image-file-input')?.addEventListener('change', (e) => {
            if (e.target.files?.length) {
                this._uploadImages(Array.from(e.target.files));
            }
        });

        // 标签点击
        document.getElementById('tag-manager')?.addEventListener('click', (e) => {
            const tagItem = e.target.closest('.tag-item');
            const addBtn = e.target.closest('.add-tag-btn');
            
            if (tagItem && !e.target.closest('.remove-tag')) {
                const tag = tagItem.dataset.tag;
                this._toggleTag(tag);
            } else if (addBtn) {
                this._showAddTagInput();
            }
        });

        // 搜索
        document.getElementById('search-input')?.addEventListener('input', (e) => {
            this._setState({ searchKeyword: e.target.value, page: 0 });
            this._debounceSearch();
        });

        // 筛选按钮
        document.getElementById('filter-btn')?.addEventListener('click', () => {
            this._toggleFilter();
        });

        // 加载更多
        document.getElementById('load-more-btn')?.addEventListener('click', () => {
            this._loadMore();
        });

        // 保存按钮
        document.getElementById('save-btn')?.addEventListener('click', () => {
            this._save();
        });

        // 日记列表点击（删除）
        document.getElementById('diary-list')?.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const id = deleteBtn.dataset.id;
                this._deleteEntry(id);
            }
        });

        // 删除图片
        document.getElementById('image-uploader')?.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-btn');
            if (removeBtn) {
                const index = parseInt(removeBtn.dataset.index);
                this._removeImage(index);
            }
        });

        // 点击空白关闭筛选
        document.addEventListener('click', (e) => {
            if (this.state.filterOpen && 
                !e.target.closest('.filter-panel') && 
                !e.target.closest('#filter-btn')) {
                this._setState({ filterOpen: false });
                this._renderFilterPanel();
            }
        });

        // 页面离开前保存草稿
        window.addEventListener('beforeunload', () => {
            this._saveDraft(true);
        });

        // 定时保存草稿
        setInterval(() => this._saveDraft(), 30000);
    }

    // ==================== 状态管理 ====================

    _setState(updates) {
        Object.assign(this.state, updates);
        this._render();
    }

    // ==================== 渲染 ====================

    _render() {
        this._renderHeader();
        this._renderMoods();
        this._renderTags();
        this._renderWeather();
        this._renderHistory();
        this._renderFilterPanel();
        this._updateSaveButton();
    }

    _renderHeader() {
        const now = new Date();
        const dateEl = document.getElementById('diary-current-date');
        const weekdayEl = document.getElementById('diary-current-weekday');
        const streakEl = document.getElementById('streak-count');

        if (dateEl) {
            dateEl.textContent = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
        }

        const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
        if (weekdayEl) weekdayEl.textContent = weekdays[now.getDay()];

        if (streakEl) streakEl.textContent = this.state.streak;

        // 更新问候语
        const greetingEl = document.getElementById('top-greeting');
        const hour = now.getHours();
        let greeting = '你好';
        if (hour >= 5 && hour < 9) greeting = '早上好';
        else if (hour >= 9 && hour < 12) greeting = '上午好';
        else if (hour >= 12 && hour < 14) greeting = '中午好';
        else if (hour >= 14 && hour < 18) greeting = '下午好';
        else if (hour >= 18 && hour < 22) greeting = '晚上好';
        else greeting = '夜深了';
        if (greetingEl) greetingEl.textContent = greeting;

        const topDateEl = document.getElementById('top-date');
        if (topDateEl) topDateEl.textContent = `${weekdays[now.getDay()]} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    _renderMoods() {
        const container = document.getElementById('mood-grid');
        if (!container) return;

        container.innerHTML = this.moods.map(mood => `
            <div class="mood-item ${this.state.currentMood === mood.level ? 'active' : ''}" 
                 data-level="${mood.level}">
                <div class="mood-emoji">${mood.emoji}</div>
                <div class="mood-label">${mood.label}</div>
            </div>
        `).join('');
    }

    _renderTags() {
        const container = document.getElementById('tag-manager');
        if (!container) return;

        const allTags = [...new Set([...this.defaultTags, ...this.state.tags])];

        container.innerHTML = allTags.map(tag => `
            <div class="tag-item ${this.state.selectedTags.includes(tag) ? 'active' : ''}" data-tag="${this._esc(tag)}">
                ${this._esc(tag)}
            </div>
        `).join('') + `
            <button class="add-tag-btn">+ 添加标签</button>
        `;
    }

    _renderWeather() {
        const container = document.getElementById('weather-selector');
        if (!container) return;

        container.querySelectorAll('.weather-item').forEach(item => {
            item.classList.toggle('active', item.dataset.weather === this.state.selectedWeather);
        });
    }

    _renderImages() {
        const container = document.getElementById('image-uploader');
        if (!container) return;

        const addBtn = document.getElementById('add-image-btn');

        // 清除现有图片（保留添加按钮）
        container.innerHTML = '';

        // 渲染已上传图片
        this.state.images.forEach((img, index) => {
            const div = document.createElement('div');
            div.className = 'image-preview';
            div.innerHTML = `
                <img src="${img}" alt="日记图片">
                <button class="remove-btn" data-index="${index}">&#10005;</button>
            `;
            container.appendChild(div);
        });

        // 重新添加添加按钮
        container.appendChild(addBtn);
        addBtn.style.display = this.state.images.length >= 9 ? 'none' : '';
    }

    _renderHistory() {
        const container = document.getElementById('diary-list');
        const loadMoreEl = document.getElementById('load-more');
        if (!container) return;

        if (this.state.entries.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">&#128221;</div>
                    <div class="empty-title">还没有日记</div>
                    <div class="empty-desc">从今天开始记录吧~</div>
                </div>
            `;
            if (loadMoreEl) loadMoreEl.style.display = 'none';
            return;
        }

        container.innerHTML = this.state.entries.map(entry => this._renderDiaryCard(entry)).join('');
        if (loadMoreEl) loadMoreEl.style.display = this.state.hasMore ? '' : 'none';
    }

    _renderDiaryCard(entry) {
        const date = new Date(entry.date);
        const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
        const contentPreview = entry.content 
            ? entry.content.substring(0, 80) + (entry.content.length > 80 ? '...' : '')
            : (entry.title || '点击查看详情');

        const mood = this.moods.find(m => m.level === entry.emotion_level) || this.moods[4];

        return `
            <div class="diary-card level-${entry.emotion_level} animate-fadeIn">
                <div class="diary-card-header">
                    <div class="diary-card-date">${dateStr}</div>
                    <div class="diary-card-mood">
                        <span class="emoji">${mood.emoji}</span>
                        <span>${mood.label}</span>
                    </div>
                </div>
                ${entry.title ? `<div class="diary-card-title">${this._esc(entry.title)}</div>` : ''}
                <div class="diary-card-content">${this._esc(contentPreview)}</div>
                <div class="diary-card-footer">
                    <div class="diary-card-tags">
                        ${entry.tags?.map(tag => `<span class="diary-card-tag">${this._esc(tag)}</span>`).join('') || ''}
                    </div>
                    <div class="diary-card-actions">
                        <button class="diary-card-action delete-btn" data-id="${entry.id}">删除</button>
                    </div>
                </div>
            </div>
        `;
    }

    _renderFilterPanel() {
        const panel = document.getElementById('filter-panel');
        const filterBtn = document.getElementById('filter-btn');

        if (panel) panel.classList.toggle('show', this.state.filterOpen);
        if (filterBtn) filterBtn.classList.toggle('active', this.state.filterOpen);

        // 渲染筛选选项
        const emotionsContainer = document.getElementById('filter-emotions');
        if (emotionsContainer) {
            emotionsContainer.innerHTML = this.moods.map(m => `
                <div class="filter-option ${this.state.filterEmotion === m.level ? 'active' : ''}" 
                     data-emotion="${m.level}">
                    ${m.emoji} ${m.label}
                </div>
            `).join('');
        }

        const tagsContainer = document.getElementById('filter-tags');
        if (tagsContainer) {
            const allTags = [...new Set([...this.defaultTags, ...this.state.tags])];
            tagsContainer.innerHTML = allTags.map(tag => `
                <div class="filter-option ${this.state.filterTag === tag ? 'active' : ''}" 
                     data-tag="${this._esc(tag)}">
                    ${this._esc(tag)}
                </div>
            `).join('');
        }

        // 绑定筛选点击
        emotionsContainer?.addEventListener('click', (e) => {
            const opt = e.target.closest('.filter-option');
            if (opt) {
                const level = parseInt(opt.dataset.emotion);
                this._setState({ 
                    filterEmotion: this.state.filterEmotion === level ? null : level,
                    page: 0
                });
                this._searchEntries();
            }
        });

        tagsContainer?.addEventListener('click', (e) => {
            const opt = e.target.closest('.filter-option');
            if (opt) {
                const tag = opt.dataset.tag;
                this._setState({ 
                    filterTag: this.state.filterTag === tag ? null : tag,
                    page: 0
                });
                this._searchEntries();
            }
        });
    }

    _updateSaveButton() {
        const btn = document.getElementById('save-btn');
        const btnText = document.getElementById('save-btn-text');

        if (btn) {
            btn.disabled = this.state.isSaving;
            btn.classList.toggle('saving', this.state.isSaving);
        }

        const isUpdate = !!this.state.todayEntry;
        if (btnText) btnText.textContent = isUpdate ? '更新日记' : '保存日记';
    }

    // ==================== 交互逻辑 ====================

    _setMood(level) {
        this._setState({ currentMood: level });
    }

    _setWeather(weather) {
        this._setState({ selectedWeather: weather });
    }

    _toggleTag(tag) {
        const tags = this.state.selectedTags.includes(tag)
            ? this.state.selectedTags.filter(t => t !== tag)
            : [...this.state.selectedTags, tag];
        this._setState({ selectedTags: tags });
    }

    async _showAddTagInput() {
        const tag = prompt('请输入新标签名称：');
        if (tag && tag.trim()) {
            const newTag = tag.trim();
            // 添加到标签列表
            if (!this.state.tags.includes(newTag)) {
                const newTags = [...this.state.tags, newTag];
                this._setState({ tags: newTags });
            }
            // 选中新标签
            if (!this.state.selectedTags.includes(newTag)) {
                this._setState({ selectedTags: [...this.state.selectedTags, newTag] });
            }
            // 保存到服务器
            try {
                await fetch('/api/diary/tags', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this._getToken()}`
                    },
                    body: JSON.stringify({ tag: newTag })
                });
            } catch (e) {
                console.error('[DiaryApp] 保存标签失败:', e);
            }
        }
    }

    async _uploadImages(files) {
        const maxFiles = 9 - this.state.images.length;
        const filesToUpload = files.slice(0, maxFiles);

        for (const file of filesToUpload) {
            if (file.size > 5 * 1024 * 1024) {
                this._toast(`${file.name} 超过5MB限制`);
                continue;
            }

            try {
                const formData = new FormData();
                formData.append('image', file);

                const res = await fetch('/api/diary/upload-image', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this._getToken()}`
                    },
                    body: formData
                });

                const data = await res.json();
                if (data.success) {
                    this._setState({ images: [...this.state.images, data.image_url] });
                    this._renderImages();
                } else {
                    this._toast(data.error || '上传失败');
                }
            } catch (e) {
                console.error('[DiaryApp] 图片上传失败:', e);
                this._toast('图片上传失败');
            }
        }
    }

    _removeImage(index) {
        const images = [...this.state.images];
        images.splice(index, 1);
        this._setState({ images });
        this._renderImages();
    }

    _toggleFilter() {
        this._setState({ filterOpen: !this.state.filterOpen });
    }

    _debounceSearch() {
        clearTimeout(this._searchTimer);
        this._searchTimer = setTimeout(() => this._searchEntries(), 300);
    }

    async _searchEntries() {
        const { searchKeyword, filterEmotion, filterTag, page } = this.state;

        try {
            const params = new URLSearchParams();
            if (searchKeyword) params.set('keyword', searchKeyword);
            if (filterEmotion) params.set('emotion', filterEmotion);
            if (filterTag) params.set('tag', filterTag);
            params.set('limit', 20);
            params.set('offset', page * 20);

            const res = await fetch(`/api/diary?${params.toString()}`);
            const data = await res.json();

            this._setState({
                entries: data.entries || [],
                hasMore: (data.entries?.length || 0) >= 20
            });
        } catch (e) {
            console.error('[DiaryApp] 搜索失败:', e);
        }
    }

    async _loadMore() {
        const { searchKeyword, filterEmotion, filterTag, page } = this.state;
        const nextPage = page + 1;

        try {
            const params = new URLSearchParams();
            if (searchKeyword) params.set('keyword', searchKeyword);
            if (filterEmotion) params.set('emotion', filterEmotion);
            if (filterTag) params.set('tag', filterTag);
            params.set('limit', 20);
            params.set('offset', nextPage * 20);

            const res = await fetch(`/api/diary?${params.toString()}`);
            const data = await res.json();

            this._setState({
                entries: [...this.state.entries, ...(data.entries || [])],
                page: nextPage,
                hasMore: (data.entries?.length || 0) >= 20
            });
        } catch (e) {
            console.error('[DiaryApp] 加载更多失败:', e);
        }
    }

    // ==================== 保存 ====================

    async _save() {
        if (this.state.isSaving) {
            this._toast('正在保存...');
            return;
        }

        const title = document.getElementById('diary-title')?.value.trim() || '';
        const content = document.getElementById('diary-content')?.value.trim() || '';

        if (!content && !title) {
            this._toast('请写点什么吧~');
            return;
        }

        if (!this.state.currentMood) {
            this._toast('请选择今天的心情~');
            return;
        }

        this._setState({ isSaving: true });

        try {
            const res = await fetch('/api/diary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this._getToken()}`
                },
                body: JSON.stringify({
                    emotion_level: this.state.currentMood,
                    title,
                    content,
                    images: this.state.images,
                    tags: this.state.selectedTags,
                    weather: this.state.selectedWeather
                })
            });

            const data = await res.json();

            if (data.success) {
                this._setState({
                    todayEntry: data.entry,
                    streak: data.streak,
                    isSaving: false
                });

                const action = data.action === 'create' ? '已保存' : '已更新';
                this._toast(`✅ 日记${action}~`, 'success');

                // 清空草稿
                this._clearDraft();

                // 刷新历史列表
                await this._loadData();
            } else {
                this._toast(data.error || '保存失败');
                this._setState({ isSaving: false });
            }
        } catch (e) {
            console.error('[DiaryApp] 保存失败:', e);
            this._toast('保存失败，请重试');
            this._setState({ isSaving: false });
        }
    }

    async _deleteEntry(entryId) {
        if (!confirm('确定要删除这篇日记吗？')) return;

        try {
            const res = await fetch(`/api/diary/${entryId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this._getToken()}`
                }
            });

            const data = await res.json();

            if (data.success) {
                this._toast('🗑️ 日记已删除', 'success');

                // 如果删除的是今日日记，重置状态
                if (this.state.todayEntry?.id === entryId) {
                    this._setState({
                        todayEntry: null,
                        currentMood: null,
                        selectedTags: [],
                        selectedWeather: '',
                        images: []
                    });
                    // 清空表单
                    const titleEl = document.getElementById('diary-title');
                    const contentEl = document.getElementById('diary-content');
                    if (titleEl) titleEl.value = '';
                    if (contentEl) contentEl.value = '';
                    const charCountEl = document.getElementById('char-count');
                    if (charCountEl) charCountEl.textContent = '0';
                    this._renderImages();
                }

                // 刷新列表
                await this._loadData();
            } else {
                this._toast(data.error || '删除失败');
            }
        } catch (e) {
            console.error('[DiaryApp] 删除失败:', e);
            this._toast('删除失败');
        }
    }

    // ==================== 草稿 ====================

    _saveDraft(silent = false) {
        const title = document.getElementById('diary-title')?.value || '';
        const content = document.getElementById('diary-content')?.value || '';

        localStorage.setItem('diary_draft', JSON.stringify({
            title,
            content,
            mood: this.state.currentMood,
            tags: this.state.selectedTags,
            weather: this.state.selectedWeather,
            images: this.state.images,
            savedAt: Date.now()
        }));
    }

    _loadDraft() {
        try {
            const draft = localStorage.getItem('diary_draft');
            if (!draft) return;

            const data = JSON.parse(draft);
            const savedAt = new Date(data.savedAt);
            const now = new Date();

            // 草稿超过24小时清除
            if (now - savedAt > 24 * 60 * 60 * 1000) {
                this._clearDraft();
                return;
            }

            // 如果没有今日日记，恢复草稿
            if (!this.state.todayEntry && (data.title || data.content)) {
                const titleEl = document.getElementById('diary-title');
                const contentEl = document.getElementById('diary-content');
                const charCountEl = document.getElementById('char-count');

                if (titleEl) titleEl.value = data.title || '';
                if (contentEl) {
                    contentEl.value = data.content || '';
                    if (charCountEl) charCountEl.textContent = (data.content || '').length;
                }

                if (data.mood) this._setState({ currentMood: data.mood });
                if (data.tags?.length) this._setState({ selectedTags: data.tags });
                if (data.weather) this._setState({ selectedWeather: data.weather });
                if (data.images?.length) {
                    this._setState({ images: data.images });
                    this._renderImages();
                }
            }
        } catch (e) {
            console.error('[DiaryApp] 加载草稿失败:', e);
        }
    }

    _clearDraft() {
        localStorage.removeItem('diary_draft');
    }

    // ==================== 工具 ====================

    _getToken() {
        return localStorage.getItem('token') || App?.token || '';
    }

    _toast(msg, type = '') {
        const toast = document.getElementById('diary-toast');
        if (toast) {
            toast.textContent = msg;
            toast.className = 'diary-toast show' + (type ? ' ' + type : '');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2500);
        }
    }

    _esc(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

window.DiaryApp = DiaryApp;
