const fs = require('fs');
const path = './cookies.json';

function loadCookies() {
  if (!fs.existsSync(path)) return {};
  return JSON.parse(fs.readFileSync(path));
}

function saveCookies(cookies) {
  fs.writeFileSync(path, JSON.stringify(cookies, null, 2));
}

function setUserCookie(userId, spdc) {
  const cookies = loadCookies();
  cookies[userId] = spdc;
  saveCookies(cookies);
}

function getUserCookie(userId) {
  const cookies = loadCookies();
  return cookies[userId];
}

module.exports = { setUserCookie, getUserCookie };
