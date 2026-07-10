// --- GLOBAL STATE ---
const appState = {
    authenticated: false,
    doctorId: null,
    doctorName: "Dr. Médico", 
    doctorEmail: "", 
    currentView: 'summary',
    patientsList: [], 
    currentPatientData: null, // Store all details for printing
    currentPatientQueries: []
};

// --- LOGIN/REGISTER TOGGLE LOGIC ---
function toggleAuthMode(mode) {
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const subtitle = document.getElementById('auth-subtitle');

    if (mode === 'register') {
        formLogin.classList.remove('active');
        formLogin.classList.add('hidden');
        formRegister.classList.remove('hidden');
        formRegister.classList.add('active');
        subtitle.innerText = "Cree una nueva cuenta de médico";
    } else {
        formRegister.classList.remove('active');
        formRegister.classList.add('hidden');
        formLogin.classList.remove('hidden');
        formLogin.classList.add('active');
        subtitle.innerText = "Bienvenido doctor, por favor inicie sesión";
    }
}

// --- OTP REQUEST LOGIC ---
async function requestOTP() {
    const email = document.getElementById('reg-email').value;
    if (!email) {
        alert("Por favor, ingrese un correo electrónico primero.");
        return;
    }

    const btn = document.getElementById('btn-send-otp');
    btn.innerText = "Enviando...";
    btn.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:8000/send_otp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email })
        });
        const data = await response.json();

        if (data.status === 'success') {
            alert(data.msg);
            document.getElementById('otp-section').classList.remove('hidden');
            btn.innerText = "Reenviar Código";
        } else {
            alert(`Error: ${data.msg}`);
            btn.innerText = "1. Solicitar Código al Correo";
        }
    } catch (error) {
        console.error("OTP Error:", error);
        alert("Error de conexión al intentar enviar el correo.");
        btn.innerText = "1. Solicitar Código al Correo";
    }
    btn.disabled = false;
}

// --- REGISTRATION WITH OTP LOGIC ---
document.getElementById('form-register').addEventListener('submit', async function(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const code = document.getElementById('reg-otp').value; // Capture the OTP code

    if (!code) {
        alert("Debe ingresar el código de verificación enviado a su correo.");
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/sign_up', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name, email, password, code })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            alert("Cuenta creada exitosamente. Ahora puede iniciar sesión.");
            toggleAuthMode('login'); 
            document.getElementById('form-register').reset();
            document.getElementById('otp-section').classList.add('hidden'); // Hide OTP section
            document.getElementById('btn-send-otp').innerText = "1. Solicitar Código al Correo";
        } else {
            alert(`Error: ${data.msg}`);
        }
    } catch (error) {
        console.error("Register fetch error:", error);
        alert("Error de conexión con el servidor.");
    }
});

// --- AUTHENTICATION & VIEWS ---
document.getElementById('form-login').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            appState.authenticated = true;
            appState.doctorId = data.doctor_id;
            appState.doctorName = data.doctor_name;
            appState.doctorEmail = email;

            document.getElementById('auth-screen').classList.add('hidden'); 
            document.getElementById('dashboard-screen').classList.remove('hidden'); 
            document.getElementById('topbar-doc-name').innerText = appState.doctorName;
            document.getElementById('welcome-message').innerText = `Bienvenido, ${appState.doctorName}`;
            
            // Load locally saved signature if it exists
            const savedSig = localStorage.getItem(`signature_${appState.doctorId}`);
            if(savedSig) {
                document.getElementById('preview-signature').src = savedSig;
                document.getElementById('preview-signature').style.display = 'block';
            }
            
            switchView('summary');
        } else {
            alert("Credenciales inválidas");
        }
    } catch (error) {
        console.error("Login fetch error:", error);
    }
});

function handleLogout() {
    location.reload(); // Cleanest way to clear state
}

function switchView(viewName) {
    appState.currentView = viewName;
    document.querySelectorAll('.content-view').forEach(v => v.classList.add('hidden'));
    document.getElementById(`view-${viewName}`).classList.remove('hidden');

    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    if(document.getElementById(`nav-${viewName}`)) document.getElementById(`nav-${viewName}`).classList.add('active');

    if (viewName === 'patients') loadPatientsListData();
    else if (viewName === 'summary') loadRecentPatients();
    else if (viewName === 'settings') {
        document.getElementById('set-name').value = appState.doctorName;
        document.getElementById('set-email').value = appState.doctorEmail;
    }
}

