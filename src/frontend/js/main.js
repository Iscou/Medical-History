/*cite: main.js*/
// Retained original comment structure intact.
// Handles view switching and API communication for both auth and dashboard SPA flow.

// --- SPA STATE MANAGEMENT ---
const appState = {
    authenticated: false,
    doctorId: null,
    doctorName: "Dr. Médico", 
    doctorEmail: "", // NEW: Store email to pre-fill settings
    currentView: 'summary',
    patientsList: [], 
    currentPatientDoc: null, 
    currentPatientName: null
};

// --- AUTHENTICATION FLOW ---
/*cite: main.js*/
function toggleAuthView(view) {
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const subtitle = document.getElementById('auth-subtitle');

    // NEW: Clear inputs and error messages when switching auth views
    formLogin.reset();
    formRegister.reset();
    document.getElementById('error-login-email').innerText = '';
    document.getElementById('error-reg-email').innerText = '';

    if (view === 'login') {
        formLogin.classList.add('active');
        formRegister.classList.remove('active');
        subtitle.innerText = "Bienvenido doctor, por favor inicie sesión"; 
    } else {
        formLogin.classList.remove('active');
        formRegister.classList.add('active');
        subtitle.innerText = "Complete los detalles para crear su cuenta médica"; 
    }
}

function handleLoginSuccess(doctorData, email) {
    appState.authenticated = true;
    appState.doctorId = doctorData.doctor_id;
    appState.doctorName = doctorData.doctor_name; // NEW: Populated from DB response
    appState.doctorEmail = email;

    document.getElementById('auth-screen').classList.add('hidden'); 
    document.getElementById('dashboard-screen').classList.remove('hidden'); 

    document.getElementById('topbar-doc-name').innerText = appState.doctorName;
    document.getElementById('welcome-message').innerText = `Bienvenido, ${appState.doctorName}`;
    
    switchView('summary');
}

function handleLogout() {
    appState.authenticated = false;
    appState.doctorId = null;
    appState.currentView = 'summary';
    appState.patientsList = [];
    appState.currentPatientDoc = null;

    document.getElementById('dashboard-screen').classList.add('hidden');
    document.getElementById('auth-screen').classList.remove('hidden');
    toggleAuthView('login');
}

// --- SPA VIEW SWAPPING LOGIC ---
function switchView(viewName) {
    appState.currentView = viewName;

    const views = document.querySelectorAll('.content-view');
    views.forEach(view => view.classList.add('hidden'));

    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
        targetView.classList.remove('hidden');
    }

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));

    const targetNav = document.getElementById(`nav-${viewName}`);
    if (targetNav) {
        targetNav.classList.add('active');
    }

    // View specific hooks
    if (viewName === 'patients') {
        loadPatientsListData();
    } else if (viewName === 'summary') {
        loadRecentPatients(); // NEW: Load 5 recent patients
    } else if (viewName === 'settings') {
        // Pre-fill settings form
        document.getElementById('set-name').value = appState.doctorName;
        document.getElementById('set-email').value = appState.doctorEmail;
        document.getElementById('set-password').value = "";
    }
}

