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

// Check if the theme toggle and icon exist before proceeding
if (themeToggle && themeIcon) {
  function getCookie(name) {
    name = encodeURIComponent(name);
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      const cookieValue = parts.pop().split(';').shift();
      return decodeURIComponent(cookieValue);
    }
    return null;
  }

  // Set the initial theme based on cookie value
  const isDarkMode = getCookie("theme") === "dark";

  // Apply theme based on preference
  function applyTheme(darkMode) {
    document.documentElement.setAttribute("data-bs-theme", darkMode ? "dark" : "light");

    // Save theme to cookies
    document.cookie = `theme=${darkMode ? "dark" : "light"}; path=/; max-age=31536000; SameSite=Strict; Secure`; // 1 year
    // Update theme icon and text
    themeIcon.className = darkMode ? "bi bi-sun-fill text-warning" : "bi bi-moon-fill text-primary";
    document.getElementById("currentThemeName").textContent = darkMode ? "Light Mode" : "Dark Mode";
  }

  applyTheme(isDarkMode);

  // Save theme to cookies and update theme when toggled
  themeToggle.addEventListener("click", function () {
    const darkMode = document.documentElement.getAttribute("data-bs-theme") !== "dark";
    applyTheme(darkMode);
  });
}

//////////////////
// Flash Messages
//////////////////

// Allow configuration of timeout duration
const FLASH_TIMEOUT = 3000;

try {
  setTimeout(function () {
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
      // Skip auto-dismiss for important messages
      if (alert.classList.contains('alert-important')) return;

      alert.classList.add("fade");
      alert.classList.remove("show");

      // Remove the element from the DOM after the transition
      setTimeout(function () {
        alert.remove();
      }, 1500);
    });
  }, FLASH_TIMEOUT);
} catch (error) {
  console.error('Error handling flash messages:', error);
}

// Add pause on hover functionality
document.querySelectorAll(".alert").forEach(alert => {
  alert.addEventListener('mouseenter', () => alert.classList.add('pause-animation'));
  alert.addEventListener('mouseleave', () => alert.classList.remove('pause-animation'));
});

////////////////
// Timezone
////////////////

document.addEventListener("DOMContentLoaded", function () {
  const detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const existingTimezone = document.cookie.split('; ').find(row => row.startsWith('timezone='));

  if (!existingTimezone || existingTimezone.split('=')[1] !== detectedTimezone) {
    document.cookie = `timezone=${detectedTimezone}; path=/; max-age=31536000`; // 1 year
    console.log("Updated timezone cookie:", detectedTimezone);
    location.reload(); // Ensure the page loads with the correct timezone
  }
});