document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const profileTrigger = document.getElementById('profile-trigger');
    const profileDropdown = document.getElementById('profile-dropdown');
    const navLinks = document.querySelectorAll('.nav-link');
    const mobileBreakpoint = 768;

    // Profile Dropdown Functionality
    if (profileTrigger && profileDropdown) {
        // Toggle dropdown on click
        profileTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Close any other dropdowns if they exist
            document.querySelectorAll('.profile-dropdown:not(.hidden)').forEach(dropdown => {
                if (dropdown !== profileDropdown) {
                    dropdown.classList.add('hidden');
                }
            });

            // Toggle current dropdown
            profileDropdown.classList.toggle('hidden');

            // Add active state to trigger
            profileTrigger.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && !profileTrigger.contains(e.target)) {
                profileDropdown.classList.add('hidden');
                profileTrigger.classList.remove('active');
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !profileDropdown.classList.contains('hidden')) {
                profileDropdown.classList.add('hidden');
                profileTrigger.classList.remove('active');
            }
        });

        // Handle focus trap within dropdown when open
        profileDropdown.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const focusableElements = profileDropdown.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const firstFocusable = focusableElements[0];
                const lastFocusable = focusableElements[focusableElements.length - 1];

                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        lastFocusable.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        firstFocusable.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    // Navigation Active State
    const setActiveLink = () => {
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath || 
                (currentPath.startsWith(href) && href !== '/')) {
                link.classList.add('active');
                // Update mobile nav if it exists
                const mobileNav = document.querySelector('.mobile-nav');
                if (mobileNav) {
                    const mobileLink = mobileNav.querySelector(`[href="${href}"]`);
                    if (mobileLink) {
                        mobileLink.classList.add('active');
                    }
                }
            } else {
                link.classList.remove('active');
            }
        });
    };

    // Set initial active state
    setActiveLink();

    // Handle navigation clicks
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Only handle navigation if it's not an external link
            if (link.getAttribute('target') !== '_blank') {
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });

    // Responsive Navigation
    const handleResize = () => {
        const isMobile = window.innerWidth <= mobileBreakpoint;
        
        // Adjust dropdown position for mobile
        if (profileDropdown) {
            if (isMobile) {
                profileDropdown.style.position = 'fixed';
                profileDropdown.style.bottom = '80px'; // Above mobile nav
                profileDropdown.style.left = '1rem';
                profileDropdown.style.right = '1rem';
                profileDropdown.style.width = 'auto';
            } else {
                profileDropdown.style.position = 'absolute';
                profileDropdown.style.bottom = 'auto';
                profileDropdown.style.left = 'auto';
                profileDropdown.style.right = '0';
                profileDropdown.style.width = '320px';
            }
        }

        // Reset any mobile-specific states
        if (!isMobile) {
            setActiveLink();
        }
    };

    // Initial responsive setup
    handleResize();

    // Handle window resize with debounce
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResize, 250);
    });

    // Handle navigation state in browser history
    window.addEventListener('popstate', setActiveLink);
});