// --- DASHBOARD SUMMARY LOGIC (NEW) ---
async function loadRecentPatients() {
    try {
        const response = await fetch('http://127.0.0.1:8000/patients/recent');
        const recentPatients = await response.json();
        
        const tbody = document.getElementById('recent-patients-body');
        const emptyMsg = document.getElementById('empty-recent-msg');
        
        tbody.innerHTML = '';
        
        if (recentPatients.length === 0) {
            emptyMsg.classList.remove('hidden');
        } else {
            emptyMsg.classList.add('hidden');
            recentPatients.forEach(p => {
                const row = `<tr onclick="loadPatientDetailsFlow('${p.document_id}')" style="cursor: pointer;">
                    <td>${p.document_id}</td>
                    <td>${p.names}</td>
                    <td>${p.surnames}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        }
    } catch (error) {
        console.error("Error loading recent patients:", error);
    }
}

// --- SETTINGS LOGIC (NEW) ---
async function handleSettingsUpdate(event) {
    event.preventDefault();
    const newName = document.getElementById('set-name').value;
    const newEmail = document.getElementById('set-email').value;
    const newPassword = document.getElementById('set-password').value;

    const payload = {
        doctor_id: appState.doctorId,
        name: newName,
        email: newEmail,
        password: newPassword
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/doctor/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            alert(result.msg);
            appState.doctorName = newName;
            appState.doctorEmail = newEmail;
            document.getElementById('topbar-doc-name').innerText = appState.doctorName;
            document.getElementById('welcome-message').innerText = `Bienvenido, ${appState.doctorName}`;
        } else {
            alert(`Error: ${result.msg}`);
        }
    } catch (error) {
        console.error("Error updating settings:", error);
    }
}

// --- PATIENT LIST LOGIC ---
async function loadPatientsListData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/patients/all');
        const patients = await response.json();
        appState.patientsList = patients;
        renderPatientsTable(patients);
    } catch (error) {
        console.error("Critical error loading patients list:", error);
    }
}

function renderPatientsTable(patientsArray, isFiltering = false) {
    const table = document.getElementById('patients-table');
    const tbody = document.getElementById('patients-table-body');
    const emptyMsg = document.getElementById('empty-patients-msg');
    const searchInput = document.getElementById('patient-search-input');

    if (patientsArray.length === 0 && !isFiltering) {
        table.classList.add('hidden');
        emptyMsg.classList.remove('hidden');
        searchInput.disabled = true;
    } else {
        table.classList.remove('hidden');
        emptyMsg.classList.add('hidden');
        searchInput.disabled = false; 
        if (!isFiltering) searchInput.value = '';

        tbody.innerHTML = ''; 

        patientsArray.forEach(p => {
            const row = `<tr onclick="loadPatientDetailsFlow('${p.document_id}')">
                <td>${p.document_id}</td>
                <td>${p.names}</td>
                <td>${p.surnames}</td>
            </tr>`;
            tbody.innerHTML += row;
        });
    }
}

function filterPatientsTable() {
    const query = document.getElementById('patient-search-input').value.toLowerCase();
    const filtered = appState.patientsList.filter(p => {
        const fullName = `${p.names} ${p.surnames}`.toLowerCase();
        const cedula = p.document_id.toLowerCase();
        return fullName.includes(query) || cedula.includes(query);
    });
    renderPatientsTable(filtered, true); 
}

// --- FORM HANDLING (INITIAL HISTORY CREATION) ---
async function handleCreatePatient(event) {
    event.preventDefault(); 
    
    const physicalExamDict = {
        general_impression: document.getElementById('cp-phys-general').value,
        head: document.getElementById('cp-phys-head').value,
        chest: document.getElementById('cp-phys-chest').value,
        abdomen: document.getElementById('cp-phys-abdomen').value
    };

    const formData = new FormData();
    
    formData.append("document_id", document.getElementById('cp-pat-cedula').value);
    formData.append("birthdate", document.getElementById('cp-pat-birthdate').value);
    formData.append("names", document.getElementById('cp-pat-names').value);
    formData.append("surnames", document.getElementById('cp-pat-surnames').value);
    formData.append("gender", document.getElementById('cp-pat-gender').value);
    formData.append("marital_status", document.getElementById('cp-pat-marital').value);
    formData.append("occupation", "No especificado");
    formData.append("allergic", document.getElementById('cp-back-allergic').value);
    formData.append("cardiovascular", document.getElementById('cp-back-cardio').value);
    formData.append("personal_background", document.getElementById('cp-back-personal').value);
    
    formData.append("motive", document.getElementById('cp-query-motive').value);
    formData.append("diagnostic", document.getElementById('cp-query-diagnostic').value);
    formData.append("current_illness", document.getElementById('cp-query-illness').value);
    
    formData.append("weight", document.getElementById('cp-weight').value || 0);
    formData.append("height", document.getElementById('cp-height').value || 0);
    formData.append("temperature", document.getElementById('cp-temp').value || 0);
    formData.append("blood_pressure", document.getElementById('cp-bp').value);
    formData.append("heart_rate", document.getElementById('cp-hr').value || 0);
    formData.append("respiratory_rate", document.getElementById('cp-rr').value || 0);
    
    formData.append("physical_examination", JSON.stringify(physicalExamDict));

    const fileInput = document.getElementById('cp-file');
    if (fileInput.files.length > 0) {
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append("exam_files", fileInput.files[i]); 
        }
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/patient/create', {
            method: 'POST',
            body: formData 
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            alert("¡Éxito! " + result.msg); 
            document.getElementById('form-create-patient').reset(); 
            switchView('patients'); 
        } else {
            const errorMsg = result.msg || JSON.stringify(result.detail) || "Error desconocido";
            alert(`Error al crear la historia: ${errorMsg}`);
        }
    } catch (error) {
        console.error("Critical error during patient history creation fetch:", error);
    }
}

// --- PATIENT DETAILS & TIMELINE ---
async function loadPatientDetailsFlow(document_id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/patient/details/${document_id}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            appState.currentPatientDoc = data.patient.document_id;
            appState.currentPatientName = `${data.patient.names} ${data.patient.surnames}`;
            
            document.getElementById('details-patient-name').innerText = appState.currentPatientName;
            document.getElementById('details-cedula').innerHTML = `<strong>Cédula:</strong> ${data.patient.document_id}`;
            document.getElementById('details-birthdate').innerHTML = `<strong>Nacimiento:</strong> ${data.patient.birthdate}`;
            document.getElementById('details-gender').innerHTML = `<strong>Género:</strong> ${data.patient.gender}`;
            document.getElementById('details-allergies').innerHTML = `Alergias: ${data.patient.allergic || 'Ninguna registrada'}`;

            document.getElementById('eq-patient-name-label').innerText = appState.currentPatientName;

            const timeline = document.getElementById('details-queries-timeline');
            timeline.innerHTML = ''; 

            if (data.queries.length === 0) {
                timeline.innerHTML = '<p style="color: #7f8c8d; font-size: 14px;">No hay consultas previas.</p>';
            } else {
                data.queries.forEach(q => {
                    const attachedExams = data.exams.filter(e => e.query_id === q.id);
                    let examHtml = '';
                    
                    if (attachedExams.length > 0) {
                        attachedExams.forEach(exam => {
                            examHtml += `<p style="font-size: 13px; color: #2980b9; margin-top: 5px;">📎 Archivo: ${exam.exam_name}</p>`;
                        });
                    }

                    const card = `
                        <div style="border-left: 3px solid var(--primary-color); padding-left: 15px; margin-bottom: 10px; background: #f9f9f9; padding: 10px; border-radius: 0 5px 5px 0;">
                            <span style="font-size: 12px; color: #7f8c8d;">Fecha: ${q.date}</span>
                            <h6 style="margin: 5px 0; color: var(--secondary-color); font-size: 15px;">Motivo: ${q.motive}</h6>
                            <p style="font-size: 13px; color: #333;"><strong>Diagnóstico:</strong> ${q.diagnostic}</p>
                            ${examHtml}
                        </div>
                    `;
                    timeline.innerHTML += card;
                });
            }
            
            switchView('patient-details');
        } else {
            alert("Error cargando detalles del paciente");
        }
    } catch (error) {
        console.error("Error loading details:", error);
    }
}

// --- CREATE EVOLUTIONARY QUERY ---
async function handleAddEvolutionaryQuery(event) {
    event.preventDefault();

    const physicalExamDict = {
        general_impression: document.getElementById('eq-phys-general').value,
        head: document.getElementById('eq-phys-head').value,
        chest: document.getElementById('eq-phys-chest').value,
        abdomen: document.getElementById('eq-phys-abdomen').value
    };

    const formData = new FormData();
    
    formData.append("patient_document_id", appState.currentPatientDoc);
    formData.append("motive", document.getElementById('eq-motive').value);
    formData.append("current_illness", document.getElementById('eq-illness').value);
    formData.append("diagnostic", document.getElementById('eq-diagnostic').value);
    formData.append("treatment", document.getElementById('eq-treatment').value);
    
    formData.append("weight", document.getElementById('eq-weight').value || 0);
    formData.append("height", document.getElementById('eq-height').value || 0);
    formData.append("temperature", document.getElementById('eq-temp').value || 0);
    formData.append("blood_pressure", document.getElementById('eq-bp').value);
    formData.append("heart_rate", document.getElementById('eq-hr').value || 0);
    formData.append("respiratory_rate", document.getElementById('eq-rr').value || 0);
    
    formData.append("physical_examination", JSON.stringify(physicalExamDict));

    const fileInput = document.getElementById('eq-file');
    if (fileInput.files.length > 0) {
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append("exam_files", fileInput.files[i]); 
        }
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/query/create', {
            method: 'POST',
            body: formData 
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert(result.msg);
            document.getElementById('form-add-query').reset();
            loadPatientDetailsFlow(appState.currentPatientDoc);
        } else {
            alert(`Error: ${result.msg}`);
        }
    } catch (error) {
        console.error("Error creating evolutionary query:", error);
    }
}

// --- ORIGINAL AUTHENTICATION LOGIC ---

/*cite: main.js*/
document.getElementById('form-login').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    document.getElementById('error-login-email').innerText = '';

    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            // PASS THE EMAIL SO WE CAN USE IT IN SETTINGS PRE-FILL
            handleLoginSuccess(data, email);
        } else {
            document.getElementById('error-login-email').innerText = data.msg === "Invalid credentials" ? "Credenciales inválidas" : data.msg;
        }
    } catch (error) {
        console.error("Login fetch error:", error);
    }
});

/*cite: main.js*/
document.getElementById('form-register').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const name = document.getElementById('reg-name').value;

    document.getElementById('error-reg-email').innerText = '';

    try {
        const response = await fetch('http://127.0.0.1:8000/sign_up', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name, email, password }) 
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            alert("Registro exitoso. Por favor inicie sesión."); 
            toggleAuthView('login');
        } else {
            document.getElementById('error-reg-email').innerText = data.msg === "Email already registered" ? "El correo ya está registrado" : data.msg;
        }
    } catch (error) {
        console.error("Register fetch error:", error);
    }
});