// --- DATA FETCHING LOGIC ---
async function loadRecentPatients() {
    if(!appState.doctorId) return;
    try {
        const response = await fetch(`http://127.0.0.1:8000/patients/recent/${appState.doctorId}`);
        const data = await response.json();
        const tbody = document.getElementById('recent-patients-body');
        tbody.innerHTML = '';
        if (data.length === 0) document.getElementById('empty-recent-msg').classList.remove('hidden');
        else {
            document.getElementById('empty-recent-msg').classList.add('hidden');
            data.forEach(p => {
                tbody.innerHTML += `<tr onclick="loadPatientDetails('${p.document_id}')" style="cursor:pointer;"><td>${p.document_id}</td><td>${p.names}</td><td>${p.surnames}</td></tr>`;
            });
        }
    } catch (error) { console.error(error); }
}

async function loadPatientsListData() {
    if(!appState.doctorId) return;
    try {
        const response = await fetch(`http://127.0.0.1:8000/patients/all/${appState.doctorId}`);
        appState.patientsList = await response.json();
        renderPatientsTable(appState.patientsList);
    } catch (error) { console.error(error); }
}

function renderPatientsTable(list) {
    const tbody = document.getElementById('patients-table-body');
    const table = document.getElementById('patients-table');
    const msg = document.getElementById('empty-patients-msg');
    
    tbody.innerHTML = '';
    if(list.length === 0) { table.classList.add('hidden'); msg.classList.remove('hidden'); }
    else {
        table.classList.remove('hidden'); msg.classList.add('hidden');
        list.forEach(p => {
            tbody.innerHTML += `<tr onclick="loadPatientDetails('${p.document_id}')" style="cursor:pointer;"><td>${p.document_id}</td><td>${p.names}</td><td>${p.surnames}</td></tr>`;
        });
    }
}

function filterPatientsTable() {
    const q = document.getElementById('patient-search-input').value.toLowerCase();
    const filtered = appState.patientsList.filter(p => `${p.names} ${p.surnames} ${p.document_id}`.toLowerCase().includes(q));
    renderPatientsTable(filtered);
}

// --- FEMALE GENDER SPECIFIC LOGIC ---
function toggleUrogenital(gender) {
    const box = document.getElementById('urogenital-container');
    if (gender === 'female') {
        box.classList.remove('hidden');
        document.getElementById('cp-int-uro').required = false; // Optional
    } else {
        box.classList.add('hidden');
        document.getElementById('cp-int-uro').value = ""; // Clear value
    }
}

