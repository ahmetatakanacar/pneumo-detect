const API_BASE_URL = "http://localhost:8000";
const TOKEN_KEY = "pneumodetect_token";

const authView = document.getElementById("auth-view");
const appView = document.getElementById("app-view");
const userBadge = document.getElementById("user-badge");
const userEmailEl = document.getElementById("user-email");
const userRoleEl = document.getElementById("user-role");
const logoutBtn = document.getElementById("logout-btn");

const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginError = document.getElementById("login-error");
const loginInfo = document.getElementById("login-info");
const registerError = document.getElementById("register-error");
const registerSuccess = document.getElementById("register-success");

const uploadForm = document.getElementById("upload-form");
const uploadBtn = document.getElementById("upload-btn");
const dropzone = document.getElementById("dropzone");
const dropzoneFilename = document.getElementById("dropzone-filename");
const xrayFileInput = document.getElementById("xray-file");
const uploadError = document.getElementById("upload-error");
const resultBox = document.getElementById("result-box");
const resultLabel = document.getElementById("result-label");
const resultIcon = document.getElementById("result-icon");
const resultText = document.getElementById("result-text");
const resultConfidence = document.getElementById("result-confidence");
const confidenceFill = document.getElementById("confidence-fill");
const resultId = document.getElementById("result-id");
const resultDate = document.getElementById("result-date");

const ICON_CHECK =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>';
const ICON_ALERT =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4" /><path d="M12 17h.01" /><path d="M10.3 3.86 1.82 18a1 1 0 0 0 .86 1.5h18.64a1 1 0 0 0 .86-1.5L13.7 3.86a1 1 0 0 0-1.72 0Z" /></svg>';

const sideGuest = document.getElementById("side-guest");
const sideUser = document.getElementById("side-user");
const sideUserIcon = document.getElementById("side-user-icon");
const sideUserHeading = document.getElementById("side-user-heading");

const ROLE_INFO = {
  doctor: {
    greeting: "Hoşgeldin, Doktor",
    icon: '<path d="M6 3v7a6 6 0 0 0 12 0V3" /><path d="M9 3h-3" /><path d="M18 3h-3" /><circle cx="20" cy="10" r="2" /><path d="M12 16v3a4 4 0 0 1-4 4" />',
  },
  admin: {
    greeting: "Hoşgeldin, Yönetici",
    icon: '<path d="M12 3 4 6.5v5c0 4.6 3.2 8.7 8 9.9 4.8-1.2 8-5.3 8-9.9v-5Z" />',
  },
  readonly: {
    greeting: "Hoşgeldin",
    icon: '<path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12Z" /><circle cx="12" cy="12" r="3" />',
  },
};

function updateDropzoneFilename() {
  const file = xrayFileInput.files[0];
  dropzoneFilename.textContent = file ? file.name : "";
}

dropzone.addEventListener("click", () => xrayFileInput.click());
dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    xrayFileInput.click();
  }
});
xrayFileInput.addEventListener("change", updateDropzoneFilename);

["dragover", "dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (e) => e.preventDefault());
});
dropzone.addEventListener("dragover", () => dropzone.classList.add("dragover"));
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
dropzone.addEventListener("drop", (e) => {
  dropzone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) {
    xrayFileInput.files = e.dataTransfer.files;
    updateDropzoneFilename();
  }
});

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function showAuthView() {
  authView.classList.remove("hidden");
  appView.classList.add("hidden");
  userBadge.classList.add("hidden");
  sideUser.classList.add("hidden");
  sideGuest.classList.remove("hidden");
}

function showAppView(user) {
  authView.classList.add("hidden");
  appView.classList.remove("hidden");
  userBadge.classList.remove("hidden");
  userEmailEl.textContent = user.email;
  userRoleEl.textContent = user.role;

  const roleInfo = ROLE_INFO[user.role] || ROLE_INFO.readonly;
  sideUserHeading.textContent = roleInfo.greeting;
  sideUserIcon.innerHTML = roleInfo.icon;
  sideGuest.classList.add("hidden");
  sideUser.classList.remove("hidden");
}

