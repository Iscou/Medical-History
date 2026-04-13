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

// Evento de Login
document.getElementById('form-login').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the page from reloading
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    // Only if the regex succeeds, do we simulate sending to the database
    if (isEmailValid(email, 'error-login-email')) {
        console.log("Datos listos para la API (Login):", { email, password });
        alert("Validación de correo exitosa. Listo para enviar al backend.");
    }
});

// Registration Event
document.getElementById('form-register').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    // Only if the regex succeeds, do we simulate sending to the database
    if (isEmailValid(email, 'error-reg-email')) {
        console.log("Datos listos para la API (Registro):", { name, email, password });
        alert("Validación de correo exitosa. Listo para guardar el médico.");
    }
});