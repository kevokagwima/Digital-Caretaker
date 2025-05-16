document.addEventListener("DOMContentLoaded", function () {
  // Initialize all carousels
  document.querySelectorAll(".carousel-container").forEach((container) => {
    const carousel = container.querySelector(".carousel");
    const prevBtn = container.querySelector(".prev");
    const nextBtn = container.querySelector(".next");
    const indicators = container.querySelectorAll(".indicator");
    let currentIndex = 0;
    const items = carousel.querySelectorAll("img").length || 1;

    // Hide buttons if only one image
    if (items <= 1) {
      prevBtn.style.display = "none";
      nextBtn.style.display = "none";
      if (container.querySelector(".carousel-indicators")) {
        container.querySelector(".carousel-indicators").style.display = "none";
      }
      return;
    }

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
    // setInterval(() => {
    //     currentIndex = (currentIndex + 1) % items;
    //     updateCarousel();
    // }, 5000);
  });
});