// --- CREATE PATIENT WITH ALL FIELDS ---
async function handleCreatePatient(e) {
    e.preventDefault();
    const formData = new FormData();
    
    // Link history to current doctor
    formData.append("doctor_id", appState.doctorId);
    
    // Personal info
    formData.append("document_id", document.getElementById('cp-pat-cedula').value);
    formData.append("names", document.getElementById('cp-pat-names').value);
    formData.append("surnames", document.getElementById('cp-pat-surnames').value);
    formData.append("gender", document.getElementById('cp-pat-gender').value);
    formData.append("birthdate", document.getElementById('cp-pat-birthdate').value);
    formData.append("marital_status", document.getElementById('cp-pat-marital').value);
    formData.append("referred", document.getElementById('cp-pat-referred').value);
    formData.append("address", document.getElementById('cp-pat-address').value);
    formData.append("phone", document.getElementById('cp-pat-phone').value);

    // Query
    formData.append("motive", document.getElementById('cp-motive').value);
    formData.append("current_illness", document.getElementById('cp-illness').value);

    // Background
    formData.append("cardiovascular", document.getElementById('cp-int-cardio').value);
    formData.append("pulmonary", document.getElementById('cp-int-pulmonary').value);
    formData.append("neurological", document.getElementById('cp-int-neuro').value);
    formData.append("urogenital", document.getElementById('cp-int-uro').value);
    formData.append("eyes", document.getElementById('cp-int-eyes').value);
    formData.append("osteomuscular", document.getElementById('cp-int-osteo').value);
    formData.append("metabolic", document.getElementById('cp-int-meta').value);
    formData.append("allergic", document.getElementById('cp-int-allergy').value);
    formData.append("surgical", document.getElementById('cp-int-surg').value);
    formData.append("orl", document.getElementById('cp-int-orl').value);
    formData.append("habits", document.getElementById('cp-int-habits').value);
    formData.append("family_background", document.getElementById('cp-int-family').value);

    // Physical exam and Auxiliaries
    formData.append("weight", document.getElementById('cp-weight').value || 0);
    formData.append("blood_pressure", document.getElementById('cp-bp').value);
    formData.append("heart_rate", document.getElementById('cp-hr').value || 0);
    formData.append("physical_examination", document.getElementById('cp-phys-exam').value);
    formData.append("electrocardiogram", document.getElementById('cp-aux-electro').value);
    formData.append("chest_xray", document.getElementById('cp-aux-rx').value);
    formData.append("laboratory", document.getElementById('cp-aux-lab').value);

    // Diagnostics
    formData.append("diagnostic", document.getElementById('cp-diagnostic').value);
    formData.append("treatment", document.getElementById('cp-treatment').value);

    // Files
    const files = document.getElementById('cp-file').files;
    for (let i = 0; i < files.length; i++) formData.append("exam_files", files[i]);

    try {
        const response = await fetch('http://127.0.0.1:8000/patient/create', { method: 'POST', body: formData });
        const result = await response.json();
        if (result.status === 'success') {
            alert(result.msg);
            document.getElementById('form-create-patient').reset();
            switchView('patients');
        } else {
            alert(`Error: ${result.msg}`);
        }
    } catch (error) { console.error(error); }
}

// --- PATIENT DETAILS & PDF GENERATOR ---
async function loadPatientDetails(document_id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/patient/details/${document_id}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            appState.currentPatientData = data.patient;
            appState.currentPatientQueries = data.queries;

            document.getElementById('details-patient-name').innerText = `${data.patient.names} ${data.patient.surnames}`;
            document.getElementById('details-cedula').innerHTML = `<strong>Cédula:</strong> ${data.patient.document_id}`;
            document.getElementById('details-gender').innerHTML = `<strong>Sexo:</strong> ${data.patient.gender === 'male' ? 'Masculino' : 'Femenino'}`;
            document.getElementById('details-phone').innerHTML = `<strong>Teléfono:</strong> ${data.patient.phone || 'N/A'}`;
            document.getElementById('details-address').innerHTML = `<strong>Dirección:</strong> ${data.patient.address || 'N/A'}`;

            // Populate background preview
            const ant = data.patient;
            let antHtml = `
                <p><strong>Cardiovascular:</strong> ${ant.cardiovascular || '-'}</p>
                <p><strong>Pulmonar:</strong> ${ant.pulmonary || '-'}</p>
                <p><strong>Metabólico:</strong> ${ant.metabolic || '-'}</p>
                <p><strong>Quirúrgico:</strong> ${ant.surgical || '-'}</p>
                <p><strong>Hábitos:</strong> ${ant.habits || '-'}</p>
                <p><strong>Familiares:</strong> ${ant.family_background || '-'}</p>
            `;
            if(ant.gender === 'female') antHtml += `<p><strong>Urogenital:</strong> ${ant.urogenital || '-'}</p>`;
            document.getElementById('details-antecedents').innerHTML = antHtml;

            // Populate timeline and download buttons
            const timeline = document.getElementById('details-queries-timeline');
            timeline.innerHTML = '';
            
            data.queries.forEach(q => {
                const queryExams = data.exams.filter(e => e.query_id === q.id);
                let examsHtml = '';
                
                if (queryExams.length > 0) {
                    examsHtml += `<div style="margin-top: 10px;"><strong>Archivos Adjuntos:</strong><br>`;
                    queryExams.forEach(e => {
                        // Download button linked to Python endpoint
                        examsHtml += `<button type="button" class="btn-primary" style="background: #95a5a6; padding: 5px 10px; font-size: 12px; margin-right: 5px; margin-top: 5px;" onclick="window.open('http://127.0.0.1:8000/exam/download/${e.id}', '_blank')">📎 ${e.exam_name}</button>`;
                    });
                    examsHtml += `</div>`;
                }

                timeline.innerHTML += `
                    <div style="border-left: 3px solid var(--primary-color); padding-left: 15px; margin-bottom: 15px; background: #f9f9f9; padding: 10px; border-radius: 0 5px 5px 0;">
                        <span style="font-size: 12px; color: #7f8c8d;">Fecha: ${q.date}</span>
                        <h6 style="color: var(--secondary-color); margin: 5px 0 10px 0;">Motivo: ${q.motive}</h6>
                        <p style="font-size: 13px; margin-bottom: 5px;"><strong>Enfermedad Actual / Evolución:</strong><br>${q.current_illness.replace(/\n/g, '<br>')}</p>
                        <p style="font-size: 13px;"><strong>Diagnóstico:</strong> ${q.diagnostic}</p>
                        ${examsHtml}
                    </div>`;
            });
            switchView('patient-details');
        }
    } catch (error) { console.error(error); }
}

