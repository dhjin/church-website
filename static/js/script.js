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

    // Shorts Slider (5 cards per page on desktop, responsive on mobile)
    const shortsGrid = document.querySelector('.shorts-grid');
    const shortsCards = shortsGrid ? shortsGrid.querySelectorAll('.shorts-card') : [];
    const shortsPrev = document.querySelector('.shorts-prev');
    const shortsNext = document.querySelector('.shorts-next');
    let shortsPage = 0;

    // Calculate cards per page based on screen size
    function getShortsPerPage() {
        const width = window.innerWidth;
        if (width <= 768) return 2;      // Mobile: 2 cards
        if (width <= 1024) return 3;     // Tablet: 3 cards
        if (width <= 1200) return 4;     // Small desktop: 4 cards
        return 5;                         // Large desktop: 5 cards
    }

    function showShortsPage(page) {
        const cardsPerPage = getShortsPerPage();
        const totalPages = Math.ceil(shortsCards.length / cardsPerPage);
        shortsPage = (page + totalPages) % totalPages;

        shortsCards.forEach((card, i) => {
            const pageIndex = Math.floor(i / cardsPerPage);
            if (pageIndex === shortsPage) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (shortsCards.length > 0) {
        showShortsPage(0);

        if (shortsPrev) {
            shortsPrev.addEventListener('click', () => {
                showShortsPage(shortsPage - 1);
            });
        }

        if (shortsNext) {
            shortsNext.addEventListener('click', () => {
                showShortsPage(shortsPage + 1);
            });
        }

        // Update on window resize
        window.addEventListener('resize', () => {
            showShortsPage(shortsPage);
        });

        // Hide buttons if cards fit in one page
        const cardsPerPage = getShortsPerPage();
        if (shortsCards.length <= cardsPerPage) {
            if (shortsPrev) shortsPrev.style.display = 'none';
            if (shortsNext) shortsNext.style.display = 'none';
        }
    }

    // QT Slider (same logic as Shorts)
    const qtyGrid = document.querySelector('.qty-grid');
    const qtyCards = qtyGrid ? qtyGrid.querySelectorAll('.qty-card') : [];
    const qtyPrev = document.querySelector('.qty-prev');
    const qtyNext = document.querySelector('.qty-next');
    let qtyPage = 0;

    function showQtyPage(page) {
        const cardsPerPage = getShortsPerPage();
        const totalPages = Math.ceil(qtyCards.length / cardsPerPage);
        qtyPage = (page + totalPages) % totalPages;

        qtyCards.forEach((card, i) => {
            const pageIndex = Math.floor(i / cardsPerPage);
            card.style.display = (pageIndex === qtyPage) ? 'block' : 'none';
        });
    }

    if (qtyCards.length > 0) {
        showQtyPage(0);

        if (qtyPrev) qtyPrev.addEventListener('click', () => showQtyPage(qtyPage - 1));
        if (qtyNext) qtyNext.addEventListener('click', () => showQtyPage(qtyPage + 1));

        window.addEventListener('resize', () => showQtyPage(qtyPage));

        const cardsPerPage = getShortsPerPage();
        if (qtyCards.length <= cardsPerPage) {
            if (qtyPrev) qtyPrev.style.display = 'none';
            if (qtyNext) qtyNext.style.display = 'none';
        }
    }

    // Add touch swipe support for all sliders
    function addSwipeSupport(element, onSwipeLeft, onSwipeRight) {
        let touchStartX = 0;
        let touchEndX = 0;

        element.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        element.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50; // minimum distance for swipe
            if (touchEndX < touchStartX - swipeThreshold) {
                // Swipe left - next
                onSwipeLeft();
            }
            if (touchEndX > touchStartX + swipeThreshold) {
                // Swipe right - previous
                onSwipeRight();
            }
        }
    }

    // Apply swipe to vision slider
    if (visionSlider) {
        addSwipeSupport(visionSlider,
            () => { visionIndex = (visionIndex + 1) % visionCards.length; showVisionCard(visionIndex); },
            () => { visionIndex = (visionIndex - 1 + visionCards.length) % visionCards.length; showVisionCard(visionIndex); }
        );
    }

    // Apply swipe to sermon slider
    if (sermonSlider) {
        addSwipeSupport(sermonSlider,
            () => showSermonPage(sermonPage + 1),
            () => showSermonPage(sermonPage - 1)
        );
    }

     // Apply swipe to shorts grid
     if (shortsGrid) {
         addSwipeSupport(shortsGrid,
             () => showShortsPage(shortsPage + 1),
             () => showShortsPage(shortsPage - 1)
         );
     }
});

// YouTube Video Modal
function openVideoModal(videoId, isShorts) {
    const modal = document.getElementById('videoModal');
    const iframe = document.getElementById('videoIframe');
    const content = document.getElementById('videoModalContent');
    const container = document.getElementById('videoContainer');

    // 숏츠 모드: 세로 비율 (9:16)
    if (isShorts) {
        modal.classList.add('shorts-mode');
    } else {
        modal.classList.remove('shorts-mode');
    }

    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeVideoModal(event) {
    if (event.target.classList.contains('video-modal') ||
        event.target.classList.contains('video-modal-close')) {
        const modal = document.getElementById('videoModal');
        const iframe = document.getElementById('videoIframe');
        iframe.src = '';
        modal.classList.remove('active');
        modal.classList.remove('shorts-mode');
        document.body.style.overflow = '';
    }
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('videoModal');
        if (modal.classList.contains('active')) {
            const iframe = document.getElementById('videoIframe');
            iframe.src = '';
            modal.classList.remove('active');
            modal.classList.remove('shorts-mode');
            document.body.style.overflow = '';
        }
    }
});
