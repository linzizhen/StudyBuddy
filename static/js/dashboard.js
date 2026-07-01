/**
 * StudyPal - Dashboard JavaScript
 */

// ============================================================
// 全局 Token 工具 + fetch 拦截（401 自动跳登录）
// ============================================================
function getToken() {
  try {
    return localStorage.getItem('token') || sessionStorage.getItem('token') || '';
  } catch (e) {
    return '';
  }
}

function getUsername() {
  try {
    return localStorage.getItem('username') || sessionStorage.getItem('username') || '';
  } catch (e) {
    return '';
  }
}

function clearAuth() {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('username');
  } catch (e) {}
}

(function patchFetch() {
  if (window.__SP_FETCH_PATCHED__) return;
  window.__SP_FETCH_PATCHED__ = true;
  var original = window.fetch ? window.fetch.bind(window) : null;
  if (!original) return;
  // 暴露原生 fetch，供需要"绕过 401 拦截"的特定场景（如保存配置）使用
  window.__SP_ORIGINAL_FETCH__ = original;

  // 仅在已登录（有 token 缓存）时才拦截 401 自动跳转
  // 避免未登录用户的 API 请求被无限循环跳登录页
  window.fetch = function() {
    var args = Array.prototype.slice.call(arguments);
    return original.apply(window, args).then(function(resp) {
      if (resp.status === 401 && getToken()) {
        clearAuth();
        if (typeof showToast === 'function') {
          showToast('登录已过期，请重新登录', 'warning');
        }
        setTimeout(function() {
          window.location.href = '/login';
        }, 1500);
      }
      return resp;
    });
  };
})();

document.addEventListener('DOMContentLoaded', function() {
  initNavigation();
  initSearch();
  initPomodoro();
  initTasks();
  initDiary();
  initChat();
  initSettings();
  updateGreeting();
  updateCountdown();
});

// ============================================================
// 导航切换
// ============================================================
var _lastSection = null;
function initNavigation() {
  var navItems = document.querySelectorAll('.nav-item');
  var sections = document.querySelectorAll('.page-section');

  function switchSection(sectionName) {
    // 离开学习搭子 → 保存当前对话
    if (_lastSection === 'buddy' && sectionName !== 'buddy') {
      if (typeof saveConversationToServer === 'function') saveConversationToServer();
    }

    navItems.forEach(function(n) { n.classList.remove('active'); });
    navItems.forEach(function(n) {
      if (n.dataset.section === sectionName) n.classList.add('active');
    });

    sections.forEach(function(s) {
      s.style.display = 'none';
      s.classList.add('hidden');
    });
    var target = document.getElementById('section-' + sectionName);
    if (target) {
      target.style.display = 'block';
      target.classList.remove('hidden');
    }

    // 进入学习搭子 → 恢复对话 + 拉历史
    if (sectionName === 'buddy') {
      if (typeof loadCurrentBuddyMessages === 'function') loadCurrentBuddyMessages();
      if (typeof loadConversationHistory === 'function') loadConversationHistory();
    }

    updateRightSidebar(sectionName);
    _lastSection = sectionName;
  }
  window.__switchSection = switchSection;

  navItems.forEach(function(item) {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      switchSection(item.dataset.section);
    });
  });

  document.querySelectorAll('.quick-card').forEach(function(card) {
    card.addEventListener('click', function(e) {
      e.preventDefault();
      var sec = card.dataset.section;
      if (sec) switchSection(sec);
    });
  });

  switchSection('dashboard');
}

function updateRightSidebar(section) {
  var rsDefault = document.getElementById('rs-default');
  var rsExam = document.getElementById('rs-exam-goal');
  if (rsDefault && rsExam) {
    rsDefault.classList.toggle('hidden', section === 'exam-goal');
    rsExam.classList.toggle('hidden', section !== 'exam-goal');
  }
}

// ============================================================
// 问候语 + 倒计时
// ============================================================
function updateGreeting() {
  var el = document.getElementById('greeting-text');
  if (!el) return;
  var h = new Date().getHours();
  var greeting = '学习战士';
  if (h < 6) greeting = '夜猫子';
  else if (h < 9) greeting = '早起的鸟';
  else if (h < 12) greeting = '上午好';
  else if (h < 14) greeting = '中午好';
  else if (h < 18) greeting = '下午好';
  else if (h < 21) greeting = '晚上好';
  else greeting = '夜猫子';
  el.textContent = greeting + '，学习战士';
}

function updateCountdown() {
  var examDate = new Date('2026-12-21');
  var today = new Date();
  var diff = Math.ceil((examDate - today) / (1000 * 60 * 60 * 24));
  var days = diff > 0 ? diff : 0;
  ['countdown-days', 'rs-countdown-days', 'exam-days'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.textContent = days;
  });
}

// ============================================================
// 搜索
// ============================================================
function initSearch() {
  var input = document.getElementById('search-input');
  if (!input) return;
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      var q = input.value.trim();
      if (q) {
        input.value = '';
        showToast('搜索功能开发中: ' + q);
      }
    }
  });
}

// ============================================================
// 番茄钟
// ============================================================
function initPomodoro() {
  var toggleBtn = document.getElementById('btn-pomo-toggle');
  var resetBtn = document.getElementById('btn-pomo-reset');
  var timeEl = document.getElementById('pomo-time');
  var statusEl = document.getElementById('pomo-status');
  var durationInput = document.getElementById('pomo-duration-input');
  var durationText = document.getElementById('pomo-duration-text');
  var ringFill = document.getElementById('pomo-ring-fill');

  if (!toggleBtn) return;

  var totalSeconds = 25 * 60;
  var remaining = totalSeconds;
  var timer = null;
  var running = false;
  var circumference = 2 * Math.PI * 90;

  function formatTime(s) {
    var m = Math.floor(s / 60).toString().padStart(2, '0');
    var sec = (s % 60).toString().padStart(2, '0');
    return m + ':' + sec;
  }

  function updateRing() {
    if (!ringFill) return;
    var offset = circumference * (1 - remaining / totalSeconds);
    ringFill.style.strokeDashoffset = offset;
  }

  function tick() {
    remaining--;
    if (timeEl) timeEl.textContent = formatTime(remaining);
    updateRing();
    if (remaining <= 0) {
      clearInterval(timer);
      running = false;
      if (statusEl) statusEl.textContent = '完成！';
      if (toggleBtn) toggleBtn.textContent = '开始';
      showToast('番茄完成！休息一下吧~');
    }
  }

  toggleBtn.addEventListener('click', function() {
    if (!running) {
      if (remaining <= 0) remaining = totalSeconds;
      running = true;
      if (statusEl) statusEl.textContent = '专注中...';
      if (toggleBtn) toggleBtn.textContent = '暂停';
      timer = setInterval(tick, 1000);
    } else {
      running = false;
      clearInterval(timer);
      if (statusEl) statusEl.textContent = '已暂停';
      if (toggleBtn) toggleBtn.textContent = '继续';
    }
  });

  if (resetBtn) {
    resetBtn.addEventListener('click', function() {
      running = false;
      clearInterval(timer);
      remaining = totalSeconds;
      if (timeEl) timeEl.textContent = formatTime(remaining);
      if (statusEl) statusEl.textContent = '准备开始';
      if (toggleBtn) toggleBtn.textContent = '开始';
      updateRing();
    });
  }

  if (durationInput) {
    durationInput.addEventListener('input', function() {
      totalSeconds = parseInt(durationInput.value, 10) * 60;
      remaining = totalSeconds;
      if (!running && timeEl) timeEl.textContent = formatTime(remaining);
      if (durationText) durationText.textContent = durationInput.value;
      updateRing();
    });
  }
}

