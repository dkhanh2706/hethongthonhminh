async function send() {
  const score = document.getElementById("score").value;
  const time = document.getElementById("time").value;

  // check input
  if (!score || !time) {
    alert("Vui lòng nhập đầy đủ!");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        score: Number(score),
        time: Number(time),
      }),
    });

    const data = await res.json();

    document.getElementById("result").innerText = "Độ khó: " + data.level;
  } catch (error) {
    console.error(error);
    alert("Lỗi kết nối server!");
  }
}
