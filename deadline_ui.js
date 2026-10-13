/**
 * deadline_ui.js - 截止时间界面模块
 * 为每个事件卡片添加截止时间设置/显示界面
 */
const DeadlineUI = (function () {
  let modalEl = null;
  let overlayEl = null;
  let currentEventId = null;

  // 初始化模态框
  function init() {
    if (modalEl) return;
    overlayEl = document.createElement('div');
    overlayEl.className = 'deadline-overlay';
    overlayEl.style.cssText = `
      position:fixed; top:0; left:0; right:0; bottom:0;
      background:rgba(0,0,0,0.5); z-index:2000;
      display:none; align-items:center; justify-content:center;
      backdrop-filter:blur(4px);
    `;
    modalEl = document.createElement('div');
    modalEl.className = 'deadline-modal';
    modalEl.style.cssText = `
      background:white; border-radius:18px; padding:28px;
      width:420px; max-width:90vw; box-shadow:0 20px 60px rgba(0,0,0,0.3);
      animation:fadeInUp 0.3s ease;
    `;
    modalEl.innerHTML = `
      <div style="text-align:center; margin-bottom:20px;">
        <div style="font-size:2.5rem; margin-bottom:8px;">⏰</div>
        <h3 style="font-size:1.2rem; color:#1f2937; margin-bottom:4px;">设置截止时间</h3>
        <p id="deadlineEventTitle" style="font-size:0.85rem; color:#6b7280;">事件名称</p>
      </div>
      <div style="margin-bottom:16px;">
        <label style="display:block; font-size:0.8rem; color:#6b7280; margin-bottom:6px; font-weight:500;">截止日期</label>
        <input type="date" id="deadlineDateInput" style="
          width:100%; padding:10px 14px; border:2px solid #e5e7eb; border-radius:10px;
          font-size:0.95rem; outline:none; transition:border-color 0.2s;
        " />
      </div>
      <div style="margin-bottom:16px;">
        <label style="display:block; font-size:0.8rem; color:#6b7280; margin-bottom:6px; font-weight:500;">截止时间</label>
        <input type="time" id="deadlineTimeInput" style="
          width:100%; padding:10px 14px; border:2px solid #e5e7eb; border-radius:10px;
          font-size:0.95rem; outline:none; transition:border-color 0.2s;
        " />
      </div>
      <div style="margin-bottom:20px;">
        <label style="display:block; font-size:0.8rem; color:#6b7280; margin-bottom:6px; font-weight:500;">备注（可选）</label>
        <input type="text" id="deadlineNoteInput" placeholder="例如：需提前提交报告" style="
          width:100%; padding:10px 14px; border:2px solid #e5e7eb; border-radius:10px;
          font-size:0.85rem; outline:none; transition:border-color 0.2s;
        " />
      </div>
      <div style="display:flex; gap:10px;">
        <button id="deadlineCancelBtn" style="
          flex:1; padding:10px; border:2px solid #e5e7eb; border-radius:10px;
          background:white; color:#6b7280; font-size:0.9rem; cursor:pointer; transition:all 0.2s;
        ">取消</button>
        <button id="deadlineClearBtn" style="
          flex:1; padding:10px; border:2px solid #fca5a5; border-radius:10px;
          background:#fef2f2; color:#dc2626; font-size:0.9rem; cursor:pointer; transition:all 0.2s;
        ">清除截止</button>
        <button id="deadlineSaveBtn" style="
          flex:2; padding:10px; border:none; border-radius:10px;
          background:linear-gradient(135deg, #667eea, #764ba2); color:white;
          font-size:0.9rem; font-weight:600; cursor:pointer; transition:all 0.2s;
          box-shadow:0 4px 12px rgba(102,126,234,0.4);
        ">💾 保存截止时间</button>
      </div>
    `;
    overlayEl.appendChild(modalEl);
    document.body.appendChild(overlayEl);

    document.getElementById('deadlineCancelBtn').addEventListener('click', closeModal);
    document.getElementById('deadlineClearBtn').addEventListener('click', clearDeadline);
    document.getElementById('deadlineSaveBtn').addEventListener('click', saveDeadline);
    overlayEl.addEventListener('click', function (e) {
      if (e.target === overlayEl) closeModal();
    });
  }

  // 打开模态框
  function openModal(eventId, eventTitle) {
    init();
    currentEventId = eventId;
    document.getElementById('deadlineEventTitle').textContent = eventTitle;

    const existing = DeadlineSave.getDeadline(eventId);
    if (existing) {
      const d = new Date(existing.deadline);
      document.getElementById('deadlineDateInput').value = d.toISOString().split('T')[0];
      document.getElementById('deadlineTimeInput').value = pad(d.getHours()) + ':' + pad(d.getMinutes());
      document.getElementById('deadlineNoteInput').value = existing.note || '';
    } else {
      const now = new Date();
      now.setDate(now.getDate() + 1);
      document.getElementById('deadlineDateInput').value = now.toISOString().split('T')[0];
      document.getElementById('deadlineTimeInput').value = '18:00';
      document.getElementById('deadlineNoteInput').value = '';
    }

    overlayEl.style.display = 'flex';
  }

  function closeModal() {
    if (overlayEl) overlayEl.style.display = 'none';
    currentEventId = null;
  }

  function clearDeadline() {
    if (currentEventId !== null) {
      DeadlineSave.removeDeadline(currentEventId);
      ExpiryReminder.refresh();
      refreshCards();
      closeModal();
      showToast('✅ 已清除截止时间');
    }
  }

  function saveDeadline() {
    const dateVal = document.getElementById('deadlineDateInput').value;
    const timeVal = document.getElementById('deadlineTimeInput').value;
    const noteVal = document.getElementById('deadlineNoteInput').value;

    if (!dateVal || !timeVal) {
      showToast('⚠️ 请填写日期和时间');
      return;
    }

    const deadlineStr = dateVal + 'T' + timeVal + ':00';
    DeadlineSave.setDeadline(currentEventId, {
      deadline: deadlineStr,
      note: noteVal,
      set_at: new Date().toISOString()
    });
    ExpiryReminder.refresh();
    refreshCards();
    closeModal();
    showToast('✅ 截止时间已保存');
  }

  // 刷新卡片显示
  function refreshCards() {
    if (typeof renderCards === 'function' && typeof currentResult !== 'undefined' && currentResult) {
      renderCards();
    }
  }

  // 在卡片上渲染截止时间区块
  function renderDeadlineBlock(eventId) {
    const dl = DeadlineSave.getDeadline(eventId);
    if (!dl) {
      return `
        <div class="deadline-section" style="margin-top:12px; padding-top:12px; border-top:1px solid #f0f0f0;">
          <button class="set-deadline-btn" data-event-id="${eventId}" style="
            width:100%; padding:8px; border:2px dashed #c7d2fe; border-radius:10px;
            background:#f8f9ff; color:#667eea; font-size:0.8rem; cursor:pointer;
            transition:all 0.2s; display:flex; align-items:center; justify-content:center; gap:6px;
          ">⏰ 设置截止时间</button>
        </div>
      `;
    }

    const deadlineDate = new Date(dl.deadline);
    const now = new Date();
    const isExpired = deadlineDate < now;
    const isToday = deadlineDate.toDateString() === now.toDateString();
    const isSoon = !isExpired && (deadlineDate - now) < 86400000;

    const formattedDate = (deadlineDate.getMonth() + 1) + '月' + deadlineDate.getDate() + '日 ' +
      pad(deadlineDate.getHours()) + ':' + pad(deadlineDate.getMinutes());

    let statusColor = '#10b981';
    let statusBg = '#d1fae5';
    let statusIcon = '🟢';
    let statusText = '进行中';

    if (isExpired) {
      statusColor = '#ef4444';
      statusBg = '#fee2e2';
      statusIcon = '🔴';
      statusText = '已过期';
    } else if (isToday) {
      statusColor = '#f59e0b';
      statusBg = '#fef3c7';
      statusIcon = '🟡';
      statusText = '今日截止';
    } else if (isSoon) {
      statusColor = '#f97316';
      statusBg = '#ffedd5';
      statusIcon = '🟠';
      statusText = '即将截止';
    }

    return `
      <div class="deadline-section" style="margin-top:12px; padding:12px; border-radius:12px;
        background:${statusBg}; border-left:4px solid ${statusColor};">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span style="font-size:0.75rem; font-weight:600; color:${statusColor};">
            ${statusIcon} 截止时间 · ${statusText}
          </span>
          <button class="edit-deadline-btn" data-event-id="${eventId}" style="
            border:none; background:rgba(255,255,255,0.5); color:${statusColor};
            font-size:0.7rem; padding:2px 8px; border-radius:6px; cursor:pointer;
          ">编辑</button>
        </div>
        <div style="font-size:0.95rem; font-weight:700; color:#1f2937; margin-bottom:4px;">
          ⏰ ${formattedDate}
        </div>
        ${dl.note ? `<div style="font-size:0.78rem; color:#6b7280;">📝 ${escapeHtml(dl.note)}</div>` : ''}
        <div style="font-size:0.68rem; color:#9ca3af; margin-top:4px;">
          设置于 ${formatTimeShort(dl.set_at)}
        </div>
      </div>
    `;
  }

  function pad(n) { return String(n).padStart(2, '0'); }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function formatTimeShort(isoStr) {
    if (!isoStr) return '-';
    const d = new Date(isoStr);
    return (d.getMonth() + 1) + '/' + d.getDate() + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }

  function showToast(msg) {
    const toast = document.getElementById('toast');
    if (toast) {
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    }
  }

  // 绑定卡片上的按钮点击
  function bindCardButtons() {
    document.querySelectorAll('.set-deadline-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        const eventId = parseInt(this.dataset.eventId);
        const event = (typeof currentResult !== 'undefined' && currentResult) ? currentResult.events[eventId] : null;
        openModal(eventId, event ? event.title : '事件 #' + eventId);
      });
    });
    document.querySelectorAll('.edit-deadline-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        const eventId = parseInt(this.dataset.eventId);
        const event = (typeof currentResult !== 'undefined' && currentResult) ? currentResult.events[eventId] : null;
        openModal(eventId, event ? event.title : '事件 #' + eventId);
      });
    });
  }

  return {
    init,
    openModal,
    closeModal,
    renderDeadlineBlock,
    bindCardButtons,
    refreshCards
  };
})();
