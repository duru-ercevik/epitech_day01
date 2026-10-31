// Hesap sayfası: giriş yapılmamışsa "hesap oluştur", yapılmışsa "hesabı düzenle"

const ROLE_LABELS = {
    user: "Kullanıcı",
    recruiter: "Şirket temsilcisi",
    admin: "Yönetici",
  };
  
  document.addEventListener("DOMContentLoaded", async () => {
    const user = await renderNav();
  
    const form = document.getElementById("account-form");
    const message = form.querySelector(".form-message");
    const submitButton = document.getElementById("account-submit");
    const passwordInput = form.elements.password;
  
    if (user) {
      setupEditMode(user, form, passwordInput, submitButton);
    }
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
  
      const body = Object.fromEntries(new FormData(form));
  
      // Düzenlemede şifre alanı boş bırakılırsa şifre değişmesin
      if (user && !body.password) {
        delete body.password;
      }
  
      submitButton.disabled = true;
      message.className = "form-message";
      message.textContent = "Kaydediliyor...";
  
      try {
        if (user) {
          const updated = await api("/api/auth/me", { method: "PUT", body });
          passwordInput.value = "";
          message.className = "form-message success";
          message.textContent = "Bilgileriniz güncellendi.";
          renderNav();  // menüdeki isim değişmiş olabilir
          Object.assign(user, updated);
        } else {
          await api("/api/auth/register", { method: "POST", body });
          // Kayıt olan kişi otomatik giriş yapmış oluyor, job board'a gönder
          window.location.href = "/";
          return;
        }
      } catch (error) {
        message.className = "form-message error";
        message.textContent = error.message;
      }
      submitButton.disabled = false;
    });
  });
  
  /** Formu "hesabı düzenle" moduna geçirir ve mevcut bilgileri doldurur. */
  function setupEditMode(user, form, passwordInput, submitButton) {
    document.title = "Hesabım · FindMyJob";
    document.getElementById("account-title").textContent = "Hesabım";
    document.getElementById("account-subtitle").textContent = "Kişisel bilgilerini güncelle.";
  
    const roleText = document.getElementById("account-role");
    roleText.hidden = false;
    roleText.textContent = `Hesap türü: ${ROLE_LABELS[user.role] || user.role}`
      + (user.company_name ? ` · ${user.company_name}` : "");
  
    form.elements.first_name.value = user.first_name;
    form.elements.last_name.value = user.last_name;
    form.elements.email.value = user.email;
    form.elements.phone.value = user.phone || "";
  
    // Şifre düzenlemede isteğe bağlı
    passwordInput.required = false;
    passwordInput.placeholder = "Değiştirmek istemiyorsan boş bırak";
    document.getElementById("password-label").textContent = "Yeni şifre (isteğe bağlı)";
  
    submitButton.textContent = "Kaydet";
    document.getElementById("account-switch").hidden = true;
  }