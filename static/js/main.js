document.addEventListener('DOMContentLoaded', () => {

  // --- Intro Cinematic Logic ---
  const introScreen = document.getElementById('intro-screen');
  if (introScreen) {
    if (!sessionStorage.getItem('introPlayed')) {
      // Intro 2.5s duration + buffer
      setTimeout(() => {
        introScreen.style.opacity = '0';
        setTimeout(() => {
          introScreen.remove();
          startReveals();
        }, 1000); // Wait for fade out
      }, 2500);
      sessionStorage.setItem('introPlayed', 'true');
    } else {
      introScreen.remove();
      startReveals();
    }
  } else {
    startReveals();
  }

  // --- Intersection Observer for Scroll Reveals ---
  function startReveals() {
    const revealElements = document.querySelectorAll('.reveal-up');
    
    const revealOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px"
    };

    const revealOnScroll = new IntersectionObserver(function(entries, observer) {
      entries.forEach(entry => {
        if (!entry.isIntersecting) {
          return;
        } else {
          entry.target.classList.add('active');
          observer.unobserve(entry.target);
        }
      });
    }, revealOptions);

    revealElements.forEach(el => {
      revealOnScroll.observe(el);
    });
  }

  // --- Smooth Parallax Logic ---
  const parallaxLayers = document.querySelectorAll('.parallax-layer');
  if (parallaxLayers.length > 0) {
    window.addEventListener('scroll', () => {
      let scrollY = window.scrollY;
      requestAnimationFrame(() => {
        parallaxLayers.forEach(layer => {
          const speed = layer.getAttribute('data-speed') || 0.5;
          const yPos = -(scrollY * speed);
          layer.style.transform = `translate3d(0, ${yPos}px, 0)`;
        });
      });
    });
  }

  // Contact smooth scrolling is handled by the general a[href^="#"] listener above.

});