// ============================================================
// 待办任务
// ============================================================
function initTasks() {
  var input = document.getElementById('new-task-input');
  var addBtn = document.getElementById('btn-add-task');
  var list = document.getElementById('task-list');
  var tabs = document.querySelectorAll('.filter-tab');

  if (!list) return;

  var tasks = [];
  var currentFilter = 'all';

  function renderTasks() {
    var filtered = tasks.filter(function(t) {
      if (currentFilter === 'pending') return !t.completed;
      if (currentFilter === 'completed') return t.completed;
      return true;
    });

    if (filtered.length === 0) {
      list.innerHTML = '<div class="empty-state">暂无任务</div>';
      return;
    }

    list.innerHTML = filtered.map(function(t) {
      var idx = tasks.indexOf(t);
      return '<div class="task-item' + (t.completed ? ' completed' : '') + '" data-index="' + idx + '">' +
        '<div class="task-checkbox' + (t.completed ? ' checked' : '') + '"></div>' +
        '<span class="task-text">' + escapeHtml(t.text) + '</span>' +
        '<button class="task-delete">&times;</button></div>';
    }).join('');

    list.querySelectorAll('.task-checkbox').forEach(function(cb) {
      cb.addEventListener('click', function() {
        var el = cb.closest('.task-item');
        var idx = parseInt(el.dataset.index, 10);
        if (!tasks[idx]) return;
        tasks[idx].completed = !tasks[idx].completed;
        renderTasks();
        updateCounts();
      });
    });

    list.querySelectorAll('.task-delete').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var el = btn.closest('.task-item');
        var idx = parseInt(el.dataset.index, 10);
        if (!tasks[idx]) return;
        tasks.splice(idx, 1);
        renderTasks();
        updateCounts();
      });
    });
  }

  function updateCounts() {
    var pending = tasks.filter(function(t) { return !t.completed; }).length;
    var completed = tasks.filter(function(t) { return t.completed; }).length;
    var pEl = document.getElementById('tasks-pending-count');
    var cEl = document.getElementById('tasks-completed-count');
    if (pEl) pEl.textContent = pending + ' 待完成';
    if (cEl) cEl.textContent = completed + ' 已完成';
  }

  function addTask(text) {
    var value = (text || '').trim();
    if (!value) return;
    tasks.push({ text: value, completed: false });
    renderTasks();
    updateCounts();
  }

  if (addBtn) addBtn.addEventListener('click', function() {
    addTask(input ? input.value : '');
  });
  if (input) {
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        addTask(input.value);
        input.value = '';
      }
    });
  }

  tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      tabs.forEach(function(t) { t.classList.remove('active'); });
      tab.classList.add('active');
      currentFilter = tab.dataset.filter || 'all';
      renderTasks();
    });
  });

  renderTasks();
}

// ============================================================
// 学习日记
// ============================================================
function initDiary() {
  var saveBtn = document.getElementById('btn-save-diary');
  var contentEl = document.getElementById('diary-content');
  var wordCountEl = document.getElementById('diary-word-count');
  var tagInput = document.getElementById('tag-input');
  var tagList = document.getElementById('tag-list');
  var moodBtns = document.querySelectorAll('.mood-btn');

  if (saveBtn) {
    saveBtn.addEventListener('click', function() {
      var title = document.getElementById('diary-title');
      var body = contentEl ? contentEl.textContent.trim() : '';
      if (!body) {
        showToast('日记内容不能为空');
        return;
      }
      showToast('日记已保存！');
      if (title) title.value = '';
      if (contentEl) contentEl.textContent = '';
      if (wordCountEl) wordCountEl.textContent = '0 字';
      if (tagList) tagList.innerHTML = '';
    });
  }

  if (contentEl) {
    contentEl.addEventListener('input', function() {
      var count = contentEl.textContent.length;
      if (wordCountEl) wordCountEl.textContent = count + ' 字';
    });
  }

  if (tagInput) {
    tagInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        var val = tagInput.value.trim();
        if (val) {
          addTag(val);
          tagInput.value = '';
        }
      }
    });
  }

  function addTag(text) {
    if (!tagList) return;
    var chip = document.createElement('span');
    chip.className = 'tag-chip';
    chip.innerHTML = escapeHtml(text) + ' <span class="tag-remove" onclick="this.parentElement.remove()">&times;</span>';
    tagList.appendChild(chip);
  }

  moodBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      moodBtns.forEach(function(b) { b.classList.remove('selected'); });
      btn.classList.add('selected');
    });
  });
}

// ============================================================
// 学习搭子
// ============================================================
const BUDDY_DATA = {
  xiaodou: { name: "小豆", type: "温柔陪伴型", emoji: "🌸", bg: "#FFD93D", personality: "warm" },
  aran:    { name: "阿燃", type: "热血激励型", emoji: "🔥", bg: "#FF6B6B", personality: "passionate" },
  xuejie:  { name: "学姐", type: "学霸导师型", emoji: "📚", bg: "#74C0FC", personality: "rational" },
  xiaoye:  { name: "小夜", type: "深夜倾听型", emoji: "🌙", bg: "#9775FA", personality: "listener" }
};

let currentBuddy = "xiaodou";

