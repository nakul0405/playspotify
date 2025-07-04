document.getElementById("login-btn").onclick = () => {
  const user_id = new URLSearchParams(window.location.search).get("user_id");
  const win = window.open("https://accounts.spotify.com/en/login", "_blank");

  document.getElementById("status").innerText = "🔄 Waiting for login...";

  setTimeout(() => checkCookie(user_id), 5000);
};

function checkCookie(user_id) {
  const cookies = document.cookie.split("; ");
  const spdc = cookies.find(c => c.startsWith("sp_dc="));
  
  if (spdc) {
    const value = spdc.split("=")[1];
    fetch("/save_spdc", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ user_id, sp_dc: value })
    }).then(() => {
      document.getElementById("status").innerText = "✅ Login successful! Return to Telegram.";
    }).catch(() => {
      document.getElementById("status").innerText = "❌ Failed to save token.";
    });
  } else {
    document.getElementById("status").innerText = "⚠️ Cookie not found. Try again.";
  }
}
