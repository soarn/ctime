////////////
// Tooltip
//////////
document.addEventListener('DOMContentLoaded', function () {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});


//////////////
// Dark Mode
//////////////

// Dark Mode Toggle
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

// Function to get the cookie value
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Set the initial theme based on cookie value
const isDarkMode = getCookie("theme") === "dark";

// Apply theme based on preference
function applyTheme(darkMode) {
  document.documentElement.setAttribute("data-bs-theme", darkMode ? "dark" : "light");
  themeIcon.setAttribute("data-feather", darkMode ? "sun" : "moon");
  document.getElementById("currentThemeName").textContent = darkMode ? "Light Mode" : "Dark Mode";
  feather.replace();
}

applyTheme(isDarkMode);

// Save theme to cookies and update theme when toggled
themeToggle.addEventListener("click", function () {
  const darkMode = document.documentElement.getAttribute("data-bs-theme") !== "dark";
  document.cookie = `theme=${darkMode ? "dark" : "light"}; path=/; max-age=31536000`; // 1 year
  applyTheme(darkMode);
})


//////////////////
// Flash Messages
//////////////////

// Auto dismiss flash messages after 3 seconds
setTimeout(function () {
  let alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    alert.classList.add("fade");
    alert.classList.remove("show");

    // Remove the element from the DOM after the transition
    setTimeout(function () {
      alert.remove();
    }, 1500);
  });
}, 3000);