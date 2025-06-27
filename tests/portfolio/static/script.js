// Cosmic Portfolio JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Navigation Logic
    function initNavigation() {
        const navLinks = document.querySelectorAll('nav a');
        const currentPath = window.location.pathname;
        
        // Set active nav link based on current page
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath || 
                (currentPath === '/' && link.getAttribute('href') === '/')) {
                link.classList.add('active');
            }
        });
        
        // Add cosmic glow effect on hover
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', function() {
                this.style.textShadow = '0 0 20px rgba(138, 43, 226, 0.8)';
            });
            
            link.addEventListener('mouseleave', function() {
                if (!this.classList.contains('active')) {
                    this.style.textShadow = '';
                }
            });
        });
    }
    
    // Create Dynamic Starfield
    function createStarfield() {
        const starCount = 150;
        const starfieldContainer = document.createElement('div');
        starfieldContainer.className = 'dynamic-starfield';
        starfieldContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        `;
        
        for (let i = 0; i < starCount; i++) {
            const star = document.createElement('div');
            star.className = 'dynamic-star';
            star.style.cssText = `
                position: absolute;
                width: ${Math.random() * 3 + 1}px;
                height: ${Math.random() * 3 + 1}px;
                background: radial-gradient(circle, #fff 0%, transparent 70%);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: starTwinkle ${Math.random() * 3 + 2}s ease-in-out infinite alternate;
                opacity: ${Math.random() * 0.8 + 0.2};
            `;
            starfieldContainer.appendChild(star);
        }
        
        document.body.appendChild(starfieldContainer);
    }
    
    // Create Cosmic Particles
    function createCosmicParticles() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'cosmic-particles';
        particleContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        `;
        
        for (let i = 0; i < 8; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: radial-gradient(circle, #fff 0%, transparent 70%);
                border-radius: 50%;
                left: ${10 + i * 10}%;
                animation: float 15s linear infinite ${i * 2}s;
            `;
            particleContainer.appendChild(particle);
        }
        
        document.body.appendChild(particleContainer);
    }
    
    // Create Black Hole
    function createBlackHole() {
        const blackHole = document.createElement('div');
        blackHole.className = 'black-hole';
        blackHole.style.cssText = `
            position: fixed;
            top: 10%;
            right: 15%;
            width: 200px;
            height: 200px;
            z-index: -1;
            opacity: 0.6;
        `;
        
        document.body.appendChild(blackHole);
    }
    
    // Smooth Scrolling for Internal Links
    function initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    // Cosmic Mouse Trail Effect
    function createMouseTrail() {
        let mouseX = 0, mouseY = 0;
        const trail = [];
        const trailLength = 20;
        
        document.addEventListener('mousemove', function(e) {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        function updateTrail() {
            trail.unshift({ x: mouseX, y: mouseY });
            if (trail.length > trailLength) {
                trail.pop();
            }
            
            const existingTrails = document.querySelectorAll('.mouse-trail');
            existingTrails.forEach(t => t.remove());
            
            trail.forEach((point, index) => {
                const trailDot = document.createElement('div');
                trailDot.className = 'mouse-trail';
                trailDot.style.cssText = `
                    position: fixed;
                    left: ${point.x}px;
                    top: ${point.y}px;
                    width: ${8 - index * 0.3}px;
                    height: ${8 - index * 0.3}px;
                    background: radial-gradient(circle, rgba(138, 43, 226, ${0.8 - index * 0.04}) 0%, transparent 70%);
                    border-radius: 50%;
                    pointer-events: none;
                    z-index: 1000;
                    transform: translate(-50%, -50%);
                `;
                document.body.appendChild(trailDot);
                
                setTimeout(() => {
                    if (trailDot.parentNode) {
                        trailDot.remove();
                    }
                }, 500);
            });
            
            requestAnimationFrame(updateTrail);
        }
        
        updateTrail();
    }
    
    // Parallax Effect for Hero Section
    function initParallax() {
        const hero = document.querySelector('.hero');
        if (!hero) return;
        
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }
    
    // Typing Animation for Hero Text
    function initTypingAnimation() {
        const heroText = document.querySelector('.hero p');
        if (!heroText) return;
        
        const originalText = heroText.textContent;
        heroText.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < originalText.length) {
                heroText.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        }
        
        // Start typing animation after a delay
        setTimeout(typeWriter, 1000);
    }
    
    // Intersection Observer for Fade-in Animations
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        // Observe elements that should fade in
        const fadeElements = document.querySelectorAll('.quick-info, .project, .about-text, .skills-section, .contact-info');
        fadeElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(el);
        });
    }
    
    // Random Cosmic Glitch Effect
    function initCosmicGlitch() {
        const glitchElements = document.querySelectorAll('h1, h2, h3');
        
        setInterval(function() {
            const randomElement = glitchElements[Math.floor(Math.random() * glitchElements.length)];
            if (randomElement && Math.random() < 0.1) { // 10% chance every interval
                randomElement.style.textShadow = `
                    2px 0 #ff00de,
                    -2px 0 #00ffff,
                    0 0 20px rgba(138, 43, 226, 0.8)
                `;
                
                setTimeout(() => {
                    randomElement.style.textShadow = '';
                }, 150);
            }
        }, 3000);
    }
    
    // Cosmic Loading Screen
    function createLoadingScreen() {
        const loader = document.createElement('div');
        loader.id = 'cosmic-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="cosmic-spinner"></div>
                <p>Initializing Cosmic Interface...</p>
            </div>
        `;
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #0a0a0a 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            opacity: 1;
            transition: opacity 0.5s ease;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .loader-content {
                text-align: center;
                color: #e0e6ed;
            }
            .cosmic-spinner {
                width: 80px;
                height: 80px;
                border: 4px solid rgba(138, 43, 226, 0.3);
                border-top: 4px solid #8a2be2;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(loader);
        
        // Remove loader after page load
        window.addEventListener('load', function() {
            setTimeout(() => {
                loader.style.opacity = '0';
                setTimeout(() => {
                    if (loader.parentNode) {
                        loader.remove();
                    }
                }, 500);
            }, 1500);
        });
    }
    
    // Mobile Navigation Toggle
    function initMobileNav() {
        const nav = document.querySelector('nav');
        const navToggle = document.createElement('button');
        navToggle.className = 'nav-toggle';
        navToggle.innerHTML = '☰';
        navToggle.style.cssText = `
            display: none;
            background: transparent;
            border: 2px solid #8a2be2;
            color: #e0e6ed;
            font-size: 1.5rem;
            padding: 0.5rem;
            border-radius: 5px;
            cursor: pointer;
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
        `;
        
        nav.style.position = 'relative';
        nav.appendChild(navToggle);
        
        navToggle.addEventListener('click', function() {
            const navUl = nav.querySelector('ul');
            navUl.classList.toggle('show');
        });
        
        // Add mobile styles
        const mobileStyle = document.createElement('style');
        mobileStyle.textContent = `
            @media (max-width: 768px) {
                .nav-toggle {
                    display: block !important;
                }
                nav ul {
                    display: none;
                    flex-direction: column;
                    position: absolute;
                    top: 100%;
                    left: 0;
                    width: 100%;
                    background: linear-gradient(135deg, rgba(20, 25, 40, 0.98), rgba(40, 20, 60, 0.98));
                    backdrop-filter: blur(10px);
                    border-top: 1px solid rgba(138, 43, 226, 0.3);
                }
                nav ul.show {
                    display: flex !important;
                }
                nav li {
                    margin: 0;
                    width: 100%;
                }
                nav a {
                    display: block;
                    padding: 1rem;
                    text-align: center;
                    border-bottom: 1px solid rgba(138, 43, 226, 0.2);
                }
            }
        `;
        document.head.appendChild(mobileStyle);
    }
    
    // Add dynamic CSS animations
    function addDynamicStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes starTwinkle {
                0%, 100% { opacity: 0.3; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.2); }
            }
            @keyframes float {
                0% { 
                    transform: translateY(100vh) scale(0);
                    opacity: 0;
                }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { 
                    transform: translateY(-100px) scale(1);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize all functions
    function init() {
        createLoadingScreen();
        initNavigation();
        createStarfield();
        createCosmicParticles();
        createBlackHole();
        initSmoothScrolling();
        createMouseTrail();
        initParallax();
        initTypingAnimation();
        initScrollAnimations();
        initCosmicGlitch();
        initMobileNav();
        addDynamicStyles();
        
        // Add cosmic cursor
        document.body.style.cursor = 'none';
        const cursor = document.createElement('div');
        cursor.style.cssText = `
            position: fixed;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, rgba(138, 43, 226, 0.8) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            mix-blend-mode: difference;
        `;
        document.body.appendChild(cursor);
        
        document.addEventListener('mousemove', function(e) {
            cursor.style.left = e.clientX - 10 + 'px';
            cursor.style.top = e.clientY - 10 + 'px';
        });
        
        console.log('🌌 Cosmic Portfolio Initialized Successfully! 🚀');
    }
    
    // Run initialization
    init();
});

// Additional utility functions
window.CosmicPortfolio = {
    // Function to add cosmic glow to any element
    addCosmicGlow: function(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.addEventListener('mouseenter', function() {
                this.style.boxShadow = '0 0 30px rgba(138, 43, 226, 0.6)';
                this.style.transform = 'scale(1.05)';
            });
            el.addEventListener('mouseleave', function() {
                this.style.boxShadow = '';
                this.style.transform = 'scale(1)';
            });
        });
    },
    
    // Function to create cosmic explosion effect
    createExplosion: function(x, y) {
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                left: ${x}px;
                top: ${y}px;
                width: 4px;
                height: 4px;
                background: radial-gradient(circle, #8a2be2 0%, transparent 70%);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
            `;
            document.body.appendChild(particle);
            
            const angle = (Math.PI * 2 * i) / 20;
            const velocity = Math.random() * 100 + 50;
            let posX = x, posY = y;
            let opacity = 1;
            
            function animate() {
                posX += Math.cos(angle) * velocity * 0.02;
                posY += Math.sin(angle) * velocity * 0.02;
                opacity -= 0.02;
                
                particle.style.left = posX + 'px';
                particle.style.top = posY + 'px';
                particle.style.opacity = opacity;
                
                if (opacity > 0) {
                    requestAnimationFrame(animate);
                } else {
                    particle.remove();
                }
            }
            animate();
        }
    }
};