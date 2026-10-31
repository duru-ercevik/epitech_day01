// Ortak yönetim paneli motoru.
// Admin ve recruiter panelleri aynı kodu kullanır, sadece verdikleri ayarlar farklıdır:
// hangi tablolar görünür, hangi sütunlar listelenir, formda hangi alanlar var,
// ekleme / düzenleme / silme yapılabilir mi.

const PANEL_PAGE_SIZE = 10;

const panel = {
  user: null,
  resources: [],
  current: null,  // seçili sekmenin ayarları
  page: 1,
};

/**
 * Paneli başlatır.
 * @param {object} config
 *   allowedRoles: bu sayfaya girebilecek roller, örn. ["admin"]
 *   resources: her sekme için ayar listesi (admin.js içinde örnekleri var)
 *   onReady(user): giriş kontrolünden sonra çalışan isteğe bağlı fonksiyon
 */
async function initPanel(config) {
  const user = await renderNav();

  // Sayfa koruması: giriş yoksa login'e, yetki yoksa kendi sayfasına gönder.
  // Asıl koruma backend'de; bu sadece kullanıcıyı boş bir sayfayla karşılamamak için.
  if (!user) {
    window.location.href = "/login.html";
    return;
  }
  if (!config.allowedRoles.includes(user.role)) {
    window.location.href = panelUrlFor(user) || "/";
    return;
  }

  panel.user = user;
  panel.resources = typeof config.resources === "function" ? config.resources(user) : config.resources;
  if (config.onReady) config.onReady(user);

  renderTabs();
  selectResource(panel.resources[0].key);
}

// ---------- Sekmeler ----------

function renderTabs() {
  const tabs = document.getElementById("panel-tabs");
  tabs.innerHTML = panel.resources
    .map((r) => `<button type="button" class="tab" data-key="${r.key}">${escapeHtml(r.label)}</button>`)
    .join("");

  tabs.addEventListener("click", (event) => {
    const button = event.target.closest(".tab");
    if (button) selectResource(button.dataset.key);
  });
}

function selectResource(key) {
  panel.current = panel.resources.find((r) => r.key === key);
  document.querySelectorAll("#panel-tabs .tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.key === key);
  });

  document.getElementById("panel-title").textContent = panel.current.label;
  const newButton = document.getElementById("panel-new");
  newButton.hidden = !panel.current.canCreate;
  newButton.textContent = `+ Yeni ${panel.current.singular || "kayıt"}`;

  closeForm();
  showMessage("");
  loadList(1);
}

// ---------- Liste ----------