function initChat() {
  const input = document.getElementById("buddy-input");
  const sendBtn = document.getElementById("btn-send-message");
  const messages = document.getElementById("buddy-messages");
  const quickReplies = document.querySelectorAll(".quick-prompt-btn");
  const newChatBtn = document.getElementById("btn-new-chat");

  if (!messages) return;

  function renderWelcome(buddyId) {
    const buddy = BUDDY_DATA[buddyId];
    messages.innerHTML = `
      <div class="message message-buddy">
        <div class="message-avatar-emoji" style="background:${buddy.bg}">${buddy.emoji}</div>
        <div class="message-content">
          <div class="message-author">${buddy.name}</div>
          <div class="message-bubble">嗨！我是${buddy.name}，你的学习搭子~ 🌟 有什么想聊的吗？</div>
          <div class="message-time">现在</div>
        </div>
      </div>
    `;
  }

  function switchBuddy(buddyId) {
    currentBuddy = buddyId;
    const buddy = BUDDY_DATA[buddyId];
    const typeShort = { warm: '温柔', passionate: '热血', rational: '学霸', listener: '倾听', humor: '幽默', analyst: '导师' };
    const short = typeShort[buddy.personality] || buddy.type.replace('型', '');

    // 聊天区头部
    const hAvatar = document.getElementById('chat-buddy-avatar');
    const hName = document.getElementById('chat-buddy-name');
    const hStatus = document.getElementById('chat-buddy-status');
    if (hAvatar) { hAvatar.textContent = buddy.emoji; hAvatar.style.background = buddy.bg; }
    if (hName) hName.textContent = buddy.name;
    if (hStatus) hStatus.textContent = '在线 · ' + buddy.type;

    // 右侧搭子档案
    const pAvatar = document.getElementById('profile-avatar');
    const pName = document.getElementById('profile-name');
    const pType = document.getElementById('profile-type');
    if (pAvatar) { pAvatar.textContent = buddy.emoji; pAvatar.style.background = buddy.bg; }
    if (pName) pName.textContent = buddy.name;
    if (pType) pType.textContent = buddy.type;

    // 右侧搭子列表 active
    document.querySelectorAll('.roster-item').forEach(item => {
      item.classList.toggle('active', item.dataset.buddy === buddyId);
    });

    // 左侧对话列表 active
    document.querySelectorAll('.conversation-item').forEach(item => {
      item.classList.toggle('active', item.querySelector('.conversation-name').textContent === buddy.name);
    });

    renderWelcome(buddyId);
  }

  function addMessage(text, sender) {
    const buddy = BUDDY_DATA[currentBuddy];
    const now = new Date();
    const timeStr = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
    const div = document.createElement("div");
    div.className = "message " + (sender === "user" ? "message-user" : "message-buddy");

    if (sender === "buddy") {
      div.innerHTML = `
        <div class="message-avatar-emoji" style="background:${buddy.bg}">${buddy.emoji}</div>
        <div class="message-content">
          <div class="message-author">${buddy.name}</div>
          <div class="message-bubble">${formatChatText(text)}</div>
          <div class="message-time">${timeStr}</div>
        </div>
      `;
    } else {
      div.innerHTML = `
        <div class="message-content">
          <div class="message-bubble">${escapeHtml(text)}</div>
          <div class="message-time">${timeStr}</div>
        </div>
      `;
    }

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  // AI 加载气泡（3 个跳动圆点 + 搭子专属思考文字）
  function addLoadingBubble() {
    const buddy = BUDDY_DATA[currentBuddy];
    const loadingTexts = {
      warm: '小豆正在思考...',
      passionate: '阿燃正在燃烧斗志...',
      rational: '学姐正在推导中...',
      listener: '小夜正在静静思考...',
      xuejie: '学姐正在推导中...',
      xiaodou: '小豆正在思考...',
      aran: '阿燃正在燃烧斗志...',
      senior: '学姐正在推导中...',
      xiaoye: '小夜正在静静思考...'
    };
    const text = loadingTexts[currentBuddy] || '搭子正在思考...';
    const id = 'loading-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message message-buddy';
    div.innerHTML =
      '<div class="message-avatar-emoji" style="background:' + buddy.bg + '">' + buddy.emoji + '</div>' +
      '<div class="message-content">' +
        '<div class="message-author">' + buddy.name + '</div>' +
        '<div class="message-bubble" style="display:flex;align-items:center;gap:8px;">' +
          '<span class="loading-dots" style="display:inline-flex;gap:4px;">' +
            '<span style="width:8px;height:8px;background:#ddd;border-radius:50%;animation:loadingDot 1.4s infinite ease-in-out both;animation-delay:-0.32s;"></span>' +
            '<span style="width:8px;height:8px;background:#ddd;border-radius:50%;animation:loadingDot 1.4s infinite ease-in-out both;animation-delay:-0.16s;"></span>' +
            '<span style="width:8px;height:8px;background:#ddd;border-radius:50%;animation:loadingDot 1.4s infinite ease-in-out both;"></span>' +
          '</span>' +
          '<span style="font-size:13px;color:#8C8C8C;">' + text + '</span>' +
        '</div>' +
      '</div>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return id;
  }

  function removeLoadingBubble(id) {
    var el = document.getElementById(id);
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  // 轻量 markdown 转 HTML（仅处理换行和 **加粗**）
  function formatChatText(text) {
    if (!text) return '';
    var safe = escapeHtml(text);
    safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    safe = safe.replace(/\n/g, '<br>');
    return safe;
  }

  // 更新对话次数
  function bumpChatStat() {
    var el = document.getElementById('stat-chats');
    if (!el) return;
    var n = parseInt(el.textContent || '0', 10) || 0;
    el.textContent = n + 1;
  }

  function sendMessage() {
    const text = (input ? input.value : "").trim();
    if (!text) return;
    if (sendBtn && sendBtn.disabled) return;

    if (sendBtn) sendBtn.disabled = true;
    addMessage(text, "user");
    if (input) input.value = "";

    // 调用真实 AI（读取用户配置的智谱模型）
    const loadingId = addLoadingBubble();

    fetch('/api/buddy/quick-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        buddy_id: currentBuddy,
        message: text,
        explain_mode: getExplainMode()
      })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      removeLoadingBubble(loadingId);
      if (data && data.success) {
        addMessage(data.reply || '...', 'buddy');
        bumpChatStat();
      } else {
        var err = (data && data.error) || 'AI 回复失败';
        var tip = (data && data.tip) || '';
        addMessage('抱歉，暂时无法回复。' + err + (tip ? '\n💡 ' + tip : ''), 'buddy');
        if (typeof showToast === 'function') showToast(err);
      }
    })
    .catch(function(e) {
      removeLoadingBubble(loadingId);
      addMessage('网络异常，请检查 AI 配置或网络状态。', 'buddy');
      if (typeof showToast === 'function') showToast('发送失败：' + e.message);
    })
    .finally(function() {
      if (sendBtn) sendBtn.disabled = false;
    });
  }

  function getExplainMode() {
    var sel = document.querySelector('input[name="explain-mode"]:checked');
    if (!sel) return 'auto';
    // 把 UI 的 auto/game/speed 直接映射
    return sel.value || 'auto';
  }

  document.querySelectorAll(".roster-item").forEach(item => {
    item.addEventListener("click", () => {
      if (item.dataset.buddy) switchBuddy(item.dataset.buddy);
    });
  });

  if (sendBtn) sendBtn.addEventListener("click", sendMessage);
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // 快捷 chip 按钮
  document.querySelectorAll(".quick-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      // 知识点讲解 chip 是开关入口，不走聊天
      if (chip.id === "btn-open-explain-panel") {
        openBuddyExplain();
        return;
      }
      const text = (chip.dataset.prompt || "").trim();
      if (text && input) {
        input.value = text;
        sendMessage();
      }
    });
  });

  // 右侧栏快捷功能按钮（知识点讲解 / 学习计划 / 学习方法 / 学习报告）
  document.querySelectorAll(".quick-action-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      var prompt = (btn.dataset.prompt || "").trim();
      if (prompt && input) {
        input.value = prompt;
        sendMessage();
      }
    });
  });

  // 右侧栏「我的搭子」列表（新 .my-buddy-item 风格）切换
  document.querySelectorAll(".my-buddy-item").forEach(item => {
    item.addEventListener("click", () => {
      var bid = item.dataset.buddy;
      if (bid && typeof switchBuddy === 'function') {
        switchBuddy(bid);
        showToast('已切换到' + (BUDDY_DATA[bid] ? BUDDY_DATA[bid].name : bid));
      }
    });
  });

  // 知识点讲解功能
  initBuddyExplain();

  // 新建对话
  var newConvBtn = document.getElementById("btn-new-conversation");
  if (newConvBtn) {
    newConvBtn.addEventListener("click", () => renderWelcome(currentBuddy));
  }

  // 历史记录按钮
  var historyBtn = document.getElementById("btn-chat-history");
  if (historyBtn) {
    historyBtn.addEventListener("click", () => showToast("历史记录功能开发中..."));
  }

  // 设置页创建搭子按钮 → 打开弹窗
  var openDesignerBtn = document.getElementById("btn-open-buddy-designer-settings");
  if (openDesignerBtn) {
    openDesignerBtn.addEventListener("click", function() {
      var modal = document.getElementById("buddy-designer-modal");
      if (modal) modal.classList.remove("hidden");
    });
  }

  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => renderWelcome(currentBuddy));
  }

  document.querySelectorAll(".chat-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".chat-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      showToast(tab.dataset.tab === "history" ? "历史对话加载中..." : "当前对话");
    });
  });

  document.querySelectorAll(".buddy-list-item").forEach(item => {
    item.addEventListener("click", () => {
      const id = item.dataset.buddy;
      if (id) switchBuddy(id);
    });
  });

  // 把 send 按钮绑定到真实 AI 调用（覆盖默认 mock）
  if (sendBtn) sendBtn.onclick = sendChatMessage;
  if (input) {
    input.onkeydown = function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    };
  }

  // 「+ 新对话」按钮
  var newConvBtn = document.getElementById('btn-new-conversation');
  if (newConvBtn) newConvBtn.onclick = startNewConversation;

  // 进入页面时拉历史
  loadConversationHistory();

  switchBuddy(currentBuddy);
}

