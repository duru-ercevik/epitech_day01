// Job board sayfası: ilan listesi, "Learn more", "Apply" ve sayfalama

let currentUser = null;
let currentPage = 1;
const PAGE_SIZE = 10;

const adsList = document.getElementById("ads-list");
const adsSummary = document.getElementById("ads-summary");
const pagination = document.getElementById("pagination");

// Sayfa açılınca: önce menüyü (ve giriş yapan kişiyi), sonra ilanları yükle
document.addEventListener("DOMContentLoaded", async () => {
  currentUser = await renderNav();
  loadAds(1);
});

// ---------- İlan listesi ----------

async function loadAds(page) {
  try {
    const data = await api(`/api/ads?page=${page}&limit=${PAGE_SIZE}`);
    currentPage = data.page;

    if (data.items.length === 0) {
      adsList.innerHTML = `<p class="muted">Şu an yayında ilan yok.</p>`;
      adsSummary.textContent = "";
      pagination.innerHTML = "";
      return;
    }

    adsSummary.textContent = `${data.total} ilan bulundu`;
    adsList.innerHTML = data.items.map(renderAdCard).join("");
    renderPagination(data);
  } catch (error) {
    adsList.innerHTML = `<p class="error">İlanlar yüklenemedi: ${escapeHtml(error.message)}</p>`;
  }
}

function renderAdCard(ad) {
  const closedBadge = ad.is_active ? "" : `<span class="badge badge-closed">Başvuruya kapalı</span>`;

  return `
    <article class="card ad-card" data-ad-id="${ad.id}">
      <div class="ad-header">
        <div>
          <h2 class="ad-title">${escapeHtml(ad.title)}</h2>
          <p class="ad-company">${escapeHtml(ad.company_name)} · ${escapeHtml(ad.location || "Konum belirtilmemiş")}</p>
        </div>
        ${closedBadge}
      </div>

      <p class="ad-short">${escapeHtml(ad.short_description)}</p>

      <div class="ad-actions">
        <button type="button" class="btn btn-ghost" data-action="details">Learn more</button>
        <button type="button" class="btn" data-action="apply" ${ad.is_active ? "" : "disabled"}>Apply</button>
      </div>

      <!-- "Learn more" ve "Apply" içerikleri buraya, kartın içine açılır (popup yok) -->
      <div class="ad-details" hidden></div>
      <div class="ad-apply" hidden></div>
    </article>
  `;
}

// Kartlardaki butonlar: her karta ayrı dinleyici eklemek yerine listeye tek bir dinleyici
adsList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const card = button.closest(".ad-card");
  const adId = card.dataset.adId;

  if (button.dataset.action === "details") toggleDetails(card, adId, button);
  if (button.dataset.action === "apply") toggleApplyForm(card, adId);
});

// ---------- Learn more ----------

async function toggleDetails(card, adId, button) {
  const details = card.querySelector(".ad-details");

  // Açıksa kapat
  if (!details.hidden) {
    details.hidden = true;
    button.textContent = "Learn more";
    return;
  }

  details.hidden = false;
  button.textContent = "Daha az göster";

  // Detaylar bir kez yüklendiyse tekrar istek atma
  if (details.dataset.loaded) return;

  details.innerHTML = `<p class="muted">Yükleniyor...</p>`;
  try {
    // Sayfa yenilenmeden, sadece bu ilanın detayları API'den çekilir
    const ad = await api(`/api/ads/${adId}`);
    details.innerHTML = `
      <p>${escapeHtml(ad.full_description || ad.short_description)}</p>
      <dl class="details-grid">
        <div><dt>Maaş</dt><dd>${escapeHtml(ad.salary || "Belirtilmemiş")}</dd></div>
        <div><dt>Konum</dt><dd>${escapeHtml(ad.location || "Belirtilmemiş")}</dd></div>
        <div><dt>Çalışma şekli</dt><dd>${escapeHtml(ad.working_time || "Belirtilmemiş")}</dd></div>
        <div><dt>Sözleşme</dt><dd>${escapeHtml(ad.contract_type || "Belirtilmemiş")}</dd></div>
        <div><dt>Şirket</dt><dd>${escapeHtml(ad.company_name)}</dd></div>
        <div><dt>Yayın tarihi</dt><dd>${formatDate(ad.created_at)}</dd></div>
      </dl>
    `;
    details.dataset.loaded = "true";
  } catch (error) {
    details.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---------- Apply ----------

function toggleApplyForm(card, adId) {
  const box = card.querySelector(".ad-apply");

  if (!box.hidden) {
    box.hidden = true;
    return;
  }

  // Giriş yapmış kullanıcı bilgilerini tekrar yazmaz, sadece mesaj alanı görünür
  const personalFields = currentUser
    ? `<p class="muted">${escapeHtml(currentUser.first_name)} ${escapeHtml(currentUser.last_name)}
         (${escapeHtml(currentUser.email)}) olarak başvuruyorsunuz.</p>`
    : `
      <div class="form-row">
        <label>Ad soyad <input name="name" required></label>
        <label>E-posta <input name="email" type="email" required></label>
      </div>
      <label>Telefon <input name="phone" type="tel"></label>
    `;

  box.innerHTML = `
    <form class="apply-form">
      <h3>Başvuru formu</h3>
      ${personalFields}
      <label>İlan sahibine mesajınız
        <textarea name="message" rows="4" placeholder="Kendinizden kısaca bahsedin..."></textarea>
      </label>
      <div class="form-actions">
        <button type="submit" class="btn">Başvuruyu gönder</button>
        <p class="form-message" role="status"></p>
      </div>
    </form>
  `;
  box.hidden = false;

  box.querySelector("form").addEventListener("submit", (event) => submitApplication(event, adId, box));
}

async function submitApplication(event, adId, box) {
  event.preventDefault();  // formun sayfayı yenilemesini engelle

  const form = event.target;
  const message = form.querySelector(".form-message");
  const submitButton = form.querySelector("button[type=submit]");

  // Form alanlarını { name: ..., email: ... } nesnesine çevir
  const body = Object.fromEntries(new FormData(form));
  body.ad_id = Number(adId);

  submitButton.disabled = true;
  message.className = "form-message";
  message.textContent = "Gönderiliyor...";

  try {
    await api("/api/applications", { method: "POST", body });
    box.innerHTML = `<p class="success">Başvurunuz alındı. Teşekkürler!</p>`;
  } catch (error) {
    message.className = "form-message error";
    message.textContent = error.message;
    submitButton.disabled = false;
  }
}

// ---------- Sayfalama ----------

function renderPagination(data) {
  if (data.pages <= 1) {
    pagination.innerHTML = "";
    return;
  }

  pagination.innerHTML = `
    <button type="button" class="btn btn-ghost" data-page="${data.page - 1}" ${data.page <= 1 ? "disabled" : ""}>← Önceki</button>
    <span>Sayfa ${data.page} / ${data.pages}</span>
    <button type="button" class="btn btn-ghost" data-page="${data.page + 1}" ${data.page >= data.pages ? "disabled" : ""}>Sonraki →</button>
  `;
}

pagination.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-page]");
  if (!button || button.disabled) return;
  loadAds(Number(button.dataset.page));
  window.scrollTo({ top: 0, behavior: "smooth" });
});