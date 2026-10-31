// Tüm sayfaların ortak kullandığı yardımcı fonksiyonlar

/**
 * API'ye istek atar, JSON cevabı döndürür.
 * Cevap başarısızsa (400, 401, 404...) sunucunun hata mesajıyla bir Error fırlatır.
 */
async function api(path, options = {}) {
    const settings = {
      method: options.method || "GET",
      headers: {},
    };
  
    if (options.body !== undefined) {
      settings.headers["Content-Type"] = "application/json";
      settings.body = JSON.stringify(options.body);
    }
  
    const response = await fetch(path, settings);
    const data = await response.json().catch(() => ({}));
  
    if (!response.ok) {
      const error = new Error(data.error || "Bir hata oluştu");
      error.status = response.status;
      throw error;
    }
    return data;
  }
  
  /**
   * Metni HTML'e güvenli şekilde koymak için özel karakterleri dönüştürür.
   * Bu olmazsa biri ilan başlığına <script> yazarak sayfada kod çalıştırabilirdi (XSS).
   */
  function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
  
  /** SQLite tarihini ("2026-10-29 14:05:00", UTC) okunur Türkçe tarihe çevirir. */
  function formatDate(value) {
    if (!value) return "-";
    const date = new Date(value.replace(" ", "T") + "Z");
    return date.toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" });
  }
  
  /** Giriş yapmış kullanıcıyı döndürür, giriş yoksa null. */
  async function getCurrentUser() {
    try {
      return await api("/api/auth/me");
    } catch (error) {
      return null;
    }
  }
  
  /** Kullanıcının rolüne göre gideceği panel sayfası. */
  function panelUrlFor(user) {
    if (user.role === "admin") return "/admin.html";
    if (user.role === "recruiter") return "/recruiter.html";
    return null;
  }
  
  /** Üst menüyü giriş durumuna göre doldurur. */
  async function renderNav() {
    const nav = document.getElementById("nav-links");
    if (!nav) return null;
  
    const user = await getCurrentUser();
  
    if (!user) {
      nav.innerHTML = `
        <a href="/login.html">Giriş yap</a>
        <a href="/account.html" class="btn btn-small">Hesap oluştur</a>
      `;
      return null;
    }
  
    const panelUrl = panelUrlFor(user);
    nav.innerHTML = `
      ${panelUrl ? `<a href="${panelUrl}">Panel</a>` : ""}
      <a href="/account.html">${escapeHtml(user.first_name)}</a>
      <button type="button" class="btn btn-small btn-ghost" id="logout-btn">Çıkış</button>
    `;
  
    document.getElementById("logout-btn").addEventListener("click", async () => {
      await api("/api/auth/logout", { method: "POST" });
      window.location.href = "/";
    });
  
    return user;
  }