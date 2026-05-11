const API_BASE = "http://127.0.0.1:8000";

const imageInput = document.querySelector("#imageInput");
const preview = document.querySelector("#preview");
const uploader = document.querySelector(".uploader");
const uploadText = document.querySelector("#uploadText");
const needInput = document.querySelector("#needInput");
const analyzeBtn = document.querySelector("#analyzeBtn");
const statusEl = document.querySelector("#status");
const resultEl = document.querySelector("#result");

imageInput.addEventListener("change", () => {
  const file = imageInput.files?.[0];
  if (!file) {
    preview.removeAttribute("src");
    uploader.classList.remove("has-image");
    uploadText.textContent = "上传商品图片";
    return;
  }

  preview.src = URL.createObjectURL(file);
  uploader.classList.add("has-image");
  uploadText.textContent = "更换图片";
});

analyzeBtn.addEventListener("click", async () => {
  const formData = new FormData();
  const file = imageInput.files?.[0];
  if (file) {
    formData.append("image", file);
  }
  formData.append("need", needInput.value.trim());

  analyzeBtn.disabled = true;
  statusEl.textContent = "正在分析商品图片和需求";
  resultEl.className = "result empty";
  resultEl.innerHTML = "<p>正在生成推荐结果...</p>";

  try {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    statusEl.textContent = "分析完成";
    renderResult(data);
  } catch (error) {
    statusEl.textContent = "分析失败";
    resultEl.className = "result empty";
    resultEl.innerHTML = `<p class="error">无法连接后端服务，请确认 FastAPI 已在 127.0.0.1:8000 启动。</p>`;
  } finally {
    analyzeBtn.disabled = false;
  }
});

function renderResult(data) {
  resultEl.className = "result";
  resultEl.innerHTML = `
    <div class="summary">${escapeHtml(data.summary)}</div>
    <div class="metrics">
      ${metric("商品类别", `${escapeHtml(data.category)} ${Math.round(data.confidence * 100)}%`)}
      ${metric("主色", `<span class="swatch" style="background:${data.visual_features.color_hex}"></span>${escapeHtml(data.visual_features.primary_color)}`)}
      ${metric("亮度", escapeHtml(data.visual_features.brightness))}
      ${metric("饱和度", escapeHtml(data.visual_features.saturation))}
    </div>
    <div class="grid">
      ${listSection("风格标签", data.visual_features.style_tags)}
      ${listSection("卖点总结", data.selling_points)}
      ${listSection("适用场景", data.suitable_scenarios)}
      ${listSection("购买建议", data.purchase_advice)}
    </div>
    ${listSection("对比分析", data.comparison)}
    <div class="section">
      <h2>相似商品推荐</h2>
      <div class="recs">
        ${data.recommendations.map(renderRecommendation).join("")}
      </div>
    </div>
  `;
}

function metric(label, value) {
  return `
    <div class="metric">
      <span>${label}</span>
      <strong>${value}</strong>
    </div>
  `;
}

function listSection(title, items) {
  return `
    <div class="section">
      <h2>${title}</h2>
      <ul>
        ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderRecommendation(item) {
  return `
    <div class="rec">
      <strong>${escapeHtml(item.name)}</strong>
      <small>${escapeHtml(item.category)} · 匹配分 ${item.score}</small>
      <span>${escapeHtml(item.reason)}</span>
    </div>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