function notifyStudyTime(minutes) {
  if (!minutes) return;
  const buddy = BUDDY_DATA[currentBuddy];
  const texts = [
    `哇，${buddy.name}看到你学习了${minutes}分钟，真是勤奋呢！`,
    `你已经专注了${minutes}分钟，太棒了！`,
    `学习${minutes}分钟了，记得适当休息哦~`
  ];
  const text = texts[Math.floor(Math.random() * texts.length)];
  addMessage(text, "buddy");
}

// ============================================================
// 设置
// ============================================================
function initSettings() {
  var saveBtn = document.getElementById('btn-save-settings');
  if (saveBtn) {
    saveBtn.addEventListener('click', function() {
      showToast('设置已保存！');
    });
  }

  // 账户状态卡
  initAccountStatus();

  // 搭子设计器弹窗
  var openBtn = document.getElementById('btn-open-buddy-designer');
  if (openBtn) {
    openBtn.addEventListener('click', function() {
      document.getElementById('buddy-designer-modal').classList.remove('hidden');
      document.getElementById('modal-title').textContent = '创建新搭子';
      document.getElementById('bd-name').value = '';
      document.getElementById('bd-desc').value = '';
      document.getElementById('bd-greeting').value = '';
      document.querySelectorAll('.avatar-option').forEach(function(o) { o.classList.remove('selected'); });
      var first = document.querySelector('.avatar-option');
      if (first) first.classList.add('selected');
    });
  }
  var closeBtn = document.getElementById('btn-close-modal');
  if (closeBtn) closeBtn.addEventListener('click', closeBuddyModal);
  var cancelBtn = document.getElementById('btn-cancel-buddy');
  if (cancelBtn) cancelBtn.addEventListener('click', closeBuddyModal);

  // 头像选择
  document.querySelectorAll('.avatar-option').forEach(function(opt) {
    opt.addEventListener('click', function() {
      document.querySelectorAll('.avatar-option').forEach(function(o) { o.classList.remove('selected'); });
      opt.classList.add('selected');
    });
  });

  // 保存搭子
  var saveBuddyBtn = document.getElementById('btn-save-buddy');
  if (saveBuddyBtn) saveBuddyBtn.addEventListener('click', saveBuddyFromModal);

  // 加载 AI 预设模型
  loadAiPresets();

  // 测试连接
  var testBtn = document.getElementById('btn-test-ai');
  if (testBtn) testBtn.addEventListener('click', testAiConnection);

  // 保存 AI 配置
  var saveAiBtn = document.getElementById('btn-save-ai');
  if (saveAiBtn) saveAiBtn.addEventListener('click', saveAiConfig);
}

function closeBuddyModal() {
  var modal = document.getElementById('buddy-designer-modal');
  if (modal) modal.classList.add('hidden');
}

function saveBuddyFromModal() {
  var name = (document.getElementById('bd-name') || {}).value || '';
  var personality = (document.getElementById('bd-personality') || {}).value || 'warm';
  var desc = (document.getElementById('bd-desc') || {}).value || '';
  var greeting = (document.getElementById('bd-greeting') || {}).value || '';
  var selected = document.querySelector('.avatar-option.selected');
  var emoji = selected ? selected.dataset.emoji : '🌸';
  var bg = selected ? selected.dataset.bg : '#F5F5F5';

  if (!name.trim()) { showToast('请输入搭子名字'); return; }

  var typeNames = { warm: '温暖陪伴型', passionate: '热血激励型', rational: '理性分析型', listener: '深夜倾听型', humor: '幽默风趣型', analyst: '学霸导师型' };
  var buddyId = 'custom_' + Date.now();

  var list = document.getElementById('buddy-designer-list');
  if (!list) { showToast('列表不存在'); return; }

  var item = document.createElement('div');
  item.className = 'designer-buddy-item';
  item.dataset.buddy = buddyId;
  item.innerHTML =
    '<div class="designer-buddy-avatar" style="background:' + bg + '">' + emoji + '</div>' +
    '<div class="designer-buddy-info">' +
      '<div class="designer-buddy-name">' + escapeHtml(name) + '</div>' +
      '<div class="designer-buddy-type">' + (typeNames[personality] || personality) + '</div>' +
      '<div class="designer-buddy-desc">' + escapeHtml(desc || '暂无描述') + '</div>' +
    '</div>';

  list.appendChild(item);
  closeBuddyModal();
  showToast('搭子保存成功！');
}

