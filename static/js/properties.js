const head = document.querySelector(".nav");
const links = document.querySelectorAll("#links");
const logo = document.querySelector("#logo");
const logos = document.querySelector(".logo");
const logo_white = document.querySelector("#logos");
const login = document.getElementById("login");

window.addEventListener("scroll", () => {
  const scroll_height = window.pageYOffset;
  if (scroll_height > 10) {
    head.classList.add("nav-actives");
    head.style.backgroundColor = "white";
    links.forEach((link) => {
      link.style.color = "black";
    });
    logo_white.style.display = "none";
    logo.style.display = "flex";
    logos.classList.add("logo-fixed");
    login.style.color = "black";
  } else {
    head.classList.remove("nav-actives");
    head.style.backgroundColor = "transparent";
    links.forEach((link) => {
      link.style.color = "white";
    });
    logo_white.style.display = "block";
    logo.style.display = "none";
    logos.classList.remove("logo-fixed");
    login.style.color = "white";
  }
});

$(document).ready(function () {
  $("#property-search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $(".all-units #units").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

const normal_search = document.getElementById("form1");
const live_search = document.getElementById("form2");
const live = document.querySelector("#live");
const lives = document.querySelector("#lives");

live.addEventListener("click", () => {
  normal_search.style.display = "None";
  live_search.style.display = "Block";
  live.style.display = "None";
  lives.style.display = "block";
});

lives.addEventListener("click", () => {
  normal_search.style.display = "Block";
  live_search.style.display = "None";
  live.style.display = "Block";
  lives.style.display = "None";
});

const profile = document.querySelector(".profile");
const user = document.querySelector(".login");

window.addEventListener("scroll", () => {
  profile.classList.remove("show-profile");
});
user.addEventListener("click", () => {
  profile.classList.toggle("show-profile");
});
