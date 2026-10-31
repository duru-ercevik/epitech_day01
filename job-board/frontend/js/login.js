// Giriş sayfası

/** Giriş yapan kişiyi rolüne göre doğru sayfaya gönderir. */
function redirectByRole(user) {
    window.location.href = panelUrlFor(user) || "/";
  }
  
  document.addEventListener("DOMContentLoaded", async () => {
    // Zaten giriş yapılmışsa formu göstermeye gerek yok
    const user = await renderNav();
    if (user) {
      redirectByRole(user);
      return;
    }
  
    const form = document.getElementById("login-form");
    const message = form.querySelector(".form-message");
    const submitButton = form.querySelector("button[type=submit]");
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
  
      const body = Object.fromEntries(new FormData(form));
      submitButton.disabled = true;
      message.className = "form-message";
      message.textContent = "Giriş yapılıyor...";
  
      try {
        const loggedInUser = await api("/api/auth/login", { method: "POST", body });
        // Admin → admin paneli, recruiter → recruiter paneli, diğerleri → job board
        redirectByRole(loggedInUser);
      } catch (error) {
        message.className = "form-message error";
        message.textContent = error.message;
        submitButton.disabled = false;
      }
    });
  });