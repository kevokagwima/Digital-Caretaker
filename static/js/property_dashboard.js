function openView(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" actives", "");
  }
  document.getElementById(cityName).style.display = "block";
}

document.getElementById("defaultOpen").click();

var dropdown = document.getElementsByClassName("dropdown-btn");
var i;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var dropdownContent = this.nextElementSibling;
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
  });
}

$(document).ready(function () {
  $("#tenant_search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#tenant_details #card").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#tenant-search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#unit_details #cards").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

const myBtn = document.getElementById("modalbtn");
const modal = document.querySelector(".modal");
const modal1 = document.querySelector(".modal1");
const close_modal = document.querySelector(".closemodal");

myBtn.addEventListener("click", () => {
  modal.style.display = "grid";
});
close_modal.addEventListener("click", () => {
  modal.style.display = "none";
});

const closes = document.querySelectorAll("#close");

closes.forEach((p) => {
  p.addEventListener("click", () => {
    p.parentElement.style.display = "none";
  });
});

const not = document.querySelector(".not");
const notifications = document.querySelector(".notifications");
const info = document.querySelectorAll("#info");

not.addEventListener("click", () => {
  notifications.classList.toggle("show-notifications");
  not_actions.forEach((q) => {
    q.classList.remove("show-not-actions");
  });
});

info.forEach((p) => {
  p.addEventListener("mouseover", () => {
    p.nextElementSibling.classList.add("show-not-actions");
  });
});

const other = document.getElementById("other");
const shifting = document.querySelector(".shifting");

other.addEventListener("click", () => {
  shifting.style.display = "flex";
});

const burger = document.querySelector(".burger");
const sidenav = document.querySelector(".side-nav");
const close = document.querySelector(".close");

burger.addEventListener("click", () => {
  sidenav.classList.add("show-side-nav");
  close.classList.add("show-close");
});

close.addEventListener("click", () => {
  sidenav.classList.remove("show-side-nav");
  close.classList.remove("show-close");
});

window.addEventListener("DOMContentLoaded", () => {
  sidenav.classList.remove("show-side-nav");
});