async function loadAiPresets() {
  var sel = document.getElementById('ai-preset-select');
  if (!sel) return;
  try {
    var res = await fetch('/api/ai-model/presets');
    var data = await res.json();
    if (!data.success || !data.presets) return;

    // 按 provider 分组
    var groups = { zhipu: [], openai: [], ollama: [], other: [] };
    data.presets.forEach(function(p) {
      var pv = (p.provider || '').toLowerCase();
      if (pv === 'zhipu') groups.zhipu.push(p);
      else if (pv === 'ollama') groups.ollama.push(p);
      else if (pv === 'openai') groups.openai.push(p);
      else groups.other.push(p);
    });

    sel.innerHTML = '<option value="">-- 选择预设模型 --</option>';

    function appendGroup(label, items) {
      if (!items.length) return;
      var og = document.createElement('optgroup');
      og.label = label;
      items.forEach(function(p) {
        var opt = document.createElement('option');
        opt.value = p.key;
        opt.textContent = p.name;
        opt.dataset.api = p.base_url || '';
        opt.dataset.model = p.model || '';
        og.appendChild(opt);
      });
      sel.appendChild(og);
    }

    appendGroup('智谱AI (Zhipu/GLM) - 国内免费推荐', groups.zhipu);
    appendGroup('云端模型 (OpenAI 兼容)', groups.openai);
    appendGroup('本地模型 (Ollama)', groups.ollama);
    appendGroup('其他', groups.other);

    // 选中预设时自动填充 base-url 和 model-name
    sel.addEventListener('change', function() {
      var opt = sel.options[sel.selectedIndex];
      if (!opt || !opt.value) return;
      var urlEl = document.getElementById('ai-base-url');
      var modelEl = document.getElementById('ai-model-name');
      if (opt.dataset.api) urlEl.value = opt.dataset.api;
      if (opt.dataset.model) modelEl.value = opt.dataset.model;
    });

    // 加载当前用户的配置回填表单
    loadCurrentAiConfig();
  } catch(e) {}
}

async function loadCurrentAiConfig() {
  try {
    var res = await fetch('/api/ai-model/current');
    var data = await res.json();
    if (!data || !data.success) return;
    var sel = document.getElementById('ai-preset-select');
    var urlEl = document.getElementById('ai-base-url');
    var modelEl = document.getElementById('ai-model-name');
    var keyEl = document.getElementById('ai-api-key');
    if (!sel || !urlEl || !modelEl) return;

    if (data.mode === 'preset' && data.model_key) {
      sel.value = data.model_key;
      var opt = sel.options[sel.selectedIndex];
      if (opt && opt.dataset.api) urlEl.value = opt.dataset.api;
      if (opt && opt.dataset.model) modelEl.value = opt.dataset.model;
    } else if (data.mode === 'custom' && data.model) {
      sel.value = '';
      urlEl.value = data.model.base_url || '';
      modelEl.value = data.model.model || '';
      if (keyEl) keyEl.value = '';  // 密钥不回填，由用户重输
    }
  } catch(e) {}
}

async function testAiConnection() {
  var key = (document.getElementById('ai-api-key') || {}).value || '';
  var baseUrl = (document.getElementById('ai-base-url') || {}).value || '';
  var model = (document.getElementById('ai-model-name') || {}).value || '';
  // 前端做轻校验：若三个字段都空，多半是预设模式或没填，给出明确提示
  if (!baseUrl || !model) {
    showToast('请先选择预设或填写自定义模型地址/模型名');
    return;
  }
  if (!key) {
    // key 为空时仍发送请求，由后端根据已登录用户回退到保存的自定义 key
    console.log('[DEBUG] testAiConnection: api_key 为空，交给后端回退处理');
  }
  showToast('正在测试连接...');
  try {
    var res = await fetch('/api/ai-model/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key, base_url: baseUrl, model: model })
    });
    var data = await res.json();
    if (data.success) { showToast('连接成功！'); }
    else { showToast('连接失败：' + (data.error || ('HTTP ' + res.status))); }
  } catch(e) { showToast('测试失败：' + e.message); }
}

async function saveAiConfig() {
  var preset = (document.getElementById('ai-preset-select') || {}).value || '';
  var baseUrl = (document.getElementById('ai-base-url') || {}).value || '';
  var apiKey = (document.getElementById('ai-api-key') || {}).value || '';
  var modelName = (document.getElementById('ai-model-name') || {}).value || '';
  // 关键修复：保存接口必须带 Authorization 头（与 GET 不同），用原 fetch 绕开全局 401 拦截器
  var rawFetch = window.__SP_ORIGINAL_FETCH__ || window.fetch.bind(window);
  var authHeaders = { 'Content-Type': 'application/json' };
  var tk = getToken();
  if (tk) authHeaders['Authorization'] = 'Bearer ' + tk;
  showToast('正在保存...');
  try {
    if (preset) {
      var res = await rawFetch('/api/ai-model/preset', {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({ model_key: preset })
      });
      var data = await res.json();
      if (data.success) { showToast('预设模型已切换'); return; }
      showToast('保存失败：' + (data.error || ('HTTP ' + res.status)));
      return;
    }
    if (baseUrl && apiKey && modelName) {
      var res = await rawFetch('/api/ai-model/custom', {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({ base_url: baseUrl, api_key: apiKey, model: modelName })
      });
      var data = await res.json();
      if (data.success) { showToast('自定义模型已保存'); return; }
      showToast('保存失败：' + (data.error || ('HTTP ' + res.status)));
      return;
    }
    showToast('请选择预设或填写自定义模型');
  } catch(e) { showToast('保存失败：' + e.message); }
}

// ============================================================
// 工具函数
// ============================================================
function showToast(message) {
  var toast = document.getElementById('study-pal-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'study-pal-toast';
    toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1A1A1A;color:#fff;padding:10px 20px;border-radius:20px;font-size:13px;z-index:9999;opacity:1;transition:opacity 0.3s;pointer-events:none;';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.style.opacity = '1';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(function() { toast.style.opacity = '0'; }, 2500);
}

function escapeHtml(str) {
  var div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ============================================================
// 知识点讲解
// ============================================================

var EXPLAIN_LOADER_WORDS = {
  xiaodou: ['小豆正在浇灌知识花园...', '花瓣慢慢展开...', '为你种下一颗种子...', '风里飘来花香...'],
  aran:    ['阿燃正在点燃竞技场！', '燃烧吧小宇宙！', '准备战斗！', '能量正在汇聚...'],
  senior:  ['学姐调整显微镜...', '记录实验数据...', '正在分析实验结果...', '实验报告生成中...'],
  xiaoye:  ['小夜仰望星空...', '月光慢慢亮起...', '星星正在连线...', '夜风送来灵感...']
};

var EXPLAIN_ROLE_THEME = {
  xiaodou: { cls: 'buddy-theme-xiaodou', emoji: '🌸' },
  aran:    { cls: 'buddy-theme-aran',    emoji: '⚡' },
  senior:  { cls: 'buddy-theme-senior',  emoji: '📚' },
  xiaoye:  { cls: 'buddy-theme-xiaoye',  emoji: '🌙' }
};

var _explainLoaderTimer = null;

function initBuddyExplain() {
  var panel = document.getElementById('buddy-explain-section');
  if (!panel) return;

  var openBtn = document.getElementById('btn-open-explain-panel');
  var closeBtn = document.getElementById('btn-close-explain');
  var startBtn = document.getElementById('btn-start-explain');
  var topicInput = document.getElementById('explain-topic-input');

  function closePanel() {
    panel.classList.add('hidden');
    stopExplainLoader();
    var lr = document.getElementById('explain-loading');
    var rr = document.getElementById('explain-result');
    if (lr) lr.classList.add('hidden');
    if (rr) rr.classList.add('hidden');
  }

  if (openBtn) {
    openBtn.addEventListener('click', function() {
      // 展开讲解区前，先把当前搭子的主题 class 同步上去
      applyBuddyTheme(currentBuddy || 'xiaodou');
      panel.classList.remove('hidden');
      if (topicInput) topicInput.focus();
    });
  }
  if (closeBtn) closeBtn.addEventListener('click', closePanel);
  if (startBtn) startBtn.addEventListener('click', startExplain);
  if (topicInput) {
    topicInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        startExplain();
      }
    });
  }
}

