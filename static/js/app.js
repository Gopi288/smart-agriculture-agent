/**
 * Smart Agriculture Agent - Client-Side Interactivity
 * Features:
 *  - 3-Mode Theme Switcher (Light / Dark / Glassmorphism) with localStorage
 *  - Collapsible Left Sidebar with keyboard shortcut ('[' key)
 *  - Mobile responsive drawer
 *  - Crop search & category filtering
 *  - Interactive demonstration scenario loaders
 *  - Flash alert auto-dismissal
 */

document.addEventListener("DOMContentLoaded", function () {
  console.log("[Smart Agriculture Agent] Client interface initialized.");

  // --------------------------------------------------------------------------
  // 1. Theme Management (Light / Dark / Glassmorphism)
  // --------------------------------------------------------------------------
  const themeButtons = document.querySelectorAll(".theme-btn");
  const validThemes = ["light", "dark", "glass"];

  function applyTheme(themeName) {
    if (!validThemes.includes(themeName)) {
      themeName = "light";
    }
    document.documentElement.setAttribute("data-theme", themeName);
    localStorage.setItem("saa_theme", themeName);

    themeButtons.forEach((btn) => {
      if (btn.getAttribute("data-theme-val") === themeName) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
  }

  // Bind click handlers to theme switcher buttons
  themeButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const selected = this.getAttribute("data-theme-val");
      applyTheme(selected);
    });
  });

  // Sync active button state with current applied theme
  const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
  applyTheme(currentTheme);

  // --------------------------------------------------------------------------
  // 2. Collapsible Left Sidebar Management
  // --------------------------------------------------------------------------
  const appShell = document.querySelector(".app-shell");
  const toggleButtons = document.querySelectorAll(".js-toggle-sidebar");

  function toggleSidebar() {
    if (!appShell) return;

    if (window.innerWidth <= 768) {
      appShell.classList.toggle("sidebar-mobile-open");
    } else {
      appShell.classList.toggle("sidebar-collapsed");
      const isCollapsed = appShell.classList.contains("sidebar-collapsed");
      localStorage.setItem("saa_sidebar_collapsed", isCollapsed ? "true" : "false");
    }
  }

  toggleButtons.forEach((btn) => {
    btn.addEventListener("click", toggleSidebar);
  });

  // Restore desktop collapsed state from localStorage
  if (appShell && window.innerWidth > 768) {
    const savedCollapsed = localStorage.getItem("saa_sidebar_collapsed");
    if (savedCollapsed === "true") {
      appShell.classList.add("sidebar-collapsed");
    }
  }

  // Keyboard shortcut: Press '[' to toggle sidebar
  document.addEventListener("keydown", function (e) {
    if (e.key === "[" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
      e.preventDefault();
      toggleSidebar();
    }
  });

  // Close mobile drawer when clicking outside
  document.addEventListener("click", function (e) {
    if (
      appShell &&
      appShell.classList.contains("sidebar-mobile-open") &&
      window.innerWidth <= 768
    ) {
      const sidebar = document.querySelector(".app-sidebar");
      const isToggleBtn = Array.from(toggleButtons).some((btn) => btn.contains(e.target));
      if (sidebar && !sidebar.contains(e.target) && !isToggleBtn) {
        appShell.classList.remove("sidebar-mobile-open");
      }
    }
  });

  // --------------------------------------------------------------------------
  // 3. Flash Messages Auto-Dismissal
  // --------------------------------------------------------------------------
  const flashAlerts = document.querySelectorAll(".alert");
  flashAlerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-8px)";
      setTimeout(() => alert.remove(), 500);
    }, 7000);
  });

  // --------------------------------------------------------------------------
  // 4. Crop Filter & Search System (for /crops view)
  // --------------------------------------------------------------------------
  const cropSearchInput = document.getElementById("cropSearchInput");
  const filterButtons = document.querySelectorAll(".crop-filter-btn");
  const cropCards = document.querySelectorAll(".crop-card");

  function filterCrops() {
    if (!cropCards.length) return;
    const query = cropSearchInput ? cropSearchInput.value.toLowerCase().trim() : "";
    const activeFilterBtn = document.querySelector(".crop-filter-btn.active");
    const activeCategory = activeFilterBtn ? activeFilterBtn.getAttribute("data-category") : "all";

    cropCards.forEach((card) => {
      const cropName = (card.getAttribute("data-name") || "").toLowerCase();
      const cropCategory = card.getAttribute("data-category") || "";
      const matchesQuery = !query || cropName.includes(query);
      const matchesCategory = activeCategory === "all" || cropCategory.toLowerCase() === activeCategory.toLowerCase();

      if (matchesQuery && matchesCategory) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  }

  if (cropSearchInput) {
    cropSearchInput.addEventListener("input", filterCrops);
  }

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      filterButtons.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      filterCrops();
    });
  });

  // --------------------------------------------------------------------------
  // 5. Image Upload Live Preview
  // --------------------------------------------------------------------------
  const leafImageInput = document.getElementById("leaf_image");
  const imagePreviewBox = document.getElementById("imagePreviewBox");
  const previewImg = document.getElementById("previewImg");
  const placeholderText = document.getElementById("previewPlaceholder");

  if (leafImageInput && previewImg && placeholderText) {
    leafImageInput.addEventListener("change", function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          previewImg.src = e.target.result;
          previewImg.style.display = "block";
          placeholderText.style.display = "none";
        };
        reader.readAsDataURL(file);
      }
    });
  }
});
