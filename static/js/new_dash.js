var acc = document.getElementsByClassName("accordion");
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
const close_modal = document.querySelector(".closemodal");

myBtn.addEventListener("click", () => {
  modal.style.display = "grid";
});
close_modal.addEventListener("click", () => {
  modal.style.display = "none";
});