function openBuddyExplain() {
  applyBuddyTheme(currentBuddy || 'xiaodou');
  var panel = document.getElementById('buddy-explain-section');
  if (panel) panel.classList.remove('hidden');
  var topicInput = document.getElementById('explain-topic-input');
  if (topicInput) topicInput.focus();
}

function applyBuddyTheme(buddyId) {
  var theme = EXPLAIN_ROLE_THEME[buddyId] || EXPLAIN_ROLE_THEME.xiaodou;
  var loaderIcon = document.getElementById('buddy-loader-icon');
  var loaderEmoji = document.getElementById('buddy-loader-emoji');
  var section = document.getElementById('buddy-explain-section');

  if (loaderIcon) {
    ['buddy-theme-xiaodou','buddy-theme-aran','buddy-theme-senior','buddy-theme-xiaoye'].forEach(function(c){
      loaderIcon.classList.remove(c);
    });
    loaderIcon.classList.add(theme.cls);
  }
  if (loaderEmoji) loaderEmoji.textContent = theme.emoji;
  if (section) {
    ['buddy-theme-xiaodou','buddy-theme-aran','buddy-theme-senior','buddy-theme-xiaoye'].forEach(function(c){
      section.classList.remove(c);
    });
    section.classList.add(theme.cls);
  }
}

function showExplainLoading(roleId) {
  var lr = document.getElementById('explain-loading');
  var rr = document.getElementById('explain-result');
  var loaderText = document.getElementById('buddy-loader-text');
  if (lr) lr.classList.remove('hidden');
  if (rr) rr.classList.add('hidden');
  applyBuddyTheme(roleId);

  var words = EXPLAIN_LOADER_WORDS[roleId] || EXPLAIN_LOADER_WORDS.xiaodou;
  var idx = 0;
  if (loaderText) loaderText.textContent = words[0];
  stopExplainLoader();
  _explainLoaderTimer = setInterval(function() {
    idx = (idx + 1) % words.length;
    if (loaderText) loaderText.textContent = words[idx];
  }, 1600);
}

function stopExplainLoader() {
  if (_explainLoaderTimer) {
    clearInterval(_explainLoaderTimer);
    _explainLoaderTimer = null;
  }
}

function showGameContent(roleId, data) {
  var lr = document.getElementById('explain-loading');
  var rr = document.getElementById('explain-result');
  if (lr) lr.classList.add('hidden');
  if (rr) rr.classList.remove('hidden');

  var gameEl = document.getElementById('explain-game-content');
  var explainEl = document.getElementById('explain-explain-content');
  var metaEl = document.getElementById('explain-meta');

  if (gameEl) {
    gameEl.innerHTML = (data.game && data.game.trim())
      ? formatExplainText(data.game)
      : '<div class="explain-empty">这一关搭子没生成游戏剧情，但知识点讲解已经在下方啦 ✨</div>';
  }
  if (explainEl) {
    explainEl.innerHTML = formatExplainText(data.explain || '搭子这一轮没有生成讲解内容，请换个知识点试试~');
  }
  if (metaEl) {
    var usedModel = data.used_model || '默认模型';
    var topic = data.topic || '';
    var name = data.buddy_name || '搭子';
    var emoji = data.buddy_emoji || '🌸';
    metaEl.innerHTML = '<span class="explain-badge">' + emoji + ' ' + escapeHtml(name) + '</span>' +
                       '<span class="explain-badge">📚 ' + escapeHtml(topic) + '</span>' +
                       '<span class="explain-badge">🤖 ' + escapeHtml(usedModel) + '</span>';
  }
}

function formatExplainText(text) {
  // 简单的 markdown 兼容：保留段落、空行、保留 emoji 不过滤
  if (!text) return '';
  var safe = escapeHtml(text);
  // 双换行分段
  return safe.split(/\n{2,}/).map(function(p){
    // 单换行用 <br>
    return '<p>' + p.replace(/\n/g, '<br>') + '</p>';
  }).join('');
}

async function startExplain() {
  var topicInput = document.getElementById('explain-topic-input');
  var startBtn = document.getElementById('btn-start-explain');
  if (!topicInput) return;

  var topic = (topicInput.value || '').trim();
  if (!topic) {
    showToast('请先输入要讲解的知识点');
    topicInput.focus();
    return;
  }

  var roleId = (typeof currentBuddy !== 'undefined' && currentBuddy) ? currentBuddy : 'xiaodou';

  if (startBtn) startBtn.disabled = true;
  showExplainLoading(roleId);

  try {
    var res = await fetch('/api/buddy/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ buddy_id: roleId, topic: topic })
    });
    var data = await res.json();
    if (data && data.success) {
      showGameContent(roleId, data);
    } else {
      var err = (data && (data.error || data.tip)) || '讲解失败，请稍后重试';
      showToast(err);
      // 回退关闭加载态让用户重试
      var lr = document.getElementById('explain-loading');
      if (lr) lr.classList.add('hidden');
    }
  } catch (e) {
    showToast('网络异常：' + e.message);
    var lr2 = document.getElementById('explain-loading');
    if (lr2) lr2.classList.add('hidden');
  } finally {
    if (startBtn) startBtn.disabled = false;
    stopExplainLoader();
  }
}

// ============================================================
// 账户状态卡（设置页面）
// ============================================================
function initAccountStatus() {
  var token = getToken();
  var username = getUsername();
  var usernameDiv = document.getElementById('account-username');
  var statusText = document.getElementById('account-status-text');
  var reloginBtn = document.getElementById('relogin-btn');
  var logoutBtn = document.getElementById('logout-btn');
  if (!usernameDiv) return;

  if (!token) {
    usernameDiv.textContent = '未登录';
    statusText.textContent = '当前为游客模式，AI 配置仅保存在本浏览器';
    if (reloginBtn) reloginBtn.style.display = 'inline-block';
    if (logoutBtn) logoutBtn.style.display = 'none';
  } else {
    usernameDiv.textContent = username || '已登录用户';
    statusText.textContent = 'Token 有效，可以使用 AI 配置持久化功能';
    if (reloginBtn) reloginBtn.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'inline-block';
  }

  if (reloginBtn) {
    reloginBtn.onclick = function() {
      window.location.href = '/login';
    };
  }
  if (logoutBtn) {
    logoutBtn.onclick = function() {
      clearAuth();
      showToast('已退出登录');
      setTimeout(function() {
        if (typeof initAccountStatus === 'function') initAccountStatus();
      }, 600);
    };
  }
}

