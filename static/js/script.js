// Mobile Menu Toggle
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navMenu = document.querySelector('.nav-menu');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        mobileMenuToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close menu when clicking on a link
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
            mobileMenuToggle.classList.remove('active');
            navMenu.classList.remove('active');
        }
    });
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Active navigation link on scroll
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-menu a');

window.addEventListener('scroll', () => {
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Add scroll effect to header
const header = document.querySelector('.header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }

    lastScroll = currentScroll;
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards and announcement items
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.card, .announcement-item, .about-item, .contact-item');
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Naver Map Integration
// Map functionality removed - using static display instead

console.log('Church website loaded successfully!');

// Card Slider Functionality
document.addEventListener('DOMContentLoaded', () => {
    // Vision Slider (1 card at a time)
    const visionSlider = document.querySelector('.vision-slider');
    const visionCards = visionSlider ? visionSlider.querySelectorAll('.card') : [];
    const visionPrev = document.querySelector('.vision-prev');
    const visionNext = document.querySelector('.vision-next');
    let visionIndex = 0;

    function showVisionCard(index) {
        visionCards.forEach((card, i) => {
            card.classList.remove('active');
            if (i === index) {
                card.classList.add('active');
            }
        });
    }

    if (visionCards.length > 0) {
        showVisionCard(0);

        if (visionPrev) {
            visionPrev.addEventListener('click', () => {
                visionIndex = (visionIndex - 1 + visionCards.length) % visionCards.length;
                showVisionCard(visionIndex);
            });
        }

        if (visionNext) {
            visionNext.addEventListener('click', () => {
                visionIndex = (visionIndex + 1) % visionCards.length;
                showVisionCard(visionIndex);
            });
        }

        // Hide buttons if only one card
        if (visionCards.length === 1) {
            if (visionPrev) visionPrev.style.display = 'none';
            if (visionNext) visionNext.style.display = 'none';
        }
    }

    // Sermon Slider (2 columns at a time)
    const sermonSlider = document.querySelector('.sermon-slider');
    const sermonCards = sermonSlider ? sermonSlider.querySelectorAll('.card') : [];
    const sermonPrev = document.querySelector('.sermon-prev');
    const sermonNext = document.querySelector('.sermon-next');
    let sermonPage = 0;
    const cardsPerPage = 2;

    function showSermonPage(page) {
        const totalPages = Math.ceil(sermonCards.length / cardsPerPage);
        sermonPage = (page + totalPages) % totalPages;

        sermonCards.forEach((card, i) => {
            const pageIndex = Math.floor(i / cardsPerPage);
            if (pageIndex === sermonPage) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (sermonCards.length > 0) {
        showSermonPage(0);

        if (sermonPrev) {
            sermonPrev.addEventListener('click', () => {
                showSermonPage(sermonPage - 1);
            });
        }

        if (sermonNext) {
            sermonNext.addEventListener('click', () => {
                showSermonPage(sermonPage + 1);
            });
        }

        // Hide buttons if 2 or fewer cards
        if (sermonCards.length <= 2) {
            if (sermonPrev) sermonPrev.style.display = 'none';
            if (sermonNext) sermonNext.style.display = 'none';
        }
    }
});
