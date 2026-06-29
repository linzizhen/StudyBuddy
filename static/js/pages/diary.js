class DiaryApp {
  constructor() {
    this.state = {
      isLoading: false,
      todayEntry: null,
      entries: [],
      streak: 0,
      tags: ['复习', '做题', '听课', '背诵'],   // 4 个预设（前端固定，不同步到后端）
      customTags: [],                           // 用户自定义标签（同步到后端）
      moodSlots: [],        // 后端 8 个槽位（5 预设 + 最多 3 自定义）
      currentMood: null,    // 当前选中 mood_id
      currentMoodValue: null,
      selectedTags: [],
      images: [],           // [{url, uploading?}]
      isDirty: false,
      deleteTargetId: null,
      deleteTargetTitle: '',
      activeFilter: 'all',
      pendingNavigation: null,
    };

    // emoji 选择器候选（覆盖常见心情场景）
    this.emojiOptions = [
      '😊','😄','😁','🥰','😘','🤩','😎','🥳',
      '😌','🙂','😉','😋','😏','🤗','😇','🤔',
      '😐','😑','😶','🤨','😴','🥱','😪','😜',
      '😢','😭','😔','😞','😟','😰','😨','😱',
      '😡','😠','🤬','😤','🥵','🥶','🤯','😵',
      '🤒','🤕','🤧','😷','🤢','🤮','🤠','🥺',
      '😈','👻','💀','🤖','💪','👍','👎','✌️',
      '🌟','⭐','🔥','💧','🌈','☀️','🌙','⚡',
    ];

    this.EMOJI_LABEL_HINT = {
      '😢':'难过','😭':'难过','😔':'低落','😞':'低落','😟':'低落',
      '😰':'焦虑','😨':'害怕','😱':'惊恐',
      '😴':'疲惫','🥱':'疲惫','😪':'疲惫',
      '😐':'一般','😑':'一般','😶':'一般',
      '🤔':'思考','😌':'平静','🙂':'不错','😉':'轻松',
      '😊':'开心','😄':'开心','😁':'开心','🥰':'幸福','😘':'幸福',
      '🤩':'兴奋','🥳':'兴奋','😎':'自信',
      '🤒':'难受','🤕':'不适','🤧':'不适','😷':'不适','🤢':'不适',
      '😡':'愤怒','😠':'愤怒','🤬':'愤怒','😤':'不甘',
      '🥵':'燥热','🥶':'寒冷','🤯':'震惊','😵':'迷茫',
      '🤠':'调皮','🥺':'委屈','😈':'坏笑','👻':'古怪',
      '💀':'崩溃','🤖':'冷酷','💪':'自信','👍':'认可','👎':'否定',
      '🌟':'闪耀','⭐':'珍贵','🔥':'热血','💧':'冷静',
      '🌈':'多彩','☀️':'阳光','🌙':'夜晚','⚡':'灵感',
    };

    // 心情格：固定 8 格（6 系统预设 + 2 自定义槽位）
    this.fallbackMoods = [
      { id: 'happy', emoji: '😊', label: '开心', value: 5, isSystem: true },
      { id: 'calm', emoji: '😌', label: '平静', value: 4, isSystem: true },
      { id: 'tired', emoji: '😴', label: '疲惫', value: 3, isSystem: true },
      { id: 'anxious', emoji: '😰', label: '焦虑', value: 2, isSystem: true },
      { id: 'sad', emoji: '😢', label: '难过', value: 1, isSystem: true },
      { id: 'excited', emoji: '🤩', label: '兴奋', value: 6, isSystem: true },
      null,  // 自定义槽位 1
      null   // 自定义槽位 2
    ];
    // 记录自定义心情添加顺序，用于 LRU 淘汰最旧
    this.customMoods = [];
  }

  init() {
    this._renderMoods();
    this._renderTags();
    this._renderWeekly();
    this._updateCharCount();
    this._bindEvents();
    this._loadAll();
  }

  // ==================== 心情渲染 ====================

  _renderMoods() {
    const grid = document.getElementById('mood-grid');
    const moodAdd = document.getElementById('mood-add');
    if (!grid) return;
    const moods = this.fallbackMoods;
    grid.innerHTML = moods.map((m, i) => {
      if (!m) {
        return `<div class="mood-item mood-placeholder" data-index="${i}" title="添加自定义心情"></div>`;
      }
      const active = this.state.currentMood === m.id ? 'active' : '';
      const customDot = !m.isSystem ? '<span class="mood-custom-dot" title="自定义">●</span>' : '';
      return `<div class="mood-item ${active}" data-mood-id="${m.id}" data-value="${m.value}" title="${m.label}">
        <span class="mood-emoji">${m.emoji}</span>
        <span class="mood-label">${m.label}${customDot}</span>
      </div>`;
    }).join('');

    grid.querySelectorAll('.mood-item:not(.mood-placeholder)').forEach(item => {
      item.addEventListener('click', () => {
        grid.querySelectorAll('.mood-item').forEach(el => el.classList.remove('active'));
        item.classList.add('active');
        this.state.currentMood = item.dataset.moodId;
        this.state.currentMoodValue = parseInt(item.dataset.value);
        this.state.isDirty = true;
        this._renderWeekly();
      });
    });

    grid.querySelectorAll('.mood-placeholder').forEach(item => {
      item.addEventListener('click', () => this._addCustomMood());
    });

    // 文字链接点击 → 打开弹窗（每次重渲需重新绑定，因 innerHTML 不会清空 #mood-add，但安全起见）
    if (moodAdd && !moodAdd.dataset.bound) {
      moodAdd.addEventListener('click', () => this._addCustomMood());
      moodAdd.style.cursor = 'pointer';
      moodAdd.dataset.bound = '1';
    }
  }

  _addCustomMood() {
    // 不管 8 格是否满，无条件打开弹窗
    this._pendingCustomMood = null;
    this._openModal('custom-mood-modal');
    this._renderEmojiGrid();
    document.getElementById('custom-mood-name').value = '';
    const levelInput = document.getElementById('custom-mood-level');
    if (levelInput) levelInput.value = 5;
    document.getElementById('custom-mood-level-display').textContent = '5';
    this._bindCustomMoodEventsOnce();
  }

  _renderEmojiGrid() {
    const grid = document.getElementById('emoji-grid');
    if (!grid) return;

    // 70% 表情 + 30% 其他
    const faceEmojis = [
      '😊','😂','🥰','😎','🤗','😋','🤩','🥳','😇','🤠',
      '🤡','👻','👽','🤖','😍','🤔','😏','😌','😜','🤪',
      '😬','🥺','😭','😤','😠','🤬','😷','🤒','🤕','🤢',
      '🤮','🥴','😵','🤯','🤓','🧐','😕','😟','🙁','☹️',
      '😮','😯','😲','😳','🥱','😴','🤤','😪','😈','👿',
      '💀','☠️','😱','😨','😰','🥵','🥶','😡',
    ];
    const otherEmojis = [
      '🎉','💪','🔥','⭐','🌈','💖','🎊','✨','💯','🏆',
      '🌟','💫','🎈','🎁','💐','🌸','❤️','🧡','💛','💚',
      '💙','💜','🖤','🤍','🍎','🍊','🍋','🍌','🍉','🍇',
      '🍓','🫐','🌞','🌝','🌛','🌜','☄️','🎯','🎨','🎬',
    ];

    // 80 个 = 56 表情 + 24 其他（70/30 比例）
    const emojis = [
      ...faceEmojis.slice(0, 56),
      ...otherEmojis.slice(0, 24),
    ];

    grid.innerHTML = emojis.map(emoji =>
      `<div class="emoji-option" data-emoji="${emoji}">${emoji}</div>`
    ).join('');

    grid.querySelectorAll('.emoji-option').forEach(el => {
      el.addEventListener('click', (e) => {
        grid.querySelectorAll('.emoji-option').forEach(o => o.classList.remove('selected'));
        e.currentTarget.classList.add('selected');
        this._pendingCustomMood = { emoji: e.currentTarget.dataset.emoji };
      });
    });
  }

  _bindCustomMoodEventsOnce() {
    if (this._customMoodEventsBound) return;
    this._customMoodEventsBound = true;

    const close = () => this._closeModal('custom-mood-modal');
    document.getElementById('custom-mood-close')?.addEventListener('click', close);
    document.getElementById('btn-cancel-custom-mood')?.addEventListener('click', close);

    document.getElementById('custom-mood-level')?.addEventListener('input', (e) => {
      document.getElementById('custom-mood-level-display').textContent = e.target.value;
    });

    document.getElementById('btn-confirm-custom-mood')?.addEventListener('click', () => {
      this._confirmAddCustomMood();
    });
  }

  _confirmAddCustomMood() {
    const name = document.getElementById('custom-mood-name')?.value.trim();
    if (!name) { this._toast('请输入心情名称'); return; }
    if (!this._pendingCustomMood || !this._pendingCustomMood.emoji) {
      this._toast('请选择一个表情');
      return;
    }

    const level = parseInt(document.getElementById('custom-mood-level')?.value || 5);
    const newMood = {
      id: 'custom_' + Date.now(),
      emoji: this._pendingCustomMood.emoji,
      label: name,
      value: level,
      isSystem: false,
      createdAt: Date.now(),
    };

    const emptyIdx = this.fallbackMoods.findIndex(m => m === null);
    let evicted = null;
    if (emptyIdx !== -1) {
      this.fallbackMoods[emptyIdx] = newMood;
      this.customMoods.push(newMood.id);
    } else {
      // LRU：替换最早的自定义
      const oldestId = this.customMoods.shift();
      const oldestIdx = this.fallbackMoods.findIndex(m => m && m.id === oldestId);
      if (oldestIdx !== -1) {
        evicted = this.fallbackMoods[oldestIdx];
        this.fallbackMoods[oldestIdx] = newMood;
        this.customMoods.push(newMood.id);
      }
    }

    this.state.currentMood = newMood.id;
    this.state.currentMoodValue = level;
    this.state.isDirty = true;

    this._closeModal('custom-mood-modal');
    this._renderMoods();
    this._renderWeekly();
    this._toast(evicted ? `已替换「${evicted.label}」` : '自定义心情添加成功');
  }

  // ==================== 自定义心情弹窗（已弃用，保留空方法以防兼容调用） ====================

  // ==================== 标签 ====================

  _renderTags() {
    const list = document.getElementById('tag-list');
    if (!list) return;

    const presetHtml = this.state.tags.map(tag => {
      const active = this.state.selectedTags.includes(tag) ? 'active' : '';
      return `<span class="tag ${active}" data-tag="${this._escape(tag)}" data-preset="true">${this._escape(tag)}</span>`;
    }).join('');

    const customHtml = this.state.customTags.map(tag => {
      const active = this.state.selectedTags.includes(tag) ? 'active' : '';
      return `<span class="tag tag-custom ${active}" data-tag="${this._escape(tag)}" data-preset="false">${this._escape(tag)}<button class="tag-delete" data-tag="${this._escape(tag)}" title="删除">×</button></span>`;
    }).join('');

    list.innerHTML = presetHtml + customHtml;

    list.querySelectorAll('.tag').forEach(tag => {
      tag.addEventListener('click', (e) => {
        if (e.target.classList.contains('tag-delete')) return;
        const t = tag.dataset.tag;
        if (this.state.selectedTags.includes(t)) {
          this.state.selectedTags = this.state.selectedTags.filter(x => x !== t);
        } else {
          this.state.selectedTags.push(t);
        }
        this.state.isDirty = true;
        this._renderTags();
      });
    });

    list.querySelectorAll('.tag-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const t = btn.dataset.tag;
        this.state.customTags = this.state.customTags.filter(x => x !== t);
        this.state.selectedTags = this.state.selectedTags.filter(x => x !== t);
        this.state.isDirty = true;
        // 同步到后端（异步，不阻塞 UI）
        fetch(`/api/diary/tags/${encodeURIComponent(t)}`, { method: 'DELETE' }).catch(() => {});
        this._renderTags();
      });
    });
  }

  // ==================== 本周心情 ====================

  _renderWeekly() {
    const grid = document.getElementById('weekly-grid');
    if (!grid) return;
    const days = ['一', '二', '三', '四', '五', '六', '日'];
    const today = new Date();
    const todayDow = today.getDay();
    const todayIndex = todayDow === 0 ? 6 : todayDow - 1;

    const weekData = this._getWeekMoodData();

    grid.innerHTML = days.map((d, i) => {
      const isToday = i === todayIndex ? 'is-today' : '';
      const mood = weekData[i];
      const emoji = mood?.emoji || '-';
      const title = mood ? `${mood.emoji} ${mood.label || ''}` : '暂无记录';
      return `<div class="weekly-day ${isToday}" title="${this._escape(title)}">
        <span class="emoji">${emoji}</span>
        <span class="day-name">周${d}</span>
      </div>`;
    }).join('');

    document.getElementById('streak-count').textContent = this.state.streak;
  }

  _getWeekMoodData() {
    const result = new Array(7).fill(null);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayDow = today.getDay();
    const todayIndex = todayDow === 0 ? 6 : todayDow - 1;

    // 在 fallbackMoods（含自定义）里按 id / value 查找
    const findMood = (entry) => {
      if (entry.mood_id) {
        const m = this.fallbackMoods.find(x => x && x.id === entry.mood_id);
        if (m) return m;
      }
      if (entry.emotion_level != null) {
        const m = this.fallbackMoods.find(x => x && x.value === entry.emotion_level);
        if (m) return m;
      }
      return { emoji: entry.emotion_emoji || '😊', label: entry.emotion_label || '' };
    };

    // 1) 历史 entries 填到对应日期
    (this.state.entries || []).forEach(entry => {
      if (!entry.date) return;
      const entryDate = new Date(entry.date);
      entryDate.setHours(0, 0, 0, 0);
      const diffDays = Math.round((today - entryDate) / 86400000);
      if (diffDays < 0 || diffDays > 6) return;
      const idx = todayIndex - diffDays;
      if (idx < 0 || idx > 6) return;
      result[idx] = findMood(entry);
    });

    // 2) 今天选中的心情（如果还没保存到 entries）覆盖今天位置
    if (this.state.currentMood) {
      const todayMood = this.fallbackMoods.find(m => m && m.id === this.state.currentMood);
      if (todayMood) {
        result[todayIndex] = todayMood;
      }
    }

    return result;
  }

  // ==================== 字数统计 ====================

  _updateCharCount() {
    const content = document.getElementById('diary-content');
    const countEl = document.getElementById('char-count');
    const hintEl = document.getElementById('word-count-hint');
    if (!content || !countEl) return;

    const update = () => {
      const text = content.innerText || '';
      const len = text.length;
      countEl.textContent = len;
      if (hintEl) {
        if (len === 0) hintEl.textContent = '开始记录吧，每一个字都算数';
        else if (len < 50) hintEl.textContent = '继续写，灵感正在涌现';
        else if (len < 200) hintEl.textContent = '写得不错，保持这个节奏';
        else hintEl.textContent = '太棒了，今天的记录很充实';
      }
      this.state.isDirty = this.state.isDirty ||
        (len > 0 || (document.getElementById('diary-title')?.value || '').length > 0);
    };

    content.addEventListener('input', update);
    update();
  }

  // ==================== 事件绑定 ====================

  _bindEvents() {
    // 保存
    document.getElementById('btn-save')?.addEventListener('click', () => this._save());

    // 历史记录
    document.getElementById('btn-history')?.addEventListener('click', () => this._openHistory());
    document.getElementById('history-modal-close')?.addEventListener('click', () => {
      this._maybeCloseWithUnsaved('history-modal');
    });
    // 点击历史弹窗外部关闭
    document.getElementById('history-modal')?.addEventListener('click', (e) => {
      if (e.target.id === 'history-modal') {
        this._maybeCloseWithUnsaved('history-modal');
      }
    });

    // 筛选按钮
    document.querySelectorAll('#view-diary .filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#view-diary .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.state.activeFilter = btn.dataset.filter;
        this._renderHistory();
      });
    });

    // 删除
    document.getElementById('btn-cancel-delete')?.addEventListener('click', () => this._closeModal('delete-modal'));
    document.getElementById('delete-modal-close')?.addEventListener('click', () => this._closeModal('delete-modal'));
    document.getElementById('btn-confirm-delete')?.addEventListener('click', () => this._confirmDelete());

    // 未保存
    document.getElementById('btn-continue-edit')?.addEventListener('click', () => this._closeModal('unsaved-modal'));
    document.getElementById('unsaved-modal-close')?.addEventListener('click', () => this._closeModal('unsaved-modal'));
    document.getElementById('btn-discard-edit')?.addEventListener('click', () => {
      this._closeModal('unsaved-modal');
      this._resetForm();
      this._proceedNavigation();
    });

    // 自定义心情弹窗事件在 _bindCustomMoodEventsOnce 中单例绑定

    // 图片
    document.getElementById('btn-image')?.addEventListener('click', () => {
      document.getElementById('image-file-input')?.click();
    });
    document.getElementById('image-file-input')?.addEventListener('change', (e) => this._handleImageUpload(e));

    // Lightbox
    document.getElementById('lightbox-close')?.addEventListener('click', () => this._closeLightbox());
    document.getElementById('lightbox-overlay')?.addEventListener('click', (e) => {
      if (e.target.id === 'lightbox-overlay') this._closeLightbox();
    });

    // 标题输入
    document.getElementById('diary-title')?.addEventListener('input', () => {
      this.state.isDirty = true;
    });

    // 标签输入
    document.getElementById('tag-input')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const val = e.target.value.trim();
        if (!val) return;
        if (this.state.tags.includes(val) || this.state.customTags.includes(val)) {
          this._toast('标签已存在');
          return;
        }
        this.state.customTags.push(val);
        this.state.selectedTags.push(val);
        this.state.isDirty = true;
        // 同步到后端
        fetch('/api/diary/tags', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tag: val }),
        }).catch(() => {});
        this._renderTags();
        e.target.value = '';
      }
    });

    // 浏览器关闭/刷新提示
    window.addEventListener('beforeunload', (e) => {
      if (this.state.isDirty) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    });
  }

  // ==================== 数据加载 ====================

  async _loadAll() {
    // 心情格纯前端维护，不需要从后端加载槽位
    await Promise.all([
      this._loadTags(),
      this._loadToday(),
    ]);
    await this._loadHistory();
  }

  // _loadMoods 已弃用：心情格全部由 fallbackMoods + customMoods 前端维护

  async _loadTags() {
    try {
      const res = await fetch('/api/diary/tags').then(r => r.json());
      if (res.success && Array.isArray(res.tags)) {
        const presets = this.state.tags;
        // 后端返回的标签扣掉前端预设，剩下的就是自定义标签
        this.state.customTags = res.tags.filter(t => !presets.includes(t));
        this._renderTags();
      }
    } catch (e) {
      console.warn('[Diary] 加载标签失败:', e);
    }
  }

  async _loadToday() {
    try {
      const res = await fetch('/api/diary/today').then(r => r.json());
      if (res.entry) {
        this.state.todayEntry = res.entry;
        this._fillFormFromEntry(res.entry);
      }
      if (typeof res.streak === 'number') {
        this.state.streak = res.streak;
        this._renderWeekly();
      }
    } catch (e) {
      console.warn('[Diary] 加载今日日记失败:', e);
    }
  }

  async _loadHistory() {
    try {
      const res = await fetch('/api/diary?limit=100').then(r => r.json());
      if (res.success) {
        this.state.entries = res.entries || [];
        this.state.streak = res.streak ?? this.state.streak;
        this._renderWeekly();
        // 顺手渲染一次历史（如果弹窗已打开）
        if (document.getElementById('history-modal')?.classList.contains('active')) {
          this._renderHistory();
        }
      }
    } catch (e) {
      console.warn('[Diary] 加载历史失败:', e);
    }
  }

  _fillFormFromEntry(entry) {
    document.getElementById('diary-title').value = entry.title || '';
    document.getElementById('diary-content').innerHTML = entry.content || '';
    // 心情：优先 mood_id（前端 ID），否则按 emotion_level 找 fallbackMoods
    if (entry.mood_id) {
      this.state.currentMood = entry.mood_id;
    } else if (entry.emotion_level) {
      const matched = this.fallbackMoods.find(m => m && m.value === entry.emotion_level);
      this.state.currentMood = matched?.id || null;
    }
    this.state.currentMoodValue = entry.emotion_level || null;
    this.state.selectedTags = entry.tags || [];
    this.state.images = (entry.images || []).map(url => ({ url, uploaded: true }));
    this.state.isDirty = false;
    this._renderMoods();
    this._renderTags();
    this._renderImagePreviews();
    this._updateCharCount();
  }

  // ==================== 保存 ====================

  async _save() {
    const title = document.getElementById('diary-title')?.value?.trim() || '';
    // 提取纯文本（避免存一堆 HTML 噪音）
    const contentEl = document.getElementById('diary-content');
    const contentHtml = contentEl?.innerHTML || '';
    const contentText = (contentEl?.innerText || '').trim();

    if (!title && !contentText && this.state.images.length === 0) {
      this._toast('日记内容不能为空');
      return;
    }

    const btn = document.getElementById('btn-save');
    if (btn) {
      btn.disabled = true;
      btn.textContent = '保存中...';
    }

    try {
      const data = {
        title,
        content: contentHtml,
        // 前端心情完全本地化：只传 emotion_level 给后端
        emotion_level: this.state.currentMoodValue || 5,
        tags: this.state.selectedTags,
        images: this.state.images.filter(i => i.uploaded).map(i => i.url),
      };

      const res = await fetch('/api/diary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }).then(r => r.json());

      if (res.success) {
        this.state.isDirty = false;
        if (res.entry) {
          this.state.todayEntry = res.entry;
          this._fillFormFromEntry(res.entry);
        }
        if (typeof res.streak === 'number') {
          this.state.streak = res.streak;
        }
        this._toast('日记保存成功');
        this._loadHistory();
      } else {
        this._toast(res.error || '保存失败');
      }
    } catch (e) {
      console.error('[Diary] 保存失败:', e);
      this._toast('保存失败，请检查网络');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '保存日记';
      }
    }
  }

  // ==================== 历史记录弹窗 ====================

  async _openHistory() {
    const modal = document.getElementById('history-modal');
    if (!modal) return;
    modal.classList.add('active');
    await this._loadHistory();
    this._renderHistory();
  }

  _filterEntries(entries, filter) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (filter === 'week') {
      const monday = new Date(today);
      const dow = today.getDay() || 7;
      monday.setDate(today.getDate() - (dow - 1));
      return entries.filter(e => {
        if (!e.date) return false;
        const d = new Date(e.date);
        return d >= monday && d <= today;
      });
    }
    if (filter === 'month') {
      const y = today.getFullYear();
      const m = today.getMonth();
      return entries.filter(e => {
        if (!e.date) return false;
        const d = new Date(e.date);
        return d.getFullYear() === y && d.getMonth() === m;
      });
    }
    return entries;
  }

  _renderHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;
    const filtered = this._filterEntries(this.state.entries, this.state.activeFilter);

    if (filtered.length === 0) {
      list.innerHTML = '<div class="history-empty">暂无符合条件的记录</div>';
      return;
    }

    list.innerHTML = filtered.map(entry => {
      const title = entry.title || '(无标题)';
      const date = entry.date || '';
      const mood = entry.emotion_emoji ? `${entry.emotion_emoji} ${entry.emotion_label || ''}` : '未记录心情';
      const tagsHtml = (entry.tags || []).slice(0, 3).map(t =>
        `<span class="history-tag" style="font-size:11px;color:#999;">#${this._escape(t)}</span>`
      ).join(' ');
      const isToday = entry.date === new Date().toISOString().slice(0, 10);
      return `<div class="history-item" data-id="${entry.id}">
        <div class="history-item-title">${this._escape(title)} ${isToday ? '<span style="font-size:11px;color:#999;">· 今天</span>' : ''}</div>
        <div class="history-item-meta">
          <span class="history-mood">${mood}</span> · ${date} ${tagsHtml}
        </div>
        <div class="history-item-actions">
          <button class="history-item-btn" data-action="view" data-id="${entry.id}">查看</button>
          <button class="history-item-btn danger" data-action="delete" data-id="${entry.id}" data-title="${this._escape(title)}">删除</button>
        </div>
      </div>`;
    }).join('');

    list.querySelectorAll('[data-action="view"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this._viewHistoryEntry(btn.dataset.id);
      });
    });
    list.querySelectorAll('[data-action="delete"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this._askDelete(btn.dataset.id, btn.dataset.title);
      });
    });
  }

  async _viewHistoryEntry(id) {
    try {
      const res = await fetch(`/api/diary/${id}`).then(r => r.json());
      if (res.success && res.entry) {
        this._closeModal('history-modal');
        // 询问是否覆盖当前编辑
        if (this.state.isDirty) {
          this._openUnsavedModal(() => {
            this._fillFormFromEntry(res.entry);
            this.state.isDirty = false;
            this._toast('已加载历史日记');
          });
        } else {
          this._fillFormFromEntry(res.entry);
          this.state.isDirty = false;
          this._toast('已加载历史日记');
        }
      } else {
        this._toast('加载失败');
      }
    } catch (e) {
      console.error('[Diary] 加载历史详情失败:', e);
      this._toast('网络错误');
    }
  }

  _askDelete(id, title) {
    this.state.deleteTargetId = id;
    this.state.deleteTargetTitle = title || '';
    const titleEl = document.getElementById('delete-target-title');
    if (titleEl) {
      titleEl.textContent = title ? `《${title}》` : '';
      titleEl.style.display = title ? 'block' : 'none';
    }
    this._openModal('delete-modal');
  }

  async _confirmDelete() {
    const id = this.state.deleteTargetId;
    if (!id) return;
    try {
      const res = await fetch(`/api/diary/${id}`, { method: 'DELETE' }).then(r => r.json());
      if (res.success) {
        this._toast('已删除');
        this._closeModal('delete-modal');
        this.state.deleteTargetId = null;
        // 如果删的是当前正在编辑的日记，清空编辑器
        if (this.state.todayEntry?.id === id) {
          this._resetForm();
        }
        await this._loadHistory();
        this._renderHistory();
        // 刷新今日
        await this._loadToday();
      } else {
        this._toast(res.error || '删除失败');
      }
    } catch (e) {
      console.error('[Diary] 删除失败:', e);
      this._toast('网络错误');
    }
  }

  // ==================== 未保存拦截 ====================

  _openUnsavedModal(onDiscard) {
    this._pendingDiscard = onDiscard;
    this._openModal('unsaved-modal');
  }

  _proceedNavigation() {
    if (this._pendingDiscard) {
      const fn = this._pendingDiscard;
      this._pendingDiscard = null;
      fn();
    }
  }

  _maybeCloseWithUnsaved(modalId) {
    if (this.state.isDirty && (modalId === 'history-modal')) {
      // 关闭历史弹窗不需要拦截；如果是离开日记视图则另说
      this._closeModal(modalId);
      return;
    }
    this._closeModal(modalId);
  }

  // ==================== 图片上传 ====================

  async _handleImageUpload(e) {
    const files = e.target.files;
    if (!files) return;
    for (const file of Array.from(files)) {
      if (!file.type.startsWith('image/')) continue;
      // 添加占位
      const placeholder = { url: '', uploading: true, name: file.name };
      this.state.images.push(placeholder);
      this._renderImagePreviews();
      try {
        const form = new FormData();
        form.append('image', file);
        const res = await fetch('/api/diary/upload-image', {
          method: 'POST',
          body: form,
        }).then(r => r.json());
        if (res.success && res.image_url) {
          // 替换占位
          const idx = this.state.images.indexOf(placeholder);
          if (idx >= 0) {
            this.state.images[idx] = { url: res.image_url, uploaded: true };
          }
          this.state.isDirty = true;
        } else {
          // 移除占位
          this.state.images = this.state.images.filter(i => i !== placeholder);
          this._toast(res.error || '上传失败');
        }
      } catch (err) {
        this.state.images = this.state.images.filter(i => i !== placeholder);
        console.error('[Diary] 上传失败:', err);
        this._toast('网络错误');
      }
    }
    this._renderImagePreviews();
    // 清空 input，允许重复选同一文件
    e.target.value = '';
  }

  _renderImagePreviews() {
    const list = document.getElementById('image-preview-list');
    if (!list) return;
    list.innerHTML = this.state.images.map((img, i) => {
      const isUploading = img.uploading && !img.url;
      if (isUploading) {
        return `<div class="image-preview-item-wrap">
          <div class="image-preview-item" style="background:#f5f5f0;display:flex;align-items:center;justify-content:center;color:#999;font-size:12px;">上传中</div>
        </div>`;
      }
      return `<div class="image-preview-item-wrap">
        <img class="image-preview-item" src="${this._escape(img.url)}" data-index="${i}" alt="">
        <button class="image-remove-btn" data-index="${i}" title="移除">✕</button>
      </div>`;
    }).join('');

    list.querySelectorAll('.image-preview-item').forEach(img => {
      img.addEventListener('click', (e) => {
        if (e.currentTarget.dataset.index === undefined) return;
        document.getElementById('lightbox-img').src = img.src;
        document.getElementById('lightbox-overlay').classList.add('active');
      });
    });
    list.querySelectorAll('.image-remove-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(btn.dataset.index);
        this.state.images.splice(idx, 1);
        this.state.isDirty = true;
        this._renderImagePreviews();
      });
    });
  }

  // ==================== 弹窗工具 ====================

  _closeModal(id) {
    document.getElementById(id)?.classList.remove('active');
  }
  _openModal(id) {
    document.getElementById(id)?.classList.add('active');
  }
  _closeLightbox() {
    document.getElementById('lightbox-overlay')?.classList.remove('active');
  }

  _resetForm() {
    document.getElementById('diary-title').value = '';
    document.getElementById('diary-content').innerHTML = '';
    this.state.currentMood = null;
    this.state.currentMoodValue = null;
    this.state.selectedTags = [];
    this.state.images = [];
    this.state.isDirty = false;
    this._renderMoods();
    this._renderTags();
    this._renderImagePreviews();
    this._updateCharCount();
  }

  _toast(msg) {
    const toast = document.getElementById('diary-toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
  }

  _escape(str) {
    return String(str ?? '').replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }
}

window.DiaryView = {
  init: () => {
    if (!window.__diaryAppInstance) {
      window.__diaryAppInstance = new DiaryApp();
    }
    window.__diaryAppInstance.init();
  }
};