// ============================================================
// 搭子对话（真实 AI + 内存保留）
// ============================================================

// 每个搭子的内存对话缓存 { buddy_id: [{sender,text,time}] }
var BUDDY_CONVERSATIONS = {
  xiaodou: [],
  aran: [],
  xuejie: [],
  xiaoye: []
};

// 搭子专属错误提示 / 思考语
var BUDDY_THINKING = {
  xiaodou: '小豆正在思考...',
  aran:    '阿燃正在燃烧斗志...',
  xuejie:  '学姐正在推导中...',
  xiaoye:  '小夜正在静静思考...'
};

function _nowTimeStr() {
  var d = new Date();
  var h = d.getHours().toString().padStart(2,'0');
  var m = d.getMinutes().toString().padStart(2,'0');
  return h + ':' + m;
}

function chatContainer() {
  return document.getElementById('buddy-messages');
}

function renderChatMessage(sender, text, time, animate) {
  var container = chatContainer();
  if (!container) return;
  var meta = (typeof BUDDY_DATA !== 'undefined' && BUDDY_DATA[currentBuddy]) || {};
  var div = document.createElement('div');
  div.className = 'chat-message ' + sender + (animate ? ' message-new' : '');
  var avatar = sender === 'buddy' ? (meta.avatar || '🌸') : '👤';
  div.innerHTML =
    '<div class="message-avatar">' + avatar + '</div>' +
    '<div>' +
      '<div class="message-bubble">' + simpleMarkdownToHtml(text) + '</div>' +
      '<div class="message-time">' + (time || _nowTimeStr()) + '</div>' +
    '</div>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function simpleMarkdownToHtml(text) {
  if (!text) return '';
  var safe = escapeHtml(text);
  // 加粗、换行
  safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  safe = safe.replace(/\n/g, '<br>');
  return safe;
}

function saveMessageToMemory(sender, text) {
  if (!BUDDY_CONVERSATIONS[currentBuddy]) BUDDY_CONVERSATIONS[currentBuddy] = [];
  BUDDY_CONVERSATIONS[currentBuddy].push({
    sender: sender,
    text: text,
    time: _nowTimeStr()
  });
}

function addChatMessage(sender, text) {
  var time = _nowTimeStr();
  renderChatMessage(sender, text, time, true);
  saveMessageToMemory(sender, text);
}

function loadCurrentBuddyMessages() {
  var container = chatContainer();
  if (!container) return;
  container.innerHTML = '';
  var msgs = BUDDY_CONVERSATIONS[currentBuddy] || [];
  if (msgs.length === 0) {
    renderWelcomeToChat(currentBuddy);
    return;
  }
  msgs.forEach(function(m) {
    renderChatMessage(m.sender, m.text, m.time, false);
  });
}

function renderWelcomeToChat(buddyId) {
  var welcomes = {
    xiaodou: '嗨！我是小豆，你的学习搭子~ 🌟 有什么想聊的吗？',
    aran:    '哟！我是阿燃！🔥 准备燃烧你的学习热情了吗！',
    xuejie:  '你好，我是学姐 📚 有什么学习上的问题尽管问。',
    xiaoye:  '晚上好...我是小夜 🌙 慢慢说，我听着呢。'
  };
  addChatMessage('buddy', welcomes[buddyId] || '你好！');
}

function addLoadingBubbleToChat() {
  var container = chatContainer();
  if (!container) return null;
  var meta = (typeof BUDDY_DATA !== 'undefined' && BUDDY_DATA[currentBuddy]) || {};
  var text = BUDDY_THINKING[currentBuddy] || '搭子正在思考...';
  var id = 'loading-' + Date.now();
  var div = document.createElement('div');
  div.id = id;
  div.className = 'chat-message loading';
  div.innerHTML =
    '<div class="message-avatar">' + (meta.avatar || '🌸') + '</div>' +
    '<div>' +
      '<div class="message-bubble" style="display:flex;align-items:center;gap:8px;">' +
        '<span style="display:inline-flex;gap:4px;">' +
          '<span style="width:8px;height:8px;background:#ddd;border-radius:50%;animation:loadingDot 1.4s infinite ease-in-out both;animation-delay:-0.32s;"></span>' +
          '<span style="width:8px;height:8px;background:#ddd;border-radius:50%;animation:loadingDot 1.4s infinite ease-in-out both;animation-delay:-0.16s;"></span>' +
          '<span style="width:8px;height:8px;background:#ddd;border-radius:50%;animation:loadingDot 1.4s infinite ease-in-out both;"></span>' +
        '</span>' +
        '<span style="font-size:13px;color:#8C8C8C;">' + text + '</span>' +
      '</div>' +
    '</div>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeLoadingBubbleFromChat(id) {
  if (!id) return;
  var el = document.getElementById(id);
  if (el && el.parentNode) el.parentNode.removeChild(el);
}

function getExplainMode() {
  var sel = document.querySelector('input[name="explain-mode"]:checked');
  return sel ? (sel.value || 'auto') : 'auto';
}

