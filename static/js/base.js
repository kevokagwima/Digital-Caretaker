const tops = document.querySelector(".nav");
const logo = document.querySelector(".logo");

window.addEventListener("scroll", () => {
  const scroll_height = window.pageYOffset;
  if (scroll_height > 10) {
    tops.classList.add("nav-active");
    logo.classList.add("logo-fixed");
  } else {
    tops.classList.remove("nav-active");
    logo.classList.remove("logo-fixed");
  }
});

const closes = document.querySelectorAll("#close");

closes.forEach((p) => {
  p.addEventListener("click", () => {
    p.parentElement.style.display = "None";
  });
});

var date = new Date();
document.getElementById("date").innerHTML = date.getFullYear();

const profile = document.querySelector(".profile");
const user = document.querySelector(".login");

window.addEventListener("scroll", () => {
  profile.classList.remove("show-profile");
});

user.addEventListener("click", () => {
  profile.classList.toggle("show-profile");
});

function myFunction() {
  document.getElementById("myDropdown").classList.toggle("show");
}

window.onclick = function (event) {
  if (!event.target.matches(".dropbtn")) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains("show")) {
        openDropdown.classList.remove("show");
      }
    }
  }
};

$(".texts").scrollTop($(".texts")[0].scrollHeight);
