const API_URL = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", function () {
  const username = localStorage.getItem("auth_username");
  const token = localStorage.getItem("auth_token");

  if (!username || !token) {
    window.location.href = "login.html";
    return;
  }

  fetch(API_URL + "/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, token }),
  })
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (!data.valid) {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_username");
        window.location.href = "login.html";
      } else {
        var welcomeEl = document.getElementById("welcomeUser");
        var avatarEl = document.getElementById("avatarInitial");
        if (welcomeEl) welcomeEl.textContent = username;
        if (avatarEl) avatarEl.textContent = username.charAt(0).toUpperCase();
      }
    })
    .catch(function () {
      window.location.href = "login.html";
    });
});

function logout() {
  var username = localStorage.getItem("auth_username");
  if (username) {
    fetch(API_URL + "/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username }),
    }).catch(function () {});
  }
  localStorage.removeItem("auth_token");
  localStorage.removeItem("auth_username");
  window.location.href = "login.html";
}

function showToast(msg, type) {
  var el = document.getElementById("toast");
  if (!el) return;
  var icon = type === "error"
    ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
  el.innerHTML = '<div class="toast ' + type + '">' + icon + '<span>' + msg + '</span></div>';
  setTimeout(function () {
    var toast = el.querySelector(".toast");
    if (toast) {
      toast.classList.add("hide");
      setTimeout(function () { el.innerHTML = ""; }, 300);
    }
  }, 4000);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function send(event) {
  event.preventDefault();

  const form = document.getElementById("form");
  const resultBox = document.getElementById("result");
  const submitBtn = document.getElementById("submitBtn");

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const score = Number(document.getElementById("score").value);
  const time = Number(document.getElementById("time").value);
  const username = localStorage.getItem("auth_username");

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-ring"></span>Đang phân tích...';
  resultBox.innerHTML = '<span class="result-spinner"></span> Đang phân tích hành vi học tập...';
  resultBox.className = "result-box loading";

  try {
    const res = await fetch(API_URL + "/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ score, time }),
    });

    if (!res.ok) throw new Error("Server error: " + res.status);
    const data = await res.json();

    var levelEmoji = "";
    if (data.level_num <= 1) levelEmoji = "🟢 ";
    else if (data.level_num <= 2) levelEmoji = "🟡 ";
    else levelEmoji = "🔴 ";

    var html = '<div class="result-content">';
    html += '<div class="result-main">';
    html += levelEmoji + '<strong style="font-size: 18px;">' + escapeHtml(data.level) + '</strong>';
    html += '</div>';

    if (data.topic) {
      html += '<div class="result-meta"><span class="badge topic-badge">' + escapeHtml(data.topic) + '</span></div>';
    }

    if (data.reasoning) {
      html += '<div class="result-reasoning"><strong>Lý do:</strong> ' + escapeHtml(data.reasoning) + '</div>';
    }

    if (data.strategy) {
      html += '<div class="result-strategy">';
      html += '<h4>' + escapeHtml(data.strategy.title) + '</h4>';
      html += '<p>' + escapeHtml(data.strategy.description) + '</p>';
      if (data.strategy.tips && data.strategy.tips.length > 0) {
        html += '<ul>';
        for (var i = 0; i < data.strategy.tips.length; i++) {
          html += '<li>' + escapeHtml(data.strategy.tips[i]) + '</li>';
        }
        html += '</ul>';
      }
      html += '</div>';
    }

    html += '</div>';

    resultBox.innerHTML = html;
    resultBox.className = "result-box success";
    showToast("Đã nhận gợi ý thành công!", "success");

    fetchAdaptiveRecommendations(username);
  } catch (error) {
    console.error(error);
    resultBox.innerHTML = "Không thể kết nối server. Vui lòng thử lại.";
    resultBox.className = "result-box error";
    showToast("Lỗi kết nối", "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Phân tích & Gợi ý';
  }
}

async function fetchAdaptiveRecommendations(username) {
  const adaptiveBox = document.getElementById("adaptiveResult");
  if (!adaptiveBox) return;

  adaptiveBox.innerHTML = '<span class="result-spinner"></span> Đang tải gợi ý cá nhân hóa...';
  adaptiveBox.className = "result-box loading";

  try {
    const res = await fetch(API_URL + "/recommend/adaptive", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, count: 5 }),
    });

    if (!res.ok) throw new Error("Server error: " + res.status);
    const response = await res.json();

    if (!response.success) {
      adaptiveBox.innerHTML = "Không thể tải gợi ý.";
      adaptiveBox.className = "result-box error";
      return;
    }

    const data = response.data;
    var html = '<div class="adaptive-content">';

    if (data.analysis_summary) {
      var summary = data.analysis_summary;
      html += '<div class="summary-grid">';

      html += '<div class="summary-card">';
      html += '<div class="summary-label">Mức độ tối ưu</div>';
      html += '<div class="summary-value level-value">' + (summary.optimal_difficulty ? summary.optimal_difficulty.label : 'N/A') + '</div>';
      if (summary.optimal_difficulty) {
        html += '<div class="summary-sub">Level ' + summary.optimal_difficulty.level + '</div>';
      }
      html += '</div>';

      html += '<div class="summary-card">';
      html += '<div class="summary-label">Kỹ năng yếu</div>';
      html += '<div class="summary-value weak-value">' + (summary.weak_areas_count || 0) + '</div>';
      html += '<div class="summary-sub">cần cải thiện</div>';
      html += '</div>';

      html += '<div class="summary-card">';
      html += '<div class="summary-label">Kỹ năng mạnh</div>';
      html += '<div class="summary-value strong-value">' + (summary.strong_areas_count || 0) + '</div>';
      html += '<div class="summary-sub">đã thành thạo</div>';
      html += '</div>';

      html += '<div class="summary-card">';
      html += '<div class="summary-label">Xu hướng</div>';
      var trendText = summary.overall_trend === 'improving' ? 'Tăng' :
                      summary.overall_trend === 'declining' ? 'Giảm' :
                      summary.overall_trend === 'stable' ? 'Ổn định' :
                      summary.overall_trend === 'new_student' ? 'Mới' : 'N/A';
      var trendClass = summary.overall_trend === 'improving' ? 'trend-up' :
                       summary.overall_trend === 'declining' ? 'trend-down' : 'trend-stable';
      html += '<div class="summary-value ' + trendClass + '">' + trendText + '</div>';
      html += '<div class="summary-sub">tiến trình</div>';
      html += '</div>';

      html += '</div>';
    }

    if (data.recommendations && data.recommendations.length > 0) {
      html += '<div class="rec-section"><h4>Câu hỏi gợi ý</h4>';
      for (var i = 0; i < data.recommendations.length; i++) {
        var rec = data.recommendations[i];
        var priorityClass = rec.priority === 'high' ? 'priority-high' :
                           rec.priority === 'medium' ? 'priority-medium' : 'priority-low';
        html += '<div class="rec-card ' + priorityClass + '">';
        html += '<div class="rec-header">';
        html += '<span class="rec-topic">' + escapeHtml(rec.topic) + ' > ' + escapeHtml(rec.subtopic) + '</span>';
        html += '<span class="rec-difficulty">Độ khó: ' + rec.question.difficulty + '/10</span>';
        html += '</div>';
        html += '<div class="rec-content">' + escapeHtml(rec.question.content) + '</div>';
        html += '<div class="rec-reason">' + escapeHtml(rec.reason) + '</div>';
        html += '<div class="rec-time">Thời gian dự kiến: ~' + rec.question.expected_time + ' phút</div>';
        html += '</div>';
      }
      html += '</div>';
    }

    if (data.learning_strategy) {
      var strat = data.learning_strategy;
      html += '<div class="strategy-section">';
      html += '<h4>Chiến lược học tập</h4>';
      html += '<div class="strategy-title">' + escapeHtml(strat.title) + '</div>';
      html += '<p>' + escapeHtml(strat.description) + '</p>';
      if (strat.tips && strat.tips.length > 0) {
        html += '<ul class="strategy-tips">';
        for (var j = 0; j < strat.tips.length; j++) {
          html += '<li>' + escapeHtml(strat.tips[j]) + '</li>';
        }
        html += '</ul>';
      }
      html += '</div>';
    }

    html += '</div>';

    adaptiveBox.innerHTML = html;
    adaptiveBox.className = "result-box success";
  } catch (error) {
    console.error(error);
    adaptiveBox.innerHTML = "Không thể tải gợi ý cá nhân hóa.";
    adaptiveBox.className = "result-box error";
  }
}

