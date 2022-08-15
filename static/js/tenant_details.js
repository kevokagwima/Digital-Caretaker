function openView(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
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

var acc = document.getElementsByClassName("accordion");
var i;
for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("actives");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

const revoke = document.getElementById("revoke");
const modal = document.querySelector(".modal");
const close_modal = document.querySelector(".closemodal");

revoke.addEventListener("click", () => {
  modal.style.display = "grid";
});
close_modal.addEventListener("click", () => {
  modal.style.display = "none";
});

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
