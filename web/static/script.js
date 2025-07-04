window.addEventListener("load", () => {
  setTimeout(() => {
    const cookies = document.cookie.split(';');
    const sp_dc = cookies.find(c => c.trim().startsWith("sp_dc="));
    if (sp_dc) {
      const value = sp_dc.split("=")[1];
      const params = new URLSearchParams(window.location.search);
      const user_id = params.get("user_id");
      if (user_id) {
        fetch("/save_spdc", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id, sp_dc: value }),
        }).then(() => {
          document.body.innerHTML = "<h3>✅ Login successful! You can return to Telegram now.</h3>";
        });
      }
    }
  }, 5000); // wait 5 sec for cookies to set
});