async function sendChatMessage() {
  var input = document.getElementById('buddy-input');
  var sendBtn = document.getElementById('btn-send-message');
  var text = (input ? input.value : '').trim();
  if (!text) return;
  if (sendBtn && sendBtn.disabled) return;
  if (input) input.value = '';
  if (sendBtn) sendBtn.disabled = true;

  addChatMessage('user', text);
  var loadingId = addLoadingBubbleToChat();

  try {
    var res = await fetch('/api/buddy/quick-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        buddy_id: currentBuddy,
        message: text,
        explain_mode: getExplainMode()
      })
    });
    var data = await res.json();
    removeLoadingBubbleFromChat(loadingId);
    if (data && data.success) {
      addChatMessage('buddy', data.reply || '...');
      bumpChatStat();
    } else {
      var err = (data && data.error) || 'AI 回复失败';
      var showCfg = /AI_AUTH|API_KEY|未配置|权限|密钥/.test(err);
      var html = escapeHtml(err);
      if (showCfg) {
        html += '<br><br><button class="chat-config-btn" onclick="goToSettings()">⚙️ 前往设置配置 AI</button>';
      }
      addChatMessageHtml('buddy', html);
      showToast(err);
    }
  } catch (e) {
    removeLoadingBubbleFromChat(loadingId);
    var raw = (e && e.message) || '网络异常';
    var msg = raw;
    var showConfigBtn = false;
    // 403 细化提示
    if (raw.indexOf('AI_AUTH_403') >= 0) {
      msg = 'AI 权限验证失败，可能原因：1) API 密钥错误 2) 模型未开通权限 3) 账户额度已用完。\n详情：' + raw.replace(/^AI_AUTH_403:\s*/, '');
      showConfigBtn = true;
    } else if (raw.indexOf('API_KEY_INVALID') >= 0 || /403|Forbidden|401/.test(raw)) {
      msg = 'AI 密钥无效或权限不足：请检查设置中的 API 密钥是否正确。\n详情：' + raw.replace(/^API_KEY_INVALID:\s*/, '');
      showConfigBtn = true;
    } else if (raw.indexOf('AI_RATE_LIMIT') >= 0) {
      msg = 'AI 调用过于频繁，请稍后再试。';
    } else if (raw.indexOf('AI_NOT_FOUND') >= 0) {
      msg = 'API 地址或模型不存在，请检查设置。\n详情：' + raw;
      showConfigBtn = true;
    } else if (raw.indexOf('AI_SERVER_ERROR') >= 0) {
      msg = 'AI 服务器异常，请稍后重试。\n详情：' + raw;
    } else if (raw.indexOf('API_KEY_MISSING') >= 0 || /未配置|not configured|api_key/i.test(raw)) {
      msg = 'AI 模型未配置，请先前往设置页面配置。';
      showConfigBtn = true;
    } else {
      msg = '网络异常：' + raw;
    }

    // 构建错误消息 HTML（带前往设置按钮）
    var html = escapeHtml(msg).replace(/\n/g, '<br>');
    if (showConfigBtn) {
      html += '<br><br><button class="chat-config-btn" onclick="goToSettings()">⚙️ 前往设置配置 AI</button>';
    }
    addChatMessageHtml('buddy', html);
    showToast('发送失败：' + msg.split('\n')[0]);
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

// 跳到设置页
function goToSettings() {
  if (typeof window.__switchSection === 'function') {
    window.__switchSection('settings');
    showToast('请在「AI 配置」区域填写 API 密钥', 'info');
  } else {
    var nav = document.querySelector('[data-section="settings"]');
    if (nav) nav.click();
  }
}

// 渲染带 HTML 的消息气泡
function addChatMessageHtml(sender, html) {
  var container = document.getElementById('buddy-messages');
  if (!container) return;
  var meta = (typeof BUDDY_DATA !== 'undefined' && BUDDY_DATA[currentBuddy]) || {};
  var div = document.createElement('div');
  div.className = 'chat-message ' + sender + ' message-new';
  var avatar = sender === 'buddy' ? (meta.avatar || '🌸') : '👤';
  div.innerHTML =
    '<div class="message-avatar">' + avatar + '</div>' +
    '<div>' +
      '<div class="message-bubble">' + html + '</div>' +
      '<div class="message-time">' + _nowTimeStr() + '</div>' +
    '</div>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  // 不写入内存（避免保存带 HTML 标签的脏数据到历史）
}

function bumpChatStat() {
  var el = document.getElementById('stat-chats');
  if (!el) return;
  var n = parseInt(el.textContent || '0', 10) || 0;
  el.textContent = n + 1;
}

// ============================================================
// 历史记录
// ============================================================
function formatTimeAgo(isoString) {
  if (!isoString) return '';
  var d = new Date(isoString);
  if (isNaN(d.getTime())) return '';
  var diff = Date.now() - d.getTime();
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
  return (d.getMonth() + 1) + '月' + d.getDate() + '日';
}

async function loadConversationHistory() {
  var listEl = document.getElementById('buddy-history-list');
  if (!listEl) return;
  if (!getToken()) {
    listEl.innerHTML = '<div class="history-empty">登录后可查看历史对话</div>';
    return;
  }
  try {
    var res = await fetch('/api/buddy/conversations', {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    var data = await res.json();
    if (!data.success || !data.conversations || data.conversations.length === 0) {
      listEl.innerHTML = '<div class="history-empty">暂无历史对话</div>';
      return;
    }
    listEl.innerHTML = '';
    data.conversations.forEach(function(conv) {
      var item = document.createElement('div');
      item.className = 'history-item';
      item.dataset.convId = conv.id;
      item.innerHTML =
        '<div class="history-avatar">' + (conv.buddy_avatar || '🤖') + '</div>' +
        '<div class="history-info">' +
          '<div class="history-name">' + escapeHtml(conv.buddy_name || '对话') + '</div>' +
          '<div class="history-preview">' + escapeHtml(conv.preview || '新对话') + '</div>' +
          '<div class="history-meta">' + (conv.message_count || 0) + '条 · ' + formatTimeAgo(conv.updated_at) + '</div>' +
        '</div>' +
        '<button class="history-delete" data-conv-id="' + conv.id + '" title="删除">×</button>';

      item.addEventListener('click', function(e) {
        if (e.target.classList.contains('history-delete')) return;
        loadConversationDetail(conv.id);
      });

      var delBtn = item.querySelector('.history-delete');
      if (delBtn) {
        delBtn.addEventListener('click', function(e) {
          e.stopPropagation();
          if (confirm('确定删除这条历史对话吗？')) {
            deleteConversation(conv.id);
          }
        });
      }
      listEl.appendChild(item);
    });
  } catch (e) {
    listEl.innerHTML = '<div class="history-empty">加载失败</div>';
  }
}

async function loadConversationDetail(convId) {
  try {
    var res = await fetch('/api/buddy/conversation/' + convId, {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    var data = await res.json();
    if (!data.success) { showToast('加载失败'); return; }
    var conv = data.conversation;
    // 切换搭子
    if (typeof switchBuddy === 'function' && conv.buddy_id) {
      switchBuddy(conv.buddy_id);
    }
    // 恢复消息到内存（这里 messages 是 [{role,content,time?}] 格式）
    BUDDY_CONVERSATIONS[currentBuddy] = (conv.messages || []).map(function(m) {
      return {
        sender: m.role === 'user' ? 'user' : 'buddy',
        text: m.content || '',
        time: m.time || ''
      };
    });
    loadCurrentBuddyMessages();
    showToast('已加载历史对话');
  } catch (e) {
    showToast('加载失败：' + e.message);
  }
}

async function saveConversationToServer() {
  if (!getToken()) return;
  var messages = BUDDY_CONVERSATIONS[currentBuddy] || [];
  if (messages.length < 2) return; // 太少不保存
  try {
    await fetch('/api/buddy/conversation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getToken()
      },
      body: JSON.stringify({
        buddy_id: currentBuddy,
        messages: messages
      })
    });
  } catch (e) {
    // 静默失败，不打断用户
  }
}

async function deleteConversation(convId) {
  try {
    var res = await fetch('/api/buddy/conversation/' + convId, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    var data = await res.json();
    if (data.success) {
      showToast('已删除');
      loadConversationHistory();
    } else {
      showToast('删除失败');
    }
  } catch (e) {
    showToast('删除失败：' + e.message);
  }
}

function startNewConversation() {
  // 先保存当前对话
  saveConversationToServer();
  // 清空当前内存
  BUDDY_CONVERSATIONS[currentBuddy] = [];
  // 重新渲染欢迎语
  var container = chatContainer();
  if (container) container.innerHTML = '';
  renderWelcomeToChat(currentBuddy);
  showToast('已开启新对话');
}
