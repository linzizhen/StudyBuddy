﻿class DiaryApp {
  constructor() {
    this.state = {
      isLoading: false,
      todayEntry: null,
      entries: [],
      streak: 0,
      tags: ['澶嶄範', '鍋氶', '鍚', '鑳岃'],   // 4 涓璁撅紙鍓嶇鍥哄畾锛屼笉鍚屾鍒板悗绔級
      customTags: [],                           // 鐢ㄦ埛鑷畾涔夋爣绛撅紙鍚屾鍒板悗绔級
      moodSlots: [],        // 鍚庣 8 涓Ы浣嶏紙5 棰勮 + 鏈€澶?3 鑷畾涔夛級
      currentMood: null,    // 褰撳墠閫変腑 mood_id
      currentMoodValue: null,
      selectedTags: [],
      images: [],           // [{url, uploading?}]
      isDirty: false,
      deleteTargetId: null,
      deleteTargetTitle: '',
      activeFilter: 'all',
      pendingNavigation: null,
    };

    // emoji 閫夋嫨鍣ㄥ€欓€夛紙瑕嗙洊甯歌蹇冩儏鍦烘櫙锛?    this.emojiOptions = [
      '馃槉','馃槃','馃榿','馃グ','馃槝','馃ぉ','馃槑','馃コ',
      '馃槍','馃檪','馃槈','馃構','馃槒','馃','馃槆','馃',
      '馃槓','馃槕','馃樁','馃え','馃槾','馃ケ','馃槳','馃槣',
      '馃槩','馃槶','馃様','馃槥','馃槦','馃槹','馃槰','馃槺',
      '馃槨','馃槧','馃が','馃槫','馃サ','馃ザ','馃く','馃樀',
      '馃','馃','馃ぇ','馃樂','馃あ','馃ぎ','馃','馃ズ',
      '馃槇','馃懟','馃拃','馃','馃挭','馃憤','馃憥','鉁岋笍',
      '馃専','猸?,'馃敟','馃挧','馃寛','鈽€锔?,'馃寵','鈿?,
    ];

    this.EMOJI_LABEL_HINT = {
      '馃槩':'闅捐繃','馃槶':'闅捐繃','馃様':'浣庤惤','馃槥':'浣庤惤','馃槦':'浣庤惤',
      '馃槹':'鐒﹁檻','馃槰':'瀹虫€?,'馃槺':'鎯婃亹',
      '馃槾':'鐤叉儷','馃ケ':'鐤叉儷','馃槳':'鐤叉儷',
      '馃槓':'涓€鑸?,'馃槕':'涓€鑸?,'馃樁':'涓€鑸?,
      '馃':'鎬濊€?,'馃槍':'骞抽潤','馃檪':'涓嶉敊','馃槈':'杞绘澗',
      '馃槉':'寮€蹇?,'馃槃':'寮€蹇?,'馃榿':'寮€蹇?,'馃グ':'骞哥','馃槝':'骞哥',
      '馃ぉ':'鍏村','馃コ':'鍏村','馃槑':'鑷俊',
      '馃':'闅惧彈','馃':'涓嶉€?,'馃ぇ':'涓嶉€?,'馃樂':'涓嶉€?,'馃あ':'涓嶉€?,
      '馃槨':'鎰ゆ€?,'馃槧':'鎰ゆ€?,'馃が':'鎰ゆ€?,'馃槫':'涓嶇敇',
      '馃サ':'鐕ョ儹','馃ザ':'瀵掑喎','馃く':'闇囨儕','馃樀':'杩疯尗',
      '馃':'璋冪毊','馃ズ':'濮斿眻','馃槇':'鍧忕瑧','馃懟':'鍙ゆ€?,
      '馃拃':'宕╂簝','馃':'鍐烽叿','馃挭':'鑷俊','馃憤':'璁ゅ彲','馃憥':'鍚﹀畾',
      '馃専':'闂€€','猸?:'鐝嶈吹','馃敟':'鐑','馃挧':'鍐烽潤',
      '馃寛':'澶氬僵','鈽€锔?:'闃冲厜','馃寵':'澶滄櫄','鈿?:'鐏垫劅',
    };

    // 蹇冩儏鏍硷細鍥哄畾 8 鏍硷紙6 绯荤粺棰勮 + 2 鑷畾涔夋Ы浣嶏級
    this.fallbackMoods = [
      { id: 'happy', emoji: '馃槉', label: '寮€蹇?, value: 5, isSystem: true },
      { id: 'calm', emoji: '馃槍', label: '骞抽潤', value: 4, isSystem: true },
      { id: 'tired', emoji: '馃槾', label: '鐤叉儷', value: 3, isSystem: true },
      { id: 'anxious', emoji: '馃槹', label: '鐒﹁檻', value: 2, isSystem: true },
      { id: 'sad', emoji: '馃槩', label: '闅捐繃', value: 1, isSystem: true },
      { id: 'excited', emoji: '馃ぉ', label: '鍏村', value: 6, isSystem: true },
      null,  // 鑷畾涔夋Ы浣?1
      null   // 鑷畾涔夋Ы浣?2
    ];
    // 璁板綍鑷畾涔夊績鎯呮坊鍔犻『搴忥紝鐢ㄤ簬 LRU 娣樻卑鏈€鏃?    this.customMoods = [];
  }

  init() {
    this._renderMoods();
    this._renderTags();
    this._renderWeekly();
    this._updateCharCount();
    this._bindEvents();
    this._loadAll();
  }

  // ==================== 蹇冩儏娓叉煋 ====================

  _renderMoods() {
    const grid = document.getElementById('mood-grid');
    const moodAdd = document.getElementById('mood-add');
    if (!grid) return;
    const moods = this.fallbackMoods;
    grid.innerHTML = moods.map((m, i) => {
      if (!m) {
        return `<div class="mood-item mood-placeholder" data-index="${i}" title="娣诲姞鑷畾涔夊績鎯?></div>`;
      }
      const active = this.state.currentMood === m.id ? 'active' : '';
      const customDot = !m.isSystem ? '<span class="mood-custom-dot" title="鑷畾涔?>鈼?/span>' : '';
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

    // 鏂囧瓧閾炬帴鐐瑰嚮 鈫?鎵撳紑寮圭獥锛堟瘡娆￠噸娓查渶閲嶆柊缁戝畾锛屽洜 innerHTML 涓嶄細娓呯┖ #mood-add锛屼絾瀹夊叏璧疯锛?    if (moodAdd && !moodAdd.dataset.bound) {
      moodAdd.addEventListener('click', () => this._addCustomMood());
      moodAdd.style.cursor = 'pointer';
      moodAdd.dataset.bound = '1';
    }
  }

  _addCustomMood() {
    // 涓嶇 8 鏍兼槸鍚︽弧锛屾棤鏉′欢鎵撳紑寮圭獥
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

    // 70% 琛ㄦ儏 + 30% 鍏朵粬
    const faceEmojis = [
      '馃槉','馃槀','馃グ','馃槑','馃','馃構','馃ぉ','馃コ','馃槆','馃',
      '馃ぁ','馃懟','馃懡','馃','馃槏','馃','馃槒','馃槍','馃槣','馃お',
      '馃槵','馃ズ','馃槶','馃槫','馃槧','馃が','馃樂','馃','馃','馃あ',
      '馃ぎ','馃ゴ','馃樀','馃く','馃','馃','馃槙','馃槦','馃檨','鈽癸笍',
      '馃槷','馃槸','馃槻','馃槼','馃ケ','馃槾','馃い','馃槳','馃槇','馃懣',
      '馃拃','鈽狅笍','馃槺','馃槰','馃槹','馃サ','馃ザ','馃槨',
    ];
    const otherEmojis = [
      '馃帀','馃挭','馃敟','猸?,'馃寛','馃挅','馃帄','鉁?,'馃挴','馃弳',
      '馃専','馃挮','馃巿','馃巵','馃拹','馃尭','鉂わ笍','馃А','馃挍','馃挌',
      '馃挋','馃挏','馃枻','馃','馃崕','馃崐','馃崑','馃崒','馃崏','馃崌',
      '馃崜','馃珢','馃尀','馃対','馃寷','馃寽','鈽勶笍','馃幆','馃帹','馃幀',
    ];

    // 80 涓?= 56 琛ㄦ儏 + 24 鍏朵粬锛?0/30 姣斾緥锛?    const emojis = [
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
    if (!name) { this._toast('璇疯緭鍏ュ績鎯呭悕绉?); return; }
    if (!this._pendingCustomMood || !this._pendingCustomMood.emoji) {
      this._toast('璇烽€夋嫨涓€涓〃鎯?);
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
      // LRU锛氭浛鎹㈡渶鏃╃殑鑷畾涔?      const oldestId = this.customMoods.shift();
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
    this._toast(evicted ? `宸叉浛鎹€?{evicted.label}銆峘 : '鑷畾涔夊績鎯呮坊鍔犳垚鍔?);
  }

  // ==================== 鑷畾涔夊績鎯呭脊绐楋紙宸插純鐢紝淇濈暀绌烘柟娉曚互闃插吋瀹硅皟鐢級 ====================

  // ==================== 鏍囩 ====================

  _renderTags() {
    const list = document.getElementById('tag-list');
    if (!list) return;

    const presetHtml = this.state.tags.map(tag => {
      const active = this.state.selectedTags.includes(tag) ? 'active' : '';
      return `<span class="tag ${active}" data-tag="${this._escape(tag)}" data-preset="true">${this._escape(tag)}</span>`;
    }).join('');

    const customHtml = this.state.customTags.map(tag => {
      const active = this.state.selectedTags.includes(tag) ? 'active' : '';
      return `<span class="tag tag-custom ${active}" data-tag="${this._escape(tag)}" data-preset="false">${this._escape(tag)}<button class="tag-delete" data-tag="${this._escape(tag)}" title="鍒犻櫎">脳</button></span>`;
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
        // 鍚屾鍒板悗绔紙寮傛锛屼笉闃诲 UI锛?        fetch(`/api/diary/tags/${encodeURIComponent(t)}`, { method: 'DELETE' }).catch(() => {});
        this._renderTags();
      });
    });
  }

  // ==================== 鏈懆蹇冩儏 ====================

  _renderWeekly() {
    const grid = document.getElementById('weekly-grid');
    if (!grid) return;
    const days = ['涓€', '浜?, '涓?, '鍥?, '浜?, '鍏?, '鏃?];
    const today = new Date();
    const todayDow = today.getDay();
    const todayIndex = todayDow === 0 ? 6 : todayDow - 1;

    const weekData = this._getWeekMoodData();

    grid.innerHTML = days.map((d, i) => {
      const isToday = i === todayIndex ? 'is-today' : '';
      const mood = weekData[i];
      const emoji = mood?.emoji || '-';
      const title = mood ? `${mood.emoji} ${mood.label || ''}` : '鏆傛棤璁板綍';
      return `<div class="weekly-day ${isToday}" title="${this._escape(title)}">
        <span class="emoji">${emoji}</span>
        <span class="day-name">鍛?{d}</span>
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

    // 鍦?fallbackMoods锛堝惈鑷畾涔夛級閲屾寜 id / value 鏌ユ壘
    const findMood = (entry) => {
      if (entry.mood_id) {
        const m = this.fallbackMoods.find(x => x && x.id === entry.mood_id);
        if (m) return m;
      }
      if (entry.emotion_level != null) {
        const m = this.fallbackMoods.find(x => x && x.value === entry.emotion_level);
        if (m) return m;
      }
      return { emoji: entry.emotion_emoji || '馃槉', label: entry.emotion_label || '' };
    };

    // 1) 鍘嗗彶 entries 濉埌瀵瑰簲鏃ユ湡
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

    // 2) 浠婂ぉ閫変腑鐨勫績鎯咃紙濡傛灉杩樻病淇濆瓨鍒?entries锛夎鐩栦粖澶╀綅缃?    if (this.state.currentMood) {
      const todayMood = this.fallbackMoods.find(m => m && m.id === this.state.currentMood);
      if (todayMood) {
        result[todayIndex] = todayMood;
      }
    }

    return result;
  }

  // ==================== 瀛楁暟缁熻 ====================

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
        if (len === 0) hintEl.textContent = '寮€濮嬭褰曞惂锛屾瘡涓€涓瓧閮界畻鏁?;
        else if (len < 50) hintEl.textContent = '缁х画鍐欙紝鐏垫劅姝ｅ湪娑岀幇';
        else if (len < 200) hintEl.textContent = '鍐欏緱涓嶉敊锛屼繚鎸佽繖涓妭濂?;
        else hintEl.textContent = '澶浜嗭紝浠婂ぉ鐨勮褰曞緢鍏呭疄';
      }
      this.state.isDirty = this.state.isDirty ||
        (len > 0 || (document.getElementById('diary-title')?.value || '').length > 0);
    };

    content.addEventListener('input', update);
    update();
  }

  // ==================== 浜嬩欢缁戝畾 ====================

  _bindEvents() {
    // 淇濆瓨
    document.getElementById('btn-save')?.addEventListener('click', () => this._save());

    // 鍘嗗彶璁板綍
    document.getElementById('btn-history')?.addEventListener('click', () => this._openHistory());
    document.getElementById('history-modal-close')?.addEventListener('click', () => {
      this._maybeCloseWithUnsaved('history-modal');
    });
    // 鐐瑰嚮鍘嗗彶寮圭獥澶栭儴鍏抽棴
    document.getElementById('history-modal')?.addEventListener('click', (e) => {
      if (e.target.id === 'history-modal') {
        this._maybeCloseWithUnsaved('history-modal');
      }
    });

    // 绛涢€夋寜閽?    document.querySelectorAll('#view-diary .filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#view-diary .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.state.activeFilter = btn.dataset.filter;
        this._renderHistory();
      });
    });

    // 鍒犻櫎
    document.getElementById('btn-cancel-delete')?.addEventListener('click', () => this._closeModal('delete-modal'));
    document.getElementById('delete-modal-close')?.addEventListener('click', () => this._closeModal('delete-modal'));
    document.getElementById('btn-confirm-delete')?.addEventListener('click', () => this._confirmDelete());

    // 鏈繚瀛?    document.getElementById('btn-continue-edit')?.addEventListener('click', () => this._closeModal('unsaved-modal'));
    document.getElementById('unsaved-modal-close')?.addEventListener('click', () => this._closeModal('unsaved-modal'));
    document.getElementById('btn-discard-edit')?.addEventListener('click', () => {
      this._closeModal('unsaved-modal');
      this._resetForm();
      this._proceedNavigation();
    });

    // 鑷畾涔夊績鎯呭脊绐椾簨浠跺湪 _bindCustomMoodEventsOnce 涓崟渚嬬粦瀹?
    // 鍥剧墖
    document.getElementById('btn-image')?.addEventListener('click', () => {
      document.getElementById('image-file-input')?.click();
    });
    document.getElementById('image-file-input')?.addEventListener('change', (e) => this._handleImageUpload(e));

    // Lightbox
    document.getElementById('lightbox-close')?.addEventListener('click', () => this._closeLightbox());
    document.getElementById('lightbox-overlay')?.addEventListener('click', (e) => {
      if (e.target.id === 'lightbox-overlay') this._closeLightbox();
    });

    // 鏍囬杈撳叆
    document.getElementById('diary-title')?.addEventListener('input', () => {
      this.state.isDirty = true;
    });

    // 鏍囩杈撳叆
    document.getElementById('tag-input')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const val = e.target.value.trim();
        if (!val) return;
        if (this.state.tags.includes(val) || this.state.customTags.includes(val)) {
          this._toast('鏍囩宸插瓨鍦?);
          return;
        }
        this.state.customTags.push(val);
        this.state.selectedTags.push(val);
        this.state.isDirty = true;
        // 鍚屾鍒板悗绔?        fetch('/api/diary/tags', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tag: val }),
        }).catch(() => {});
        this._renderTags();
        e.target.value = '';
      }
    });

    // 娴忚鍣ㄥ叧闂?鍒锋柊鎻愮ず
    window.addEventListener('beforeunload', (e) => {
      if (this.state.isDirty) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    });
  }

  // ==================== 鏁版嵁鍔犺浇 ====================

  async _loadAll() {
    // 蹇冩儏鏍肩函鍓嶇缁存姢锛屼笉闇€瑕佷粠鍚庣鍔犺浇妲戒綅
    await Promise.all([
      this._loadTags(),
      this._loadToday(),
    ]);
    await this._loadHistory();
  }

  // _loadMoods 宸插純鐢細蹇冩儏鏍煎叏閮ㄧ敱 fallbackMoods + customMoods 鍓嶇缁存姢

  async _loadTags() {
    try {
      const res = await fetch('/api/diary/tags').then(r => r.json());
      if (res.success && Array.isArray(res.tags)) {
        const presets = this.state.tags;
        // 鍚庣杩斿洖鐨勬爣绛炬墸鎺夊墠绔璁撅紝鍓╀笅鐨勫氨鏄嚜瀹氫箟鏍囩
        this.state.customTags = res.tags.filter(t => !presets.includes(t));
        this._renderTags();
      }
    } catch (e) {
      console.warn('[Diary] 鍔犺浇鏍囩澶辫触:', e);
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
      console.warn('[Diary] 鍔犺浇浠婃棩鏃ヨ澶辫触:', e);
    }
  }

  async _loadHistory() {
    try {
      const res = await fetch('/api/diary?limit=100').then(r => r.json());
      if (res.success) {
        this.state.entries = res.entries || [];
        this.state.streak = res.streak ?? this.state.streak;
        this._renderWeekly();
        // 椤烘墜娓叉煋涓€娆″巻鍙诧紙濡傛灉寮圭獥宸叉墦寮€锛?        if (document.getElementById('history-modal')?.classList.contains('active')) {
          this._renderHistory();
        }
      }
    } catch (e) {
      console.warn('[Diary] 鍔犺浇鍘嗗彶澶辫触:', e);
    }
  }

  _fillFormFromEntry(entry) {
    document.getElementById('diary-title').value = entry.title || '';
    document.getElementById('diary-content').innerHTML = entry.content || '';
    // 蹇冩儏锛氫紭鍏?mood_id锛堝墠绔?ID锛夛紝鍚﹀垯鎸?emotion_level 鎵?fallbackMoods
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

  // ==================== 淇濆瓨 ====================

  async _save() {
    const title = document.getElementById('diary-title')?.value?.trim() || '';
    // 鎻愬彇绾枃鏈紙閬垮厤瀛樹竴鍫?HTML 鍣煶锛?    const contentEl = document.getElementById('diary-content');
    const contentHtml = contentEl?.innerHTML || '';
    const contentText = (contentEl?.innerText || '').trim();

    if (!title && !contentText && this.state.images.length === 0) {
      this._toast('鏃ヨ鍐呭涓嶈兘涓虹┖');
      return;
    }

    const btn = document.getElementById('btn-save');
    if (btn) {
      btn.disabled = true;
      btn.textContent = '淇濆瓨涓?..';
    }

    try {
      const data = {
        title,
        content: contentHtml,
        // 鍓嶇蹇冩儏瀹屽叏鏈湴鍖栵細鍙紶 emotion_level 缁欏悗绔?        emotion_level: this.state.currentMoodValue || 5,
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
        this._toast('鏃ヨ淇濆瓨鎴愬姛');
        this._loadHistory();
      } else {
        this._toast(res.error || '淇濆瓨澶辫触');
      }
    } catch (e) {
      console.error('[Diary] 淇濆瓨澶辫触:', e);
      this._toast('淇濆瓨澶辫触锛岃妫€鏌ョ綉缁?);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '淇濆瓨鏃ヨ';
      }
    }
  }

  // ==================== 鍘嗗彶璁板綍寮圭獥 ====================

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
      list.innerHTML = '<div class="history-empty">鏆傛棤绗﹀悎鏉′欢鐨勮褰?/div>';
      return;
    }

    list.innerHTML = filtered.map(entry => {
      const title = entry.title || '(鏃犳爣棰?';
      const date = entry.date || '';
      const mood = entry.emotion_emoji ? `${entry.emotion_emoji} ${entry.emotion_label || ''}` : '鏈褰曞績鎯?;
      const tagsHtml = (entry.tags || []).slice(0, 3).map(t =>
        `<span class="history-tag" style="font-size:11px;color:#999;">#${this._escape(t)}</span>`
      ).join(' ');
      const isToday = entry.date === new Date().toISOString().slice(0, 10);
      return `<div class="history-item" data-id="${entry.id}">
        <div class="history-item-title">${this._escape(title)} ${isToday ? '<span style="font-size:11px;color:#999;">路 浠婂ぉ</span>' : ''}</div>
        <div class="history-item-meta">
          <span class="history-mood">${mood}</span> 路 ${date} ${tagsHtml}
        </div>
        <div class="history-item-actions">
          <button class="history-item-btn" data-action="view" data-id="${entry.id}">鏌ョ湅</button>
          <button class="history-item-btn danger" data-action="delete" data-id="${entry.id}" data-title="${this._escape(title)}">鍒犻櫎</button>
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
        // 璇㈤棶鏄惁瑕嗙洊褰撳墠缂栬緫
        if (this.state.isDirty) {
          this._openUnsavedModal(() => {
            this._fillFormFromEntry(res.entry);
            this.state.isDirty = false;
            this._toast('宸插姞杞藉巻鍙叉棩璁?);
          });
        } else {
          this._fillFormFromEntry(res.entry);
          this.state.isDirty = false;
          this._toast('宸插姞杞藉巻鍙叉棩璁?);
        }
      } else {
        this._toast('鍔犺浇澶辫触');
      }
    } catch (e) {
      console.error('[Diary] 鍔犺浇鍘嗗彶璇︽儏澶辫触:', e);
      this._toast('缃戠粶閿欒');
    }
  }

  _askDelete(id, title) {
    this.state.deleteTargetId = id;
    this.state.deleteTargetTitle = title || '';
    const titleEl = document.getElementById('delete-target-title');
    if (titleEl) {
      titleEl.textContent = title ? `銆?{title}銆媊 : '';
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
        this._toast('宸插垹闄?);
        this._closeModal('delete-modal');
        this.state.deleteTargetId = null;
        // 濡傛灉鍒犵殑鏄綋鍓嶆鍦ㄧ紪杈戠殑鏃ヨ锛屾竻绌虹紪杈戝櫒
        if (this.state.todayEntry?.id === id) {
          this._resetForm();
        }
        await this._loadHistory();
        this._renderHistory();
        // 鍒锋柊浠婃棩
        await this._loadToday();
      } else {
        this._toast(res.error || '鍒犻櫎澶辫触');
      }
    } catch (e) {
      console.error('[Diary] 鍒犻櫎澶辫触:', e);
      this._toast('缃戠粶閿欒');
    }
  }

  // ==================== 鏈繚瀛樻嫤鎴?====================

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
      // 鍏抽棴鍘嗗彶寮圭獥涓嶉渶瑕佹嫤鎴紱濡傛灉鏄寮€鏃ヨ瑙嗗浘鍒欏彟璇?      this._closeModal(modalId);
      return;
    }
    this._closeModal(modalId);
  }

  // ==================== 鍥剧墖涓婁紶 ====================

  async _handleImageUpload(e) {
    const files = e.target.files;
    if (!files) return;
    for (const file of Array.from(files)) {
      if (!file.type.startsWith('image/')) continue;
      // 娣诲姞鍗犱綅
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
          // 鏇挎崲鍗犱綅
          const idx = this.state.images.indexOf(placeholder);
          if (idx >= 0) {
            this.state.images[idx] = { url: res.image_url, uploaded: true };
          }
          this.state.isDirty = true;
        } else {
          // 绉婚櫎鍗犱綅
          this.state.images = this.state.images.filter(i => i !== placeholder);
          this._toast(res.error || '涓婁紶澶辫触');
        }
      } catch (err) {
        this.state.images = this.state.images.filter(i => i !== placeholder);
        console.error('[Diary] 涓婁紶澶辫触:', err);
        this._toast('缃戠粶閿欒');
      }
    }
    this._renderImagePreviews();
    // 娓呯┖ input锛屽厑璁搁噸澶嶉€夊悓涓€鏂囦欢
    e.target.value = '';
  }

  _renderImagePreviews() {
    const list = document.getElementById('image-preview-list');
    if (!list) return;
    list.innerHTML = this.state.images.map((img, i) => {
      const isUploading = img.uploading && !img.url;
      if (isUploading) {
        return `<div class="image-preview-item-wrap">
          <div class="image-preview-item" style="background:#f5f5f0;display:flex;align-items:center;justify-content:center;color:#999;font-size:12px;">涓婁紶涓?/div>
        </div>`;
      }
      return `<div class="image-preview-item-wrap">
        <img class="image-preview-item" src="${this._escape(img.url)}" data-index="${i}" alt="">
        <button class="image-remove-btn" data-index="${i}" title="绉婚櫎">鉁?/button>
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

  // ==================== 寮圭獥宸ュ叿 ====================

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
