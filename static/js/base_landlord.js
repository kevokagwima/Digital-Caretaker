document.addEventListener("DOMContentLoaded", function () {
  // Toggle sidebar
  const sidebarToggle = document.getElementById("sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function (e) {
      e.preventDefault();
      document.body.classList.toggle("sb-sidenav-toggled");
      localStorage.setItem(
        "sb|sidebar-toggle",
        document.body.classList.contains("sb-sidenav-toggled")
      );
    });
  }

  // Check localStorage for sidebar state
  if (localStorage.getItem("sb|sidebar-toggle") === "true") {
    document.body.classList.add("sb-sidenav-toggled");
  }

  // Close flash messages when clicked
  document.querySelectorAll(".alert-flash .btn-close").forEach((button) => {
    button.addEventListener("click", function () {
      this.closest(".alert-flash").style.display = "none";
    });
  });

  // Auto-close flash messages after 5 seconds
  setTimeout(() => {
    document.querySelectorAll(".alert-flash").forEach((alert) => {
      alert.style.display = "none";
    });
  }, 5000);
});

// Function to show a toast notification
function showToast(type, message) {
  const toastContainer = document.getElementById("toast-container");
  if (!toastContainer) return;

  const toast = document.createElement("div");
  toast.className = `alert alert-${type} alert-dismissible fade show alert-flash`;
  toast.role = "alert";
  toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 5000);
}
