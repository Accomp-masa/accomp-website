document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    /* =========================================
       Navigation & Mobile Menu
       ========================================= */
    const navbar = document.querySelector('.navbar');
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link, .mobile-btn');

    // Scroll Navbar Effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile Menu Toggle
    let isMenuOpen = false;
    menuToggle.addEventListener('click', () => {
        isMenuOpen = !isMenuOpen;
        if (isMenuOpen) {
            mobileMenu.classList.add('active');
            menuToggle.innerHTML = '<i data-lucide="x"></i>';
        } else {
            mobileMenu.classList.remove('active');
            menuToggle.innerHTML = '<i data-lucide="menu"></i>';
        }
        lucide.createIcons();
    });

    // Close Mobile Menu on Link Click
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            isMenuOpen = false;
            mobileMenu.classList.remove('active');
            menuToggle.innerHTML = '<i data-lucide="menu"></i>';
            lucide.createIcons();
        });
    });

    /* =========================================
       Scroll Reveal Animations
       ========================================= */
    const revealElements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('appear');
                observer.unobserve(entry.target); // Reveal only once
            }
        });
    }, {
        root: null,
        rootMargin: '0px',
        threshold: 0.15 // Trigger when 15% visible
    });

    revealElements.forEach(el => revealObserver.observe(el));

    /* =========================================
       Simple Data Network Particles (Hero)
       ========================================= */
    const particlesContainer = document.getElementById('particles');

    // Create floating dots for the "network/data" feel
    if (particlesContainer) {
        const particleCount = 20;

        for (let i = 0; i < particleCount; i++) {
            const dot = document.createElement('div');

            // Random properties
            const size = Math.random() * 4 + 2; // 2px to 6px
            const posX = Math.random() * 100; // 0% to 100%
            const posY = Math.random() * 100;
            const delay = Math.random() * 5;
            const duration = Math.random() * 10 + 10; // 10s to 20s

            // Styles
            dot.style.position = 'absolute';
            dot.style.width = `${size}px`;
            dot.style.height = `${size}px`;
            dot.style.left = `${posX}%`;
            dot.style.top = `${posY}%`;
            dot.style.backgroundColor = Math.random() > 0.5 ? 'var(--accent-orange)' : 'var(--accent-gold)';
            dot.style.borderRadius = '50%';
            dot.style.opacity = Math.random() * 0.5 + 0.1;
            dot.style.boxShadow = `0 0 ${size * 2}px ${dot.style.backgroundColor}`;
            dot.style.zIndex = '0';
            dot.style.pointerEvents = 'none';
            dot.style.animation = `floatParticle ${duration}s ease-in-out ${delay}s infinite alternate`;

            particlesContainer.appendChild(dot);
        }
    }

    // Dynamic style block for particle animation
    const styleBlock = document.createElement('style');
    styleBlock.textContent = `
        @keyframes floatParticle {
            0% { transform: translate(0, 0) scale(1); opacity: 0.1; }
            50% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) scale(1.5); opacity: 0.6; }
            100% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) scale(1); opacity: 0.1; }
        }
    `;
    document.head.appendChild(styleBlock);
});
