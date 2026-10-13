/**
 * expiry_reminder.js - 过期提醒模块
 * 定时检查截止时间，自动发现过期/即将过期项目，展示可视化提醒
 */
const ExpiryReminder = (function () {
  let checkInterval = null;
  let notifiedIds = new Set();
  let bannerEl = null;

  // 启动定时检查
  function start(intervalMs) {
    stop();
    check();
    checkInterval = setInterval(check, intervalMs || 60000);
    injectBannerStyles();
  }

  // 停止
  function stop() {
    if (checkInterval) {
      clearInterval(checkInterval);
      checkInterval = null;
    }
  }

  // 执行检查
  function check() {
    const expired = DeadlineSave.getExpired();
    const today = DeadlineSave.getTodayDeadlines();
    const soon = DeadlineSave.getSoonDeadlines();
    const stats = DeadlineSave.getStats();

    updateBanner(stats, expired, today, soon);

    expired.forEach(item => {
      if (!notifiedIds.has(item.eventId)) {
        notifiedIds.add(item.eventId);
        showToast(`🔴 事件已过期！` + getEventTitle(item.eventId), 'error');
      }
    });

    soon.forEach(item => {
      const notifyKey = 'soon_' + item.eventId + '_' + new Date(item.deadline).toDateString();
      if (!notifiedIds.has(notifyKey)) {
        notifiedIds.add(notifyKey);
        const hours = Math.floor(item.remaining_ms / 3600000);
        const mins = Math.floor((item.remaining_ms % 3600000) / 60000);
        showToast(`🟠 即将截止：${getEventTitle(item.eventId)} - 剩余 ${hours}h${mins}m`, 'warning');
      }
    });

    applyExpiryStyles();
  }

  // 获取事件标题
  function getEventTitle(eventId) {
    if (typeof currentResult !== 'undefined' && currentResult && currentResult.events[eventId]) {
      return currentResult.events[eventId].title;
    }
    return '事件 #' + eventId;
  }

  // 注入横幅样式
  function injectBannerStyles() {
    if (document.getElementById('expiry-banner-styles')) return;
    const style = document.createElement('style');
    style.id = 'expiry-banner-styles';
    style.textContent = `
      .expiry-banner {
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        z-index: 1500; min-width: 320px; max-width: 500px;
        border-radius: 14px; padding: 14px 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        display: none; align-items: center; gap: 12px;
        backdrop-filter: blur(10px);
        animation: slideDown 0.4s ease;
      }
      @keyframes slideDown {
        from { opacity:0; transform: translateX(-50%) translateY(-20px); }
        to { opacity:1; transform: translateX(-50%) translateY(0); }
      }
      .expiry-banner.show { display: flex; }
      .expiry-banner.has-expired { background: linear-gradient(135deg, #fee2e2, #fecaca); border: 1px solid #f87171; }
      .expiry-banner.only-soon { background: linear-gradient(135deg, #fef3c7, #fde68a); border: 1px solid #fbbf24; }
      .expiry-banner.all-clear { background: linear-gradient(135deg, #d1fae5, #a7f3d0); border: 1px solid #10b981; }
      .expiry-banner .banner-icon { font-size: 1.5rem; flex-shrink: 0; }
      .expiry-banner .banner-content { flex: 1; }
      .expiry-banner .banner-title { font-size: 0.85rem; font-weight: 700; }
      .expiry-banner .banner-detail { font-size: 0.72rem; opacity: 0.85; margin-top: 2px; }
      .expiry-banner .banner-close {
        background: rgba(255,255,255,0.5); border: none; border-radius: 6px;
        padding: 4px 8px; cursor: pointer; font-size: 0.7rem; color: #555;
        flex-shrink: 0;
      }

      .event-card.expired-card {
        animation: expiredPulse 2s ease-in-out infinite;
      }
      @keyframes expiredPulse {
        0%, 100% { box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        50% { box-shadow: 0 4px 30px rgba(239,68,68,0.3), 0 0 0 2px rgba(239,68,68,0.15); }
      }
      .event-card.expired-card .card-banner {
        filter: saturate(0.4);
      }
      .event-card.expired-card .card-banner::after {
        background: rgba(239,68,68,0.15) !important;
      }

      .event-card.soon-card .card-banner {
        box-shadow: inset 0 -3px 0 #f59e0b;
      }
    `;
    document.head.appendChild(style);
  }

  // 更新顶部横幅
  function updateBanner(stats, expired, today, soon) {
    if (!bannerEl) {
      bannerEl = document.createElement('div');
      bannerEl.className = 'expiry-banner';
      document.body.appendChild(bannerEl);
    }

    if (stats.total === 0) {
      bannerEl.classList.remove('show');
      return;
    }

    let icon = '✅';
    let title = '';
    let details = [];
    let cls = 'all-clear';

    if (stats.expired > 0) {
      icon = '🔴';
      title = `${stats.expired} 个截止时间已过期`;
      cls = 'has-expired';
    } else if (stats.today > 0) {
      icon = '🟡';
      title = `${stats.today} 个今日截止`;
      cls = 'only-soon';
    } else if (stats.soon > 0) {
      icon = '🟠';
      title = `${stats.soon} 个即将截止`;
      cls = 'only-soon';
    } else {
      icon = '🟢';
      title = `${stats.upcoming} 个待办截止`;
      cls = 'all-clear';
    }

    if (stats.expired > 0) details.push(`过期 ${stats.expired}`);
    if (stats.today > 0) details.push(`今日 ${stats.today}`);
    if (stats.soon > 0) details.push(`即将 ${stats.soon}`);
    if (stats.upcoming > 0) details.push(`待办 ${stats.upcoming}`);
    details.push(`合计 ${stats.total}`);

    bannerEl.className = `expiry-banner show ${cls}`;
    bannerEl.innerHTML = `
      <div class="banner-icon">${icon}</div>
      <div class="banner-content">
        <div class="banner-title">${title}</div>
        <div class="banner-detail">${details.join(' · ')}</div>
      </div>
      <button class="banner-close" onclick="this.parentElement.classList.remove('show')">关闭</button>
    `;
  }

  // 给卡片添加过期样式
  function applyExpiryStyles() {
    const all = DeadlineSave.getAll();
    const now = new Date();
    const cards = document.querySelectorAll('.event-card');

    cards.forEach((card, idx) => {
      const eventId = idx;
      const dl = all[eventId];
      if (!dl) return;
      const deadlineDate = new Date(dl.deadline);
      const isExpired = deadlineDate < now;
      const isSoon = !isExpired && (deadlineDate - now) < 86400000;

      card.classList.remove('expired-card', 'soon-card');
      if (isExpired) {
        card.classList.add('expired-card');
      } else if (isSoon) {
        card.classList.add('soon-card');
      }
    });
  }

  // Toast 提醒
  function showToast(msg, type) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.style.background = type === 'error' ? '#dc2626' : (type === 'warning' ? '#f59e0b' : '#333');
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
      toast.style.background = '';
    }, 4000);
  }

  // 手动刷新
  function refresh() {
    check();
  }

  // 重置通知记忆（用于重新提醒已过期的）
  function resetNotifications() {
    notifiedIds.clear();
  }

  return {
    start,
    stop,
    check,
    refresh,
    resetNotifications,
    getStats: () => DeadlineSave.getStats()
  };
})();