function switchTab(which) {
  const isLogin = which === "login";
  tabLogin.classList.toggle("active", isLogin);
  tabRegister.classList.toggle("active", !isLogin);
  loginForm.classList.toggle("hidden", !isLogin);
  registerForm.classList.toggle("hidden", isLogin);
  loginError.classList.add("hidden");
  loginInfo.classList.add("hidden");
  registerError.classList.add("hidden");
  registerSuccess.classList.add("hidden");
}

tabLogin.addEventListener("click", () => switchTab("login"));
tabRegister.addEventListener("click", () => switchTab("register"));

async function bootstrap() {
  const token = getToken();
  if (!token) {
    showAuthView();
    return;
  }
  try {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("invalid token");
    const user = await res.json();
    showAppView(user);
  } catch {
    clearToken();
    showAuthView();
  }
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.classList.add("hidden");
  loginInfo.classList.add("hidden");

  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Giriş başarısız");
    }

    const data = await res.json();
    setToken(data.access_token);

    const meRes = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    const user = await meRes.json();
    showAppView(user);
    loginForm.reset();
  } catch (err) {
    loginError.textContent = err.message;
    loginError.classList.remove("hidden");
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  registerError.classList.add("hidden");
  registerSuccess.classList.add("hidden");

  const email = document.getElementById("register-email").value;
  const password = document.getElementById("register-password").value;

  try {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Kayıt başarısız");
    }

    registerForm.reset();
    switchTab("login");
    document.getElementById("login-email").value = email;
    loginInfo.textContent = "Kayıt başarılı! Şimdi giriş yapabilirsin.";
    loginInfo.classList.remove("hidden");
  } catch (err) {
    registerError.textContent = err.message;
    registerError.classList.remove("hidden");
  }
});

logoutBtn.addEventListener("click", () => {
  clearToken();
  resultBox.classList.add("hidden");
  uploadError.classList.add("hidden");
  uploadForm.reset();
  dropzoneFilename.textContent = "";
  showAuthView();
});

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  uploadError.classList.add("hidden");
  resultBox.classList.add("hidden");

  const file = xrayFileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Analiz ediliyor...";

  try {
    const res = await fetch(`${API_BASE_URL}/upload-xray`, {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
      body: formData,
    });

    const body = await res.json().catch(() => ({}));

    if (res.status === 403) {
      throw new Error(
        "Bu hesap 'readonly' yetkisinde, röntgen yükleyemez. " +
          "Yükleme yapabilmek için hesabın DOCTOR/ADMIN rolüne yükseltilmesi gerekir " +
          "(demo ortamında veritabanından elle yapılır)."
      );
    }
    if (!res.ok) {
      throw new Error(body.detail || "Analiz başarısız oldu.");
    }

    const isNormal = body.result === "NORMAL";
    resultText.textContent = isNormal ? "NORMAL" : "PNÖMONİ ŞÜPHESİ";
    resultIcon.innerHTML = isNormal ? ICON_CHECK : ICON_ALERT;
    resultLabel.className = "result-label " + (isNormal ? "normal" : "pneumonia");
    const confidencePct = body.confidence * 100;
    resultConfidence.textContent = confidencePct.toFixed(1) + "%";
    confidenceFill.style.width = confidencePct + "%";
    confidenceFill.style.background = isNormal ? "var(--success)" : "var(--danger)";
    resultId.textContent = body.id;
    resultDate.textContent = new Date(body.created_at).toLocaleString("tr-TR");
    resultBox.classList.remove("hidden");
  } catch (err) {
    uploadError.textContent = err.message;
    uploadError.classList.remove("hidden");
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Analiz Et";
  }
});

bootstrap();