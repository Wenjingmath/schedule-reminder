/**
 * deadline_save.js - 截止时间保存逻辑模块
 * 使用 localStorage 持久化截止时间数据
 * 数据结构：{ eventId: { deadline, note, set_at } }
 */
const DeadlineSave = (function () {
  const STORAGE_KEY = 'schedule_reminder_deadlines';

  // 读取全部截止时间
  function getAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      console.error('读取截止时间失败:', e);
      return {};
    }
  }

  // 写入全部截止时间
  function saveAll(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      return true;
    } catch (e) {
      console.error('保存截止时间失败:', e);
      return false;
    }
  }

  // 获取单个截止时间
  function getDeadline(eventId) {
    const all = getAll();
    return all[eventId] || null;
  }

  // 设置/更新截止时间
  function setDeadline(eventId, data) {
    const all = getAll();
    all[eventId] = {
      deadline: data.deadline,
      note: data.note || '',
      set_at: data.set_at || new Date().toISOString()
    };
    return saveAll(all);
  }

  // 删除截止时间
  function removeDeadline(eventId) {
    const all = getAll();
    if (all[eventId]) {
      delete all[eventId];
      return saveAll(all);
    }
    return false;
  }

  // 获取所有已过期的截止时间
  function getExpired() {
    const all = getAll();
    const now = new Date();
    const expired = [];
    for (const id in all) {
      const dl = new Date(all[id].deadline);
      if (dl < now) {
        expired.push({
          eventId: parseInt(id),
          ...all[id],
          expired_at: dl.toISOString()
        });
      }
    }
    return expired;
  }

  // 获取今日截止的
  function getTodayDeadlines() {
    const all = getAll();
    const today = new Date();
    const todayStr = today.toDateString();
    const result = [];
    for (const id in all) {
      const dl = new Date(all[id].deadline);
      if (dl.toDateString() === todayStr) {
        result.push({
          eventId: parseInt(id),
          ...all[id]
        });
      }
    }
    return result;
  }

  // 获取即将截止的（24小时内）
  function getSoonDeadlines() {
    const all = getAll();
    const now = new Date();
    const result = [];
    for (const id in all) {
      const dl = new Date(all[id].deadline);
      const diff = dl - now;
      if (diff > 0 && diff < 86400000) {
        result.push({
          eventId: parseInt(id),
          ...all[id],
          remaining_ms: diff
        });
      }
    }
    return result.sort((a, b) => a.remaining_ms - b.remaining_ms);
  }

  // 统计信息
  function getStats() {
    const all = getAll();
    const now = new Date();
    let total = 0;
    let expired = 0;
    let today = 0;
    let soon = 0;
    let upcoming = 0;

    const todayStr = now.toDateString();
    for (const id in all) {
      total++;
      const dl = new Date(all[id].deadline);
      if (dl < now) {
        expired++;
      } else if (dl.toDateString() === todayStr) {
        today++;
      } else if ((dl - now) < 86400000) {
        soon++;
      } else {
        upcoming++;
      }
    }

    return { total, expired, today, soon, upcoming };
  }

  // 导出为 JSON
  function exportJSON() {
    return JSON.stringify(getAll(), null, 2);
  }

  // 从 JSON 导入
  function importJSON(jsonStr) {
    try {
      const data = JSON.parse(jsonStr);
      saveAll(data);
      return true;
    } catch (e) {
      console.error('导入截止时间失败:', e);
      return false;
    }
  }

  // 清空所有
  function clearAll() {
    localStorage.removeItem(STORAGE_KEY);
  }

  return {
    getAll,
    getDeadline,
    setDeadline,
    removeDeadline,
    getExpired,
    getTodayDeadlines,
    getSoonDeadlines,
    getStats,
    exportJSON,
    importJSON,
    clearAll
  };
})();
