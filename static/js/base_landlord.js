const alertMessages = document.querySelectorAll(".alert");
alertMessages.forEach((alertMessage) => {
  const closeAlertBtn = alertMessage.lastElementChild;
  closeAlertBtn.addEventListener("click", () => {
    alertMessage.style.display = "none";
  });
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

function openView(event, tabName) {
  const tabContents = document.querySelectorAll(".tabcontent");
  tabContents.forEach((content) => {
    content.classList.remove("active");
  });

  // Remove active class from all buttons
  const tabButtons = document.querySelectorAll(".tablinks");
  tabButtons.forEach((button) => {
    button.classList.remove("active");
  });

  // Show the selected tab content and add active class to the button
  document.getElementById(tabName).classList.add("active");
  event.currentTarget.classList.add("active");
}

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
