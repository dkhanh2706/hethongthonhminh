async function send(event) {
  event.preventDefault();

  const form = document.getElementById("form");
  const resultBox = document.getElementById("result");
  const submitBtn = document.getElementById("submitBtn");

  // Validate form
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const score = Number(document.getElementById("score").value);
  const time = Number(document.getElementById("time").value);

  // Disable button and show loading state
  submitBtn.disabled = true;
  resultBox.innerHTML = '<div class="spinner"></div> Đang xử lý...';
  resultBox.className = "result-box";

  try {
    const res = await fetch("http://127.0.0.1:5000/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        score: score,
        time: time,
      }),
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();

    // Display result with success styling
    resultBox.innerHTML = `<strong>Độ khó: ${escapeHtml(data.level)}</strong>`;
    resultBox.className = "result-box success";
  } catch (error) {
    console.error(error);
    resultBox.innerHTML = `<strong>⚠️ Lỗi:</strong> Không thể kết nối server. Vui lòng thử lại.`;
    resultBox.className = "result-box error";
  } finally {
    // Re-enable button
    submitBtn.disabled = false;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
