document.addEventListener("DOMContentLoaded", function () {
  // Toggle sidebar on mobile
  const sidebar = document.querySelector(".sidebar");
  const mainContent = document.querySelector(".main-content");

  // Simulate toggle functionality (in a real app, this would be more complex)
  document
    .querySelector(".notification-btn")
    .addEventListener("click", function () {
      alert("Notifications would appear here");
    });

  // Welcome banner action button
  document
    .querySelector(".welcome-action .btn")
    .addEventListener("click", function (e) {
      e.preventDefault();
      alert("Redirecting to property listing form...");
      // In a real app, this would navigate to the property upload page
    });

  // Card action buttons
  const cardActions = document.querySelectorAll(".card-action");
  cardActions.forEach((action) => {
    action.addEventListener("click", function (e) {
      e.preventDefault();
      const cardTitle =
        this.closest(".card").querySelector(".card-title").textContent;
      alert(`Viewing all ${cardTitle}`);
    });
  });
});
