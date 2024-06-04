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