async function loadDashboard() {
  const username = localStorage.getItem("auth_username");
  if (!username) return;

  const dashBox = document.getElementById("dashboardResult");
  if (!dashBox) return;

  dashBox.innerHTML = '<span class="result-spinner"></span> Đang tải dashboard...';
  dashBox.className = "result-box loading";

  try {
    const res = await fetch(API_URL + "/learning/dashboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username }),
    });

    if (!res.ok) throw new Error("Server error: " + res.status);
    const response = await res.json();

    if (!response.success) {
      dashBox.innerHTML = "Không thể tải dashboard.";
      dashBox.className = "result-box error";
      return;
    }

    const data = response.data;
    var html = '<div class="dashboard-content">';

    if (data.stats) {
      html += '<div class="summary-grid">';
      html += '<div class="summary-card"><div class="summary-label">Tổng câu hỏi</div><div class="summary-value">' + data.stats.total_questions + '</div></div>';
      html += '<div class="summary-card"><div class="summary-label">Đúng</div><div class="summary-value strong-value">' + data.stats.total_correct + '</div></div>';
      html += '<div class="summary-card"><div class="summary-label">Độ chính xác</div><div class="summary-value">' + data.stats.accuracy + '%</div></div>';
      html += '<div class="summary-card"><div class="summary-label">Thời gian TB</div><div class="summary-value">' + data.stats.avg_time_per_question + ' phút</div></div>';
      html += '</div>';
    }

    html += '</div>';
    dashBox.innerHTML = html;
    dashBox.className = "result-box success";
  } catch (error) {
    console.error(error);
    dashBox.innerHTML = "Không thể tải dashboard.";
    dashBox.className = "result-box error";
  }
}
