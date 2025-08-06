const closes = document.querySelectorAll("#close");

closes.forEach((p) => {
  p.addEventListener("click", () => {
    p.parentElement.style.display = "None";
  });
});

const side_nav = document.querySelector(".side-nav");
const close_side_nav = document.querySelector("#close-side-nav");
const burger = document.querySelector(".burger");

burger.addEventListener("click", () => {
  side_nav.classList.add("show-side-nav");
});

close_side_nav.addEventListener("click", () => {
  side_nav.classList.remove("show-side-nav");
});
