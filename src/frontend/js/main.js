// Regular expresion for the emails than are the users in the bd
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Function to toggle views
function toggleAuthView(view) {
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const subtitle = document.getElementById('auth-subtitle');

    if (view === 'register') {
        formLogin.classList.remove('active');
        formRegister.classList.add('active');
        subtitle.innerText = "Registro de nuevo facultativo";
    } else {
        formRegister.classList.remove('active');
        formLogin.classList.add('active');
        subtitle.innerText = "Ingrese sus credenciales para continuar";
    }
}

// Regex validator 
function isEmailValid(email, errorElementId) {
    const errorSpan = document.getElementById(errorElementId);
    if (!emailRegex.test(email)) {
        errorSpan.innerText = "Por favor, use el formato: cualquiertexto@dominio.com";
        return false;
    }
    errorSpan.innerText = ""; // We'll fix the error if everything is okay
    return true;
}

// Login Event
document.getElementById('form-login').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the page from reloading
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (isEmailValid(email, 'error-login-email')) {
        
        // We pack the data according to the Pydantic model (LoginData)
        const payload = {
            email: email,
            password: password
        };

        // We shoot the request to the FastAPI backend
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("¡Acceso concedido! " + data.msg);
                // Here you will redirect the doctor to the main dashboard later
                // window.location.href = "dashboard.html";
            } else {
                alert("Error: " + data.msg); // Shows "Invalid user or password"
            }
        })
        .catch(error => console.error('Network error:', error));
    }
});

// Registration Event
document.getElementById('form-register').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    if (isEmailValid(email, 'error-reg-email')) {
        
        // We pack the data according to the Pydantic model (RegisterData)
        const payload = {
            name: name,
            email: email,
            password: password
        };

        // We shoot the request to the FastAPI backend
        fetch('/sign_up', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.msg); // "Doctor registrado exitosamente"
                // Clear the form and send them back to the login view
                document.getElementById('form-register').reset();
                toggleAuthView('login');
            } else {
                alert("Error al registrar: " + data.msg); // E.g., email already exists
            }
        })
        .catch(error => console.error('Network error:', error));
    }
});