// --- MEDICAL DOCUMENT GENERATOR (Iframe solution to bypass blockers) ---
function printMedicalRecord() {
    const p = appState.currentPatientData;
    const q = appState.currentPatientQueries[0]; 
    const signatureBase64 = localStorage.getItem(`signature_${appState.doctorId}`) || "";
    const signatureHtml = signatureBase64 ? `<img src="${signatureBase64}" style="max-height: 120px; margin-top:20px;">` : `<br><br><br>`;

    const printContent = `
        <html>
        <head>
            <title>Historia Médica - ${p.names} ${p.surnames}</title>
            <style>
                /* --- CLEAN PRINT STYLES --- */
                @page {
                    size: auto;
                    margin: 20mm 15mm 20mm 15mm; /* Physical page margins */
                }
                
                html, body {
                    background-color: #fff;
                    margin: 0px;  /* Remove default browser margins */
                    padding: 0px;
                }

                /* Hide native Windows headers and footers */
                @media print {
                    thead { display: table-header-group; }
                    tfoot { display: table-footer-group; }
                    body { -webkit-print-color-adjust: exact; }
                }

                /* --- DOCUMENT LAYOUT --- */
                body { font-family: Arial, sans-serif; padding: 20px; color: #000; line-height: 1.5; font-size: 14px; }
                h2, h3 { text-align: center; color: #2c3e50; margin: 5px 0; }
                .header { border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px; }
                .section { margin-bottom: 20px; }
                .section-title { font-weight: bold; background: #eee; padding: 5px; text-transform: uppercase; margin-bottom: 10px;}
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
                .full-width { grid-column: span 2; }
                .field { margin-bottom: 5px; }
                .footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc; page-break-inside: avoid; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>${appState.doctorName.toUpperCase()}</h2>
                <h3>HISTORIA CLÍNICA GENERAL</h3>
            </div>
            <div class="section">
                <div class="section-title">Datos Personales</div>
                <div class="grid">
                    <div class="field"><strong>Nombre:</strong> ${p.names} ${p.surnames}</div>
                    <div class="field"><strong>C.I:</strong> ${p.document_id}</div>
                    <div class="field"><strong>Fecha Nac.:</strong> ${p.birthdate}</div>
                    <div class="field"><strong>Sexo:</strong> ${p.gender === 'male' ? 'Masculino' : 'Femenino'}</div>
                    <div class="field full-width"><strong>Dirección:</strong> ${p.address || ''}</div>
                    <div class="field"><strong>Teléfono:</strong> ${p.phone || ''}</div>
                </div>
            </div>
            ${q ? `
            <div class="section">
                <div class="section-title">Consulta (Fecha: ${q.date})</div>
                <div class="field"><strong>Motivo:</strong> ${q.motive}</div>
                <div class="field"><strong>Enfermedad Actual:</strong> ${q.current_illness}</div>
            </div>
            <div class="section">
                <div class="section-title">Antecedentes</div>
                <div class="grid">
                    <div class="field"><strong>Cardio:</strong> ${p.cardiovascular || '-'}</div>
                    <div class="field"><strong>Pulmonar:</strong> ${p.pulmonary || '-'}</div>
                    <div class="field full-width"><strong>Familiares:</strong> ${p.family_background || '-'}</div>
                </div>
            </div>
            <div class="section">
                <div class="section-title">Impresión Diagnóstica y Tratamiento</div>
                <div class="field"><strong>Diagnóstico:</strong> ${q.diagnostic}</div>
                <div class="field"><strong>Tratamiento:</strong> ${q.treatment || '-'}</div>
            </div>
            ` : '<p>No hay consultas registradas.</p>'}
            <div class="footer">
                ${signatureHtml}
                <br>
                <p>___________________________________</p>
                <strong>${appState.doctorName}</strong>
            </div>
        </body>
        </html>
    `;

    // Inject invisible iframe to print without native Windows warnings
    let iframe = document.getElementById('print-iframe');
    if (!iframe) {
        iframe = document.createElement('iframe');
        iframe.id = 'print-iframe';
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
    }
    
    iframe.contentWindow.document.open();
    iframe.contentWindow.document.write(printContent);
    iframe.contentWindow.document.close();
    
    setTimeout(() => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
    }, 500);
}
window.printPatientHistory = printMedicalRecord;

