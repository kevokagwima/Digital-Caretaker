const landlord = document.querySelector(".landlord-system");
const tenant = document.querySelector(".tenant-system");
const property = document.querySelector(".property-info");
const testimonials = document.querySelectorAll(".test");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("show", entry.isIntersecting);
      if (entry.isIntersecting) observer.unobserve(entry.target);
    });
  },
  {
    threshold: 0.3,
  }
);
observer.observe(tenant);
observer.observe(landlord);

const propobserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("show-property", entry.isIntersecting);
      if (entry.isIntersecting) propobserver.unobserve(entry.target);
    });
  },
  {
    threshold: 0.2,
  }
);
propobserver.observe(property);

const testobserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("show-test", entry.isIntersecting);
      if (entry.isIntersecting) testobserver.unobserve(entry.target);
    });
  },
  {
    threshold: 0.5,
  }
);
testimonials.forEach((test) => {
  testobserver.observe(test);
});

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

const one = document.querySelectorAll(".one");
const two = document.querySelectorAll(".two");
const dots = document.querySelectorAll(".dot");

const oneobserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("show-line", entry.isIntersecting);
      if (entry.isIntersecting) oneobserver.unobserve(entry.target);
    });
  },
  {
    threshold: 1,
  }
);
one.forEach((ones) => {
  oneobserver.observe(ones);
});
two.forEach((ones) => {
  oneobserver.observe(ones);
});
