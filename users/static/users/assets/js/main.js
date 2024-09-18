(function() {
  "use strict";

  // Function to apply .scrolled class to the body
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader || (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top'))) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  // Sticky header
  window.onscroll = function() {
    var header = document.querySelector('.header');
    if (header) {
      if (window.scrollY > 50) {
        header.classList.add('sticky');
      } else {
        header.classList.remove('sticky');
      }
    }
  };

  // Scroll up sticky header
  let lastScrollTop = 0;
  window.addEventListener('scroll', function() {
    const selectHeader = document.querySelector('#header');
    if (!selectHeader || !selectHeader.classList.contains('scroll-up-sticky')) return;

    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop > lastScrollTop && scrollTop > selectHeader.offsetHeight) {
      selectHeader.style.setProperty('position', 'sticky', 'important');
      selectHeader.style.top = `-${selectHeader.offsetHeight + 50}px`;
    } else if (scrollTop > selectHeader.offsetHeight) {
      selectHeader.style.setProperty('position', 'sticky', 'important');
      selectHeader.style.top = "0";
    } else {
      selectHeader.style.removeProperty('top');
      selectHeader.style.removeProperty('position');
    }
    lastScrollTop = scrollTop;
  });

  // Mobile nav menu toggle
  document.querySelector('.mobile-nav-toggle').addEventListener('click', function() {
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
    if (mobileNavOverlay) {
      mobileNavOverlay.classList.toggle('active');
      this.classList.toggle('bi-list');
      this.classList.toggle('bi-x');
      document.body.classList.toggle('no-scroll');
    }
  });

  // Close mobile nav menu
  document.querySelector('.mobile-nav-close').addEventListener('click', function() {
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
    if (mobileNavOverlay) {
      mobileNavOverlay.classList.remove('active');
      const toggleButton = document.querySelector('.mobile-nav-toggle');
      if (toggleButton) {
        toggleButton.classList.remove('bi-x');
        toggleButton.classList.add('bi-list');
      }
      document.body.classList.remove('no-scroll');
    }
  });

  // Close mobile nav menu if clicking outside
  document.addEventListener('click', function(event) {
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
    const toggleButton = document.querySelector('.mobile-nav-toggle');
    if (mobileNavOverlay && mobileNavOverlay.classList.contains('active') &&
        !mobileNavOverlay.contains(event.target) &&
        !toggleButton.contains(event.target)) {
      mobileNavOverlay.classList.remove('active');
      if (toggleButton) {
        toggleButton.classList.remove('bi-x');
        toggleButton.classList.add('bi-list');
      }
      document.body.classList.remove('no-scroll');
    }
  });

  // Preloader
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  // Scroll top button
  let scrollTopButton = document.querySelector('.scroll-top');
  function toggleScrollTop() {
    if (scrollTopButton) {
      window.scrollY > 100 ? scrollTopButton.classList.add('active') : scrollTopButton.classList.remove('active');
    }
  }
  if (scrollTopButton) {
    scrollTopButton.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  // Animation on scroll function
  function aosInit() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }
  window.addEventListener('load', aosInit);

  // Auto-generate carousel indicators
  document.querySelectorAll('.carousel-indicators').forEach((carouselIndicator) => {
    carouselIndicator.closest('.carousel').querySelectorAll('.carousel-item').forEach((carouselItem, index) => {
      carouselIndicator.innerHTML += `<li data-bs-target="#${carouselIndicator.closest('.carousel').id}" data-bs-slide-to="${index}" ${index === 0 ? 'class="active"' : ''}></li>`;
    });
  });

  // Initialize Swiper sliders
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );
  
      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }
  
  window.addEventListener("load", initSwiper);

  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  // Introduce a simple error for testing
  try {
    // Intentional error: calling a non-existent function
    nonExistentFunction();
  } catch (error) {
    console.error("An error occurred: ", error);
  }

})();
