document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const authForms = document.getElementById('auth-forms');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const userInfo = document.getElementById('user-info');
    const complaintsList = document.getElementById('complaints-list');

    let isLoggedIn = false;

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    voiceBtn.addEventListener('click', startVoiceRecognition);
    loginBtn.addEventListener('click', showLoginForm);
    registerBtn.addEventListener('click', showRegisterForm);
    logoutBtn.addEventListener('click', logout);
    loginForm.addEventListener('submit', login);
    registerForm.addEventListener('submit', register);

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessageToChat('user', message);
            userInput.value = '';
            if (isLoggedIn) {
                processIncident(message);
            } else {
                addMessageToChat('bot', 'Please log in to submit a complaint.');
            }
        }
    }

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function startVoiceRecognition() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
            };

            recognition.start();
        } else {
            alert('Speech recognition is not supported in your browser.');
        }
    }

    function showLoginForm() {
        authForms.style.display = 'block';
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    }

    function showRegisterForm() {
        authForms.style.display = 'block';
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }

    function login(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                isLoggedIn = true;
                updateUIAfterLogin();
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while logging in.');
        });
    }

    function register(e) {
        e.preventDefault();
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const contact = document.getElementById('register-contact').value;
        const address = document.getElementById('register-address').value;

        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password, contact, address }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                isLoggedIn = true;
                updateUIAfterLogin();
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while registering.');
        });
    }

    function logout() {
        fetch('/logout')
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                isLoggedIn = false;
                updateUIAfterLogout();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while logging out.');
        });
    }

    function updateUIAfterLogin() {
        authForms.style.display = 'none';
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
        userInfo.style.display = 'block';
        fetchUserInfo();
        fetchUserComplaints();
    }

    function updateUIAfterLogout() {
        authForms.style.display = 'none';
        loginBtn.style.display = 'inline-block';
        registerBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
        userInfo.style.display = 'none';
        complaintsList.innerHTML = '';
    }

    function fetchUserInfo() {
        fetch('/user_info')
        .then(response => response.json())
        .then(data => {
            document.getElementById('user-name').textContent = data.name;
            document.getElementById('user-email').textContent = data.email;
            document.getElementById('user-contact').textContent = data.contact;
            document.getElementById('user-address').textContent = data.address;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching user information.');
        });
    }

    function fetchUserComplaints() {
        fetch('/user_complaints')
        .then(response => response.json())
        .then(complaints => {
            complaintsList.innerHTML = '';
            complaints.forEach(complaint => {
                const li = document.createElement('li');
                li.textContent = `Complaint on ${new Date(complaint.date).toLocaleString()}: ${complaint.description.substring(0, 50)}...`;
                complaintsList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching user complaints.');
        });
    }

    function processIncident(description) {
        fetch('/process_incident', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        })
        .then(response => response.json())
        .then(data => {
            addMessageToChat('bot', data.response);
            fetchUserComplaints();
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('bot', 'Sorry, there was an error processing your request.');
        });
    }
});