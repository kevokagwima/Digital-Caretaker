const three_dots = document.querySelectorAll(".three-dots");
const delete_bookings = document.querySelectorAll(".delete-booking");

three_dots.forEach((p) => {
  p.addEventListener("click", () => {
    p.nextElementSibling.classList.toggle("show-delete");
  });
});
