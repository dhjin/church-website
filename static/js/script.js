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

// Unified Video Tabs Functionality
function switchVideoTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Find the button that was clicked and make it active
    const clickedBtn = document.querySelector(`.tab-btn[onclick="switchVideoTab('${tabId}')"]`);
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }

    // Update tab content panels
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const targetContent = document.getElementById(`tab-${tabId}`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// Handle URL parameters for direct tab linking
document.addEventListener('DOMContentLoaded', () => {
    // Check if there's a specific tab in the hash or query params
    const hash = window.location.hash;
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');

    if (hash && hash.includes('#videos')) {
        if (tabParam) {
            switchVideoTab(tabParam);
        }
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

document.addEventListener('keydown', function (e) {
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

// Horizontal Carousel Scroll Function
function scrollCarousel(button, direction) {
    // Find the closest carousel container
    const container = button.closest('.carousel-container');
    if (!container) return;

    // Find the track inside this container
    const track = container.querySelector('.carousel-track');
    if (!track) return;

    // Calculate how much to scroll based on the visible width of the track
    const scrollAmount = track.clientWidth * 0.8; // Scroll 80% of the visible container width

    // Apply the scroll
    track.scrollBy({
        left: direction * scrollAmount,
        behavior: 'smooth'
    });
}