async function loadList(page) {
  const resource = panel.current;
  const container = document.getElementById("panel-list");
  container.innerHTML = `<p class="muted">Yükleniyor...</p>`;

  try {
    // Ayarlarda loadItems varsa liste onunla yüklenir (örn. recruiter'ın tek şirketi).
    // Yoksa endpoint'ten sayfalı liste çekilir; listParams ek filtre ekler (örn. company_id=3).
    const extra = resource.listParams ? `&${resource.listParams}` : "";
    const data = resource.loadItems
      ? await resource.loadItems(page)
      : await api(`${resource.endpoint}?page=${page}&limit=${PANEL_PAGE_SIZE}${extra}`);
    panel.page = data.page;
    document.getElementById("panel-count").textContent = `${data.total} kayıt`;

    if (data.items.length === 0) {
      container.innerHTML = `<p class="muted">Henüz kayıt yok.</p>`;
    } else {
      container.innerHTML = renderTable(resource, data.items);
    }
    renderPanelPagination(data);
  } catch (error) {
    container.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderTable(resource, items) {
  const hasActions = resource.canEdit || resource.canDelete;

  const head = resource.columns.map((c) => `<th>${escapeHtml(c.label)}</th>`).join("")
    + (hasActions ? "<th></th>" : "");

  const rows = items.map((item) => {
    const cells = resource.columns.map((column) => {
      const value = item[column.key];
      // format fonksiyonu kendi HTML'ini üretir ve escape etmekten kendisi sorumludur
      const html = column.format ? column.format(value, item) : escapeHtml(value ?? "-");
      return `<td>${html}</td>`;
    }).join("");

    const actions = hasActions ? `
      <td class="row-actions">
        ${resource.canEdit ? `<button type="button" class="btn btn-small btn-ghost" data-edit="${item.id}">Düzenle</button>` : ""}
        ${resource.canDelete ? `<button type="button" class="btn btn-small btn-danger" data-delete="${item.id}">Sil</button>` : ""}
      </td>` : "";

    return `<tr>${cells}${actions}</tr>`;
  }).join("");

  // Geniş tablolar küçük ekranda sayfayı değil, sadece kendini kaydırır
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr>${head}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderPanelPagination(data) {
  const nav = document.getElementById("panel-pagination");
  if (data.pages <= 1) {
    nav.innerHTML = "";
    return;
  }
  nav.innerHTML = `
    <button type="button" class="btn btn-ghost btn-small" data-page="${data.page - 1}" ${data.page <= 1 ? "disabled" : ""}>← Önceki</button>
    <span>Sayfa ${data.page} / ${data.pages}</span>
    <button type="button" class="btn btn-ghost btn-small" data-page="${data.page + 1}" ${data.page >= data.pages ? "disabled" : ""}>Sonraki →</button>
  `;
}

// ---------- Düzenle / sil butonları ----------

document.addEventListener("click", async (event) => {
  const pageButton = event.target.closest("#panel-pagination button[data-page]");
  if (pageButton && !pageButton.disabled) {
    loadList(Number(pageButton.dataset.page));
    return;
  }

  const editButton = event.target.closest("button[data-edit]");
  if (editButton) {
    await openEditForm(editButton.dataset.edit);
    return;
  }

  const deleteButton = event.target.closest("button[data-delete]");
  if (deleteButton) {
    handleDelete(deleteButton);
  }
});

async function openEditForm(id) {
  try {
    // Listede bütün alanlar olmayabilir, kaydın güncel halini API'den al
    const record = await api(`${panel.current.endpoint}/${id}`);
    await openForm(record);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

/**
 * Silme iki adımlı: ilk tıklamada buton "Emin misin?" olur,
 * 3 saniye içinde tekrar tıklanırsa silinir. Yanlışlıkla silmeyi önler.
 */
async function handleDelete(button) {
  if (!button.dataset.confirming) {
    button.dataset.confirming = "true";
    button.textContent = "Emin misin?";
    setTimeout(() => {
      delete button.dataset.confirming;
      button.textContent = "Sil";
    }, 3000);
    return;
  }

  try {
    const result = await api(`${panel.current.endpoint}/${button.dataset.delete}`, { method: "DELETE" });
    showMessage(result.message, "success");
    closeForm();
    loadList(panel.page);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

// ---------- Ekleme / düzenleme formu ----------

document.getElementById("panel-new").addEventListener("click", () => openForm(null));

async function openForm(record) {
  const resource = panel.current;
  const isEdit = record !== null;
  const box = document.getElementById("panel-form");

  // Sadece bu modda görünecek alanlar
  const fields = resource.fields.filter((f) => (isEdit ? !f.createOnly : !f.editOnly));

  // Seçenekleri API'den gelen açılır listeleri (şirketler, kişiler...) doldur
  const options = {};
  for (const field of fields) {
    if (field.type === "select") {
      options[field.name] = field.loadOptions ? await field.loadOptions() : field.options;
    }
  }

  box.innerHTML = `
    <form id="record-form" class="card record-form" novalidate>
      <h3>${isEdit ? `${escapeHtml(resource.singular || "Kayıt")} düzenle (#${record.id})` : `Yeni ${escapeHtml(resource.singular || "kayıt")}`}</h3>
      <div class="form-grid">
        ${fields.map((f) => renderField(f, record, options[f.name], isEdit)).join("")}
      </div>
      <div class="form-actions">
        <button type="submit" class="btn">${isEdit ? "Kaydet" : "Oluştur"}</button>
        <button type="button" class="btn btn-ghost" id="form-cancel">Vazgeç</button>
        <p class="form-message" role="status"></p>
      </div>
    </form>
  `;
  box.hidden = false;
  box.scrollIntoView({ behavior: "smooth", block: "start" });

  const form = document.getElementById("record-form");
  document.getElementById("form-cancel").addEventListener("click", closeForm);
  form.addEventListener("submit", (event) => submitForm(event, fields, record));
}

function renderField(field, record, options, isEdit) {
  const value = record ? record[field.name] : field.default;
  const required = field.required && !(isEdit && field.type === "password");
  const label = escapeHtml(field.label) + (required ? " *" : "");
  const wide = field.wide || field.type === "textarea" ? " field-wide" : "";
  const hint = field.hint ? `<small class="muted">${escapeHtml(field.hint)}</small>` : "";

  if (field.type === "textarea") {
    return `<label class="field${wide}">${label}
      <textarea name="${field.name}" rows="4">${escapeHtml(value ?? "")}</textarea>${hint}</label>`;
  }

  if (field.type === "checkbox") {
    const checked = value === undefined ? true : Boolean(value);
    return `<label class="field field-checkbox${wide}">
      <input type="checkbox" name="${field.name}" ${checked ? "checked" : ""}> ${label}${hint}</label>`;
  }

  if (field.type === "select") {
    const optionHtml = (field.allowEmpty ? `<option value="">${escapeHtml(field.emptyLabel || "Seçilmedi")}</option>` : "")
      + options.map((o) => `<option value="${escapeHtml(o.value)}" ${String(o.value) === String(value ?? "") ? "selected" : ""}>${escapeHtml(o.label)}</option>`).join("");
    return `<label class="field${wide}">${label}
      <select name="${field.name}">${optionHtml}</select>${hint}</label>`;
  }

  // text, email, tel, url, number, password
  const inputValue = field.type === "password" ? "" : escapeHtml(value ?? "");
  const placeholder = field.type === "password" && isEdit ? 'placeholder="Değiştirmek istemiyorsan boş bırak"' : "";
  return `<label class="field${wide}">${label}
    <input type="${field.type || "text"}" name="${field.name}" value="${inputValue}" ${placeholder}>${hint}</label>`;
}

/** Form alanlarını API'nin beklediği türlere çevirir (sayı, true/false, null). */
function collectFormData(form, fields) {
  const body = {};
  for (const field of fields) {
    const input = form.elements[field.name];

    if (field.type === "checkbox") {
      body[field.name] = input.checked;
      continue;
    }

    const raw = input.value.trim();

    if (field.type === "password") {
      if (raw) body[field.name] = raw;  // boşsa gönderme, şifre değişmesin
      continue;
    }

    if (raw === "") {
      body[field.name] = null;
    } else if (field.type === "number" || field.numeric) {
      body[field.name] = Number(raw);
    } else {
      body[field.name] = raw;
    }
  }
  return body;
}

async function submitForm(event, fields, record) {
  event.preventDefault();
  const form = event.target;
  const message = form.querySelector(".form-message");
  const submitButton = form.querySelector("button[type=submit]");
  const isEdit = record !== null;
  const resource = panel.current;

  const body = collectFormData(form, fields);

  // Zorunlu alanları gönderimden önce kontrol et (backend de ayrıca kontrol ediyor)
  const missing = fields.find((f) => f.required && !(isEdit && f.type === "password") && (body[f.name] === null || body[f.name] === undefined));
  if (missing) {
    message.className = "form-message error";
    message.textContent = `${missing.label} zorunlu`;
    return;
  }

  submitButton.disabled = true;
  message.className = "form-message";
  message.textContent = "Kaydediliyor...";

  try {
    if (isEdit) {
      await api(`${resource.endpoint}/${record.id}`, { method: "PUT", body });
      showMessage(`#${record.id} güncellendi.`, "success");
    } else {
      const created = await api(resource.endpoint, { method: "POST", body });
      showMessage(`Yeni kayıt oluşturuldu (#${created.id}).`, "success");
    }
    closeForm();
    loadList(isEdit ? panel.page : 1);
  } catch (error) {
    message.className = "form-message error";
    message.textContent = error.message;
    submitButton.disabled = false;
  }
}

function closeForm() {
  const box = document.getElementById("panel-form");
  box.hidden = true;
  box.innerHTML = "";
}

function showMessage(text, type = "") {
  const element = document.getElementById("panel-message");
  element.textContent = text;
  element.className = `panel-message ${type}`;
  element.hidden = !text;
}

// ---------- Ayar dosyalarında kullanılan yardımcılar ----------

/** Açılır liste seçeneklerini bir API listesinden üretir. */
async function optionsFrom(endpoint, labelFn) {
  const data = await api(`${endpoint}?limit=100`);
  return data.items.map((item) => ({ value: item.id, label: labelFn(item) }));
}

/** true/false değeri tabloda okunur bir etikete çevirir. */
function yesNo(value, yes = "Evet", no = "Hayır") {
  return value ? `<span class="badge badge-on">${yes}</span>` : `<span class="badge badge-off">${no}</span>`;
}