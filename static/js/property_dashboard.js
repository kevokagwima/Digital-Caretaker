const closes = document.querySelectorAll("#close");

closes.forEach((p) => {
  p.addEventListener("click", () => {
    p.parentElement.style.display = "none";
  });
});

const other = document.getElementById("other");
const shifting = document.querySelector(".shifting");

other.addEventListener("click", () => {
  shifting.style.display = "flex";
});
