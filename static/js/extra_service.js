const close_modal = document.getElementById("close-modal");
const cards = document.querySelectorAll(".card");
const modal = document.querySelector(".modal");

cards.forEach((card) => {
  card.addEventListener("click", () => {
    modal.style.display = "grid";
  });
});

close_modal.addEventListener("click", () => {
  modal.style.display = "none";
});
