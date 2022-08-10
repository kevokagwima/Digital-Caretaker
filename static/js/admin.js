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

const accord = document.querySelectorAll(".accordion");

accord.forEach((data) => {
  data.addEventListener("click", () => {
    data.classList.toggle("accordion-active");
    data.nextElementSibling.classList.toggle("close-panel");
  });
});

var acc = document.getElementsByClassName("accordions");
var i;
for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

$(document).ready(function () {
  $("#tenant-search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#table .accordion").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#search-unit").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#table .accordion").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#landlord-search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#table .accordion").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#property-search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#table .accordion").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

const closes = document.querySelectorAll("#close");

closes.forEach((p) => {
  p.addEventListener("click", () => {
    p.parentElement.style.display = "none";
  });
});

const extra_btn = document.querySelector("#extras");
const extra_modal = document.querySelector(".extra-modal");
const close_extra = document.querySelector("#closes");

extra_btn.addEventListener("click", () => {
  extra_modal.style.display = "grid";
});

close_extra.addEventListener("click", () => {
  extra_modal.style.display = "none";
});
