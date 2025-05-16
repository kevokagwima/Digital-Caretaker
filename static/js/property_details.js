document.addEventListener("DOMContentLoaded", function () {
  // Initialize main property carousel
  const carouselContainer = document.querySelector(
    ".main-carousel .carousel-container"
  );
  if (carouselContainer) {
    const carousel = carouselContainer.querySelector(".carousel");
    const prevBtn = carouselContainer.querySelector(".prev");
    const nextBtn = carouselContainer.querySelector(".next");
    const indicators = carouselContainer.querySelectorAll(".indicator");
    let currentIndex = 0;
    const items = carousel.querySelectorAll("img").length;

    function updateCarousel() {
      carousel.style.transform = `translateX(-${currentIndex * 100}%)`;

      // Update indicators
      indicators.forEach((indicator, index) => {
        if (index === currentIndex) {
          indicator.classList.add("active");
        } else {
          indicator.classList.remove("active");
        }
      });
    }

    // Next button click
    nextBtn.addEventListener("click", () => {
      currentIndex = (currentIndex + 1) % items;
      updateCarousel();
    });

    // Previous button click
    prevBtn.addEventListener("click", () => {
      currentIndex = (currentIndex - 1 + items) % items;
      updateCarousel();
    });

    // Indicator clicks
    indicators.forEach((indicator, index) => {
      indicator.addEventListener("click", () => {
        currentIndex = index;
        updateCarousel();
      });
    });

    // Auto-rotate (optional)
    // const autoRotate = setInterval(() => {
    //     currentIndex = (currentIndex + 1) % items;
    //     updateCarousel();
    // }, 5000);

    // Pause on hover
    // carouselContainer.addEventListener('mouseenter', () => {
    //     clearInterval(autoRotate);
    // });

    // carouselContainer.addEventListener('mouseleave', () => {
    //     autoRotate = setInterval(() => {
    //         currentIndex = (currentIndex + 1) % items;
    //         updateCarousel();
    //     }, 5000);
    // });
  }

  // Form submission handling
  const enquiryForm = document.getElementById("enquiryForm");
  if (enquiryForm) {
    enquiryForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Get form values
      const formData = new FormData(enquiryForm);
      const data = Object.fromEntries(formData);

      // Here you would typically send the data to a server
      console.log("Form submitted:", data);

      // Show success message
      alert("Thank you for your enquiry! We will contact you shortly.");

      // Reset form
      enquiryForm.reset();
    });
  }

  // Set minimum date for viewing date to today
  const dateInput = document.getElementById("date");
  if (dateInput) {
    const today = new Date().toISOString().split("T")[0];
    dateInput.min = today;
  }
});
