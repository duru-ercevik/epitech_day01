// Admin paneli ayarları: dört tablonun tamamı, tüm işlemler açık

const ROLE_OPTIONS = [
    { value: "user", label: "Kullanıcı" },
    { value: "recruiter", label: "Şirket temsilcisi (recruiter)" },
    { value: "admin", label: "Yönetici (admin)" },
  ];
  
  const ROLE_NAMES = { user: "Kullanıcı", recruiter: "Recruiter", admin: "Admin" };
  
  const companyOptions = () => optionsFrom("/api/companies", (c) => c.name);
  const personOptions = () => optionsFrom("/api/people", (p) =>
    `${p.first_name} ${p.last_name}${p.company_name ? ` (${p.company_name})` : ""}`);
  const adOptions = () => optionsFrom("/api/ads", (a) => `#${a.id} ${a.title} · ${a.company_name}`);
  
  const ADMIN_RESOURCES = [
    {
      key: "ads",
      label: "İlanlar",
      singular: "ilan",
      endpoint: "/api/ads",
      canCreate: true,
      canEdit: true,
      canDelete: true,
      columns: [
        { key: "id", label: "#" },
        { key: "title", label: "Başlık" },
        { key: "company_name", label: "Şirket" },
        { key: "location", label: "Konum" },
        { key: "is_active", label: "Durum", format: (v) => yesNo(v, "Açık", "Kapalı") },
        { key: "created_at", label: "Tarih", format: (v) => formatDate(v) },
      ],
      fields: [
        { name: "title", label: "Başlık", required: true, wide: true },
        { name: "short_description", label: "Kısa açıklama", required: true, wide: true },
        { name: "full_description", label: "Tam açıklama", type: "textarea" },
        { name: "company_id", label: "Şirket", type: "select", numeric: true, required: true, loadOptions: companyOptions },
        { name: "contact_person_id", label: "Sorumlu kişi", type: "select", numeric: true, allowEmpty: true, loadOptions: personOptions },
        { name: "salary", label: "Maaş" },
        { name: "location", label: "Konum" },
        { name: "working_time", label: "Çalışma şekli", hint: "Örn. Tam zamanlı, Hibrit" },
        { name: "contract_type", label: "Sözleşme türü", hint: "Örn. Kalıcı, Staj" },
        { name: "is_active", label: "Başvuruya açık", type: "checkbox" },
      ],
    },
    {
      key: "companies",
      label: "Şirketler",
      singular: "şirket",
      endpoint: "/api/companies",
      canCreate: true,
      canEdit: true,
      canDelete: true,
      columns: [
        { key: "id", label: "#" },
        { key: "name", label: "Ad" },
        { key: "city", label: "Şehir" },
        { key: "website", label: "Web sitesi" },
      ],
      fields: [
        { name: "name", label: "Şirket adı", required: true },
        { name: "city", label: "Şehir" },
        { name: "website", label: "Web sitesi", type: "url", wide: true },
        { name: "description", label: "Açıklama", type: "textarea" },
      ],
    },
    {
      key: "people",
      label: "Kişiler",
      singular: "kişi",
      endpoint: "/api/people",
      canCreate: true,
      canEdit: true,
      canDelete: true,
      columns: [
        { key: "id", label: "#" },
        { key: "first_name", label: "Ad soyad", format: (v, p) => escapeHtml(`${p.first_name} ${p.last_name}`) },
        { key: "email", label: "E-posta" },
        { key: "role", label: "Rol", format: (v) => escapeHtml(ROLE_NAMES[v] || v) },
        { key: "company_name", label: "Şirket" },
      ],
      fields: [
        { name: "first_name", label: "Ad", required: true },
        { name: "last_name", label: "Soyad", required: true },
        { name: "email", label: "E-posta", type: "email", required: true },
        { name: "phone", label: "Telefon", type: "tel" },
        { name: "role", label: "Rol", type: "select", options: ROLE_OPTIONS, default: "user" },
        { name: "company_id", label: "Şirket", type: "select", numeric: true, allowEmpty: true,
          loadOptions: companyOptions, hint: "Sadece recruiter için gerekli" },
        { name: "password", label: "Şifre", type: "password", wide: true,
          hint: "Boş bırakılırsa kişi giriş yapamaz (örn. sadece iletişim kişisi)" },
      ],
    },
    {
      key: "applications",
      label: "Başvurular",
      singular: "başvuru",
      endpoint: "/api/applications",
      canCreate: true,
      canEdit: true,
      canDelete: true,
      columns: [
        { key: "id", label: "#" },
        { key: "name", label: "Aday" },
        { key: "email", label: "E-posta" },
        { key: "ad_title", label: "İlan" },
        { key: "email_sent", label: "E-posta gönderildi", format: (v) => yesNo(v) },
        { key: "created_at", label: "Tarih", format: (v) => formatDate(v) },
      ],
      fields: [
        // İlan sadece oluştururken seçilir, sonradan başka ilana taşınamaz
        { name: "ad_id", label: "İlan", type: "select", numeric: true, required: true, createOnly: true, wide: true, loadOptions: adOptions },
        { name: "name", label: "Aday adı", required: true },
        { name: "email", label: "E-posta", type: "email", required: true },
        { name: "phone", label: "Telefon", type: "tel" },
        { name: "message", label: "Mesaj", type: "textarea" },
        { name: "email_sent", label: "Adaya e-posta gönderildi", type: "checkbox", editOnly: true },
      ],
    },
  ];
  
  document.addEventListener("DOMContentLoaded", () => {
    initPanel({
      allowedRoles: ["admin"],
      resources: ADMIN_RESOURCES,
    });
  });