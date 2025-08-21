document.addEventListener("DOMContentLoaded", function () {
  // Add interactivity to cards and buttons
  const cardActions = document.querySelectorAll(".card-action");
  cardActions.forEach((action) => {
    action.addEventListener("click", function () {
      const cardTitle =
        this.closest(".card").querySelector(".card-title").textContent;
      alert(`Viewing all ${cardTitle}`);
    });
  });

  // Add button functionality
  const buttons = document.querySelectorAll(".btn");
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      if (this.classList.contains("btn-primary")) {
        alert("Opening Add Unit form...");
      } else if (this.classList.contains("btn-outline")) {
        alert("Opening Edit Property form...");
      }
    });
  });
});
