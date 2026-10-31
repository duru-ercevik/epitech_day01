// Recruiter paneli ayarları.
// Aynı panel motoru (panel.js) kullanılır; farklar sadece ayarlarda:
//  - sadece kendi şirketinin ilanları, başvuruları ve şirket bilgisi görünür
//  - kişiler sekmesi yok, şirket eklenemez/silinemez
//  - başvurularda sadece "e-posta gönderildi" işaretlenebilir
// Bu kısıtlar sadece görünüm için; asıl kontrolü backend yapıyor.

function recruiterResources(user) {
    return [
      {
        key: "ads",
        label: "İlanlarımız",
        singular: "ilan",
        endpoint: "/api/ads",
        listParams: `company_id=${user.company_id}`,
        canCreate: true,
        canEdit: true,
        canDelete: true,
        columns: [
          { key: "id", label: "#" },
          { key: "title", label: "Başlık" },
          { key: "location", label: "Konum" },
          { key: "working_time", label: "Çalışma şekli" },
          { key: "is_active", label: "Durum", format: (v) => yesNo(v, "Açık", "Kapalı") },
          { key: "created_at", label: "Tarih", format: (v) => formatDate(v) },
        ],
        // Şirket alanı yok: backend ilanı her zaman recruiter'ın kendi şirketine açar.
        // Sorumlu kişi de varsayılan olarak recruiter'ın kendisi olur.
        fields: [
          { name: "title", label: "Başlık", required: true, wide: true },
          { name: "short_description", label: "Kısa açıklama", required: true, wide: true },
          { name: "full_description", label: "Tam açıklama", type: "textarea" },
          { name: "salary", label: "Maaş" },
          { name: "location", label: "Konum" },
          { name: "working_time", label: "Çalışma şekli", hint: "Örn. Tam zamanlı, Hibrit" },
          { name: "contract_type", label: "Sözleşme türü", hint: "Örn. Kalıcı, Staj" },
          { name: "is_active", label: "Başvuruya açık", type: "checkbox" },
        ],
      },
      {
        key: "applications",
        label: "Gelen başvurular",
        singular: "başvuru",
        endpoint: "/api/applications",  // backend recruiter'a zaten sadece kendi şirketininkileri döndürür
        canCreate: false,
        canEdit: true,
        canDelete: false,
        columns: [
          { key: "id", label: "#" },
          { key: "name", label: "Aday" },
          { key: "email", label: "E-posta", format: (v) => `<a href="mailto:${escapeHtml(v)}">${escapeHtml(v)}</a>` },
          { key: "phone", label: "Telefon" },
          { key: "ad_title", label: "İlan" },
          { key: "message", label: "Mesaj", format: (v) => `<span class="cell-text">${escapeHtml(v || "-")}</span>` },
          { key: "email_sent", label: "Dönüş yapıldı", format: (v) => yesNo(v) },
          { key: "created_at", label: "Tarih", format: (v) => formatDate(v) },
        ],
        fields: [
          { name: "email_sent", label: "Adaya e-posta ile dönüş yapıldı", type: "checkbox", wide: true },
        ],
      },
      {
        key: "company",
        label: "Şirketim",
        singular: "şirket",
        endpoint: "/api/companies",
        canCreate: false,
        canEdit: true,
        canDelete: false,
        // Liste yerine sadece kendi şirketi gösterilir
        loadItems: async () => {
          const company = await api(`/api/companies/${user.company_id}`);
          return { items: [company], page: 1, pages: 1, total: 1 };
        },
        columns: [
          { key: "name", label: "Ad" },
          { key: "city", label: "Şehir" },
          { key: "website", label: "Web sitesi" },
          { key: "description", label: "Açıklama", format: (v) => `<span class="cell-text">${escapeHtml(v || "-")}</span>` },
        ],
        fields: [
          { name: "name", label: "Şirket adı", required: true },
          { name: "city", label: "Şehir" },
          { name: "website", label: "Web sitesi", type: "url", wide: true },
          { name: "description", label: "Açıklama", type: "textarea" },
        ],
      },
    ];
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    initPanel({
      allowedRoles: ["recruiter"],
      resources: recruiterResources,
      onReady: (user) => {
        document.getElementById("panel-company").textContent = user.company_name;
      },
    });
  });