// --- EVOLUTIONARY QUERY LOGIC ---
function openEvolutionaryQuery() {
    document.getElementById('eq-patient-name-label').innerText = `${appState.currentPatientData.names} ${appState.currentPatientData.surnames}`;
    document.getElementById('form-add-query').reset();
    switchView('add-query');
}

async function handleEvolutionaryQuery(e) {
    e.preventDefault();
    const formData = new FormData();
    
    formData.append("patient_document_id", appState.currentPatientData.document_id);
    formData.append("motive", document.getElementById('eq-motive').value);
    formData.append("current_illness", document.getElementById('eq-illness').value);
    formData.append("diagnostic", document.getElementById('eq-diagnostic').value);
    
    // Fill hidden fields to maintain database integrity
    formData.append("treatment", "");
    formData.append("weight", 0);
    formData.append("height", 0);
    formData.append("temperature", 0);
    formData.append("blood_pressure", "");
    formData.append("heart_rate", 0);
    formData.append("respiratory_rate", 0);
    formData.append("physical_examination", "");
    formData.append("electrocardiogram", "");
    formData.append("chest_xray", "");
    formData.append("laboratory", "");

    const files = document.getElementById('eq-file').files;
    for (let i = 0; i < files.length; i++) formData.append("exam_files", files[i]);

    try {
        const response = await fetch('http://127.0.0.1:8000/query/create', { method: 'POST', body: formData });
        const result = await response.json();
        if (result.status === 'success') {
            alert(result.msg);
            loadPatientDetails(appState.currentPatientData.document_id); // Reload preview
        } else {
            alert(`Error: ${result.msg}`);
        }
    } catch (error) { console.error(error); }
}

// --- SAVE SETTINGS & SIGNATURE (Base64 Client-Side) ---
async function handleSettingsUpdate(e) {
    e.preventDefault();
    const name = document.getElementById('set-name').value;
    const email = document.getElementById('set-email').value;
    const fileInput = document.getElementById('set-signature');

    if (fileInput.files.length > 0) {
        const reader = new FileReader();
        reader.onload = function(event) {
            localStorage.setItem(`signature_${appState.doctorId}`, event.target.result);
            document.getElementById('preview-signature').src = event.target.result;
            document.getElementById('preview-signature').style.display = 'block';
        };
        reader.readAsDataURL(fileInput.files[0]);
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/doctor/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ doctor_id: appState.doctorId, name, email })
        });
        const result = await response.json();
        if (result.status === 'success') {
            appState.doctorName = name;
            document.getElementById('topbar-doc-name').innerText = name;
            alert("Perfil y firma actualizados.");
        }
    } catch (error) { console.error(error); }
}