document.addEventListener('DOMContentLoaded', () => {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const authForms = document.querySelectorAll('.auth-form');
    const loginForm = document.getElementById('login');
    const registerForm = document.getElementById('register');

    // Toggle between login and register forms
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const formName = btn.getAttribute('data-form');
            
            // Update toggle buttons
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update forms
            authForms.forEach(form => {
                form.classList.remove('active');
                if (form.id === `${formName}-form`) {
                    setTimeout(() => {
                        form.classList.add('active');
                    }, 50);
                }
            });
        });
    });

    // Login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Login successful', 'success');
                window.location.href = '/dashboard';
            } else {
                showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while logging in.', 'error');
        }
    });

    // Register form submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        
        try {
            const response = await fetch('/register', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Registration successful', 'success');
                window.location.href = '/dashboard';
            } else {
                showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while registering.', 'error');
        }
    });

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});

