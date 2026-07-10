const apiFetch = async (url, options = {}) => {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = body.message || body.error || response.statusText || 'An error occurred.';
    throw new Error(message);
  }
  return body;
};

const showAlert = (container, type, message) => {
  if (!container) return;
  container.innerHTML = `<div class="alert alert-${type} rounded-4 shadow-sm">${message}</div>`;
};

const clearAlert = (container) => {
  if (!container) return;
  container.innerHTML = '';
};

const formatDateTime = (value) => {
  try {
    const date = new Date(value);
    return date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
  } catch {
    return value || '-';
  }
};

const renderStatusBadge = (status) => {
  const map = {
    approved: 'success',
    pending: 'warning',
    rejected: 'danger',
    cancelled: 'secondary',
    open: 'danger',
  };
  const variant = map[status?.toLowerCase()] || 'primary';
  return `<span class="badge bg-${variant} text-uppercase">${status || 'Unknown'}</span>`;
};

const renderPriorityBadge = (priority) => {
  const map = {
    urgent: 'danger',
    normal: 'primary',
    medium: 'warning',
  };
  const variant = map[priority?.toLowerCase()] || 'secondary';
  return `<span class="badge bg-${variant}">${priority || 'Normal'}</span>`;
};

const renderBedStatus = (status) => {
  const map = {
    available: 'success',
    occupied: 'danger',
    reserved: 'warning',
    cleaning: 'secondary',
    maintenance: 'dark',
  };
  const variant = map[status?.toLowerCase()] || 'primary';
  return `<span class="badge bg-${variant}">${status || 'Unknown'}</span>`;
};

const whenExists = (id, callback) => {
  const node = document.getElementById(id);
  if (node) callback(node);
};

const addTextRow = (row, label, value) => {
  const cell = document.createElement('td');
  cell.innerHTML = value || '-';
  row.appendChild(cell);
};

const setupAppointmentsPage = () => {
  const alertContainer = document.getElementById('appointmentsAlert');
  const loading = document.getElementById('appointmentsLoading');
  const tableWrapper = document.getElementById('appointmentsTableWrapper');
  const tableBody = document.getElementById('appointmentsTable');
  const doctorSelect = document.getElementById('doctorSelect');
  const departmentSelect = document.getElementById('departmentSelect');
  const form = document.getElementById('appointmentForm');

  const loadAppointments = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      const appointments = await apiFetch('/api/appointments');
      tableBody.innerHTML = appointments.map((appointment) => `
        <tr>
          <td>${appointment.patient || 'You'}</td>
          <td>${appointment.doctor || '-'}</td>
          <td>${appointment.department || '-'}</td>
          <td>${formatDateTime(appointment.date)}</td>
          <td>${renderStatusBadge(appointment.status)}</td>
          <td>${renderPriorityBadge(appointment.priority)}</td>
        </tr>
      `).join('');
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  const loadSelectors = async () => {
    try {
      const [doctors, departments] = await Promise.all([apiFetch('/api/doctors'), apiFetch('/api/departments')]);
      doctorSelect.innerHTML = doctors.length ? doctors.map((doctor) => `<option value="${doctor.id}">${doctor.full_name} – ${doctor.specialty}</option>`).join('') : '<option value="">No doctor found</option>';
      departmentSelect.innerHTML = departments.length ? `<option value="">Select department</option>${departments.map((department) => `<option value="${department.id}">${department.name}</option>`).join('')}` : '<option value="">No department found</option>';
    } catch (error) {
      showAlert(alertContainer, 'danger', `Could not load appointment form data: ${error.message}`);
    }
  };

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      clearAlert(alertContainer);
      const payload = {
        doctor_id: Number(doctorSelect.value),
        department_id: Number(departmentSelect.value),
        appointment_date: document.getElementById('appointmentDate').value,
        symptoms: document.getElementById('appointmentSymptoms').value,
        priority: document.getElementById('appointmentPriority').value,
      };
      const result = await apiFetch('/api/appointments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      showAlert(alertContainer, 'success', 'Appointment booked successfully.');
      form.reset();
      await loadAppointments();
    } catch (error) {
      showAlert(alertContainer, 'danger', error.message);
    }
  });

  loadSelectors();
  loadAppointments();
};

const setupDoctorsPage = () => {
  const alertContainer = document.getElementById('doctorsAlert');
  const loading = document.getElementById('doctorsLoading');
  const tableWrapper = document.getElementById('doctorsTableWrapper');
  const tableBody = document.getElementById('doctorsTable');
  const searchInput = document.getElementById('doctorSearch');
  const departmentFilter = document.getElementById('departmentFilter');
  let doctors = [];

  const filterDoctors = () => {
    const search = searchInput.value.trim().toLowerCase();
    const department = departmentFilter.value;
    tableBody.innerHTML = doctors.filter((doctor) => {
      const matchesSearch = doctor.full_name.toLowerCase().includes(search) || doctor.specialty.toLowerCase().includes(search);
      const matchesDepartment = !department || doctor.specialty.toLowerCase().includes(department.toLowerCase()) || doctor.full_name.toLowerCase().includes(department.toLowerCase());
      return matchesSearch && matchesDepartment;
    }).map((doctor) => `
      <tr>
        <td>${doctor.full_name}</td>
        <td>${doctor.specialty}</td>
        <td>${doctor.license_number || '-'}</td>
        <td>${department || 'General Medicine'}</td>
      </tr>
    `).join('');
  };

  const loadDoctors = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      const [doctorData, departmentData] = await Promise.all([apiFetch('/api/doctors'), apiFetch('/api/departments')]);
      doctors = doctorData;
      departmentFilter.innerHTML = `<option value="">All departments</option>${departmentData.map((department) => `<option value="${department.name}">${department.name}</option>`).join('')}`;
      filterDoctors();
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  searchInput?.addEventListener('input', filterDoctors);
  departmentFilter?.addEventListener('change', filterDoctors);
  loadDoctors();
};

const setupPatientsPage = () => {
  const alertContainer = document.getElementById('patientsAlert');
  const loading = document.getElementById('patientsLoading');
  const tableWrapper = document.getElementById('patientsTableWrapper');
  const tableBody = document.getElementById('patientsTable');
  const searchInput = document.getElementById('patientSearch');

  const loadPatients = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      const patients = await apiFetch('/api/patients');
      tableBody.innerHTML = patients.map((patient) => `
        <tr>
          <td>${patient.full_name}</td>
          <td>${patient.email}</td>
          <td>${patient.phone || '-'}</td>
        </tr>
      `).join('');
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  const filterPatients = () => {
    const search = searchInput.value.trim().toLowerCase();
    document.querySelectorAll('#patientsTable tr').forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(search) ? '' : 'none';
    });
  };

  searchInput?.addEventListener('input', filterPatients);
  loadPatients();
};

const setupDepartmentsPage = () => {
  const alertContainer = document.getElementById('departmentsAlert');
  const loading = document.getElementById('departmentsLoading');
  const grid = document.getElementById('departmentsGrid');

  const loadDepartments = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      const departments = await apiFetch('/api/departments');
      grid.innerHTML = departments.map((department) => `
        <div class="col-md-6 col-xl-4">
          <div class="card rounded-4 shadow-sm p-4 h-100">
            <h5>${department.name}</h5>
            <p class="text-muted">${department.description || 'No description provided.'}</p>
            <div class="mt-3"><span class="badge bg-primary">Beds: ${department.bed_count || 0}</span></div>
          </div>
        </div>
      `).join('');
      loading.classList.add('d-none');
      grid.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  loadDepartments();
};

const setupBedsPage = () => {
  const alertContainer = document.getElementById('bedsAlert');
  const loading = document.getElementById('bedsLoading');
  const tableWrapper = document.getElementById('bedsTableWrapper');
  const tableBody = document.getElementById('bedsTable');

  const loadBeds = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      const beds = await apiFetch('/api/beds');
      tableBody.innerHTML = beds.map((bed) => `
        <tr>
          <td>${bed.bed_number}</td>
          <td>${bed.department || '-'}</td>
          <td>${bed.room_number || '-'}</td>
          <td>${renderBedStatus(bed.status)}</td>
        </tr>
      `).join('');
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  loadBeds();
};

const setupMedicinesPage = () => {
  const alertContainer = document.getElementById('medicinesAlert');
  const loading = document.getElementById('medicinesLoading');
  const tableWrapper = document.getElementById('medicinesTableWrapper');
  const tableBody = document.getElementById('medicinesTable');
  const searchInput = document.getElementById('medicineSearch');
  let medicines = [];

  const loadMedicines = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      medicines = await apiFetch('/api/medicines');
      renderMedicines();
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  const renderMedicines = () => {
    const search = searchInput.value.trim().toLowerCase();
    tableBody.innerHTML = medicines.filter((item) => item.name.toLowerCase().includes(search) || (item.category || '').toLowerCase().includes(search)).map((item) => {
      const lowStock = item.stock_quantity <= 20;
      return `
        <tr class="${lowStock ? 'table-warning' : ''}">
          <td>${item.name}</td>
          <td>${item.category || '-'}</td>
          <td>${item.stock_quantity}</td>
          <td>${item.unit_price ? '$' + item.unit_price.toFixed(2) : '-'}</td>
          <td>${item.manufacturer || '-'}</td>
        </tr>
      `;
    }).join('');
  };

  searchInput?.addEventListener('input', renderMedicines);
  loadMedicines();
};

const setupReportsPage = () => {
  const alertContainer = document.getElementById('reportsAlert');
  const loading = document.getElementById('reportsLoading');
  const tableWrapper = document.getElementById('reportsTableWrapper');
  const tableBody = document.getElementById('reportsTable');

  const loadReports = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      const reports = await apiFetch('/api/reports');
      tableBody.innerHTML = reports.map((report) => `
        <tr>
          <td>${report.title}</td>
          <td>${report.summary || 'No summary available.'}</td>
          <td>${formatDateTime(report.report_date)}</td>
        </tr>
      `).join('');
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  loadReports();
};

const setupPrescriptionsPage = () => {
  const alertContainer = document.getElementById('prescriptionsAlert');
  const loading = document.getElementById('prescriptionsLoading');
  const tableWrapper = document.getElementById('prescriptionsTableWrapper');
  const tableBody = document.getElementById('prescriptionsTable');

  const loadPrescriptions = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      tableWrapper.classList.add('d-none');
      const prescriptions = await apiFetch('/api/prescriptions');
      tableBody.innerHTML = prescriptions.map((prescription) => `
        <tr>
          <td>${prescription.medicine_name}</td>
          <td>${prescription.dosage || '-'}</td>
          <td>${prescription.instructions || '-'}</td>
          <td>${prescription.patient || '-'}</td>
        </tr>
      `).join('');
      loading.classList.add('d-none');
      tableWrapper.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  loadPrescriptions();
};

const setupNotificationsPage = () => {
  const alertContainer = document.getElementById('notificationsAlert');
  const loading = document.getElementById('notificationsLoading');
  const list = document.getElementById('notificationsList');

  const loadNotifications = async () => {
    try {
      clearAlert(alertContainer);
      loading.classList.remove('d-none');
      list.classList.add('d-none');
      const notifications = await apiFetch('/api/notifications');
      list.innerHTML = notifications.map((notification) => `
        <div class="list-group-item rounded-4 mb-3 ${notification.read ? 'bg-white' : 'bg-light border'}">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div><strong>${notification.title}</strong></div>
            <span class="badge bg-${notification.read ? 'secondary' : 'info'}">${notification.read ? 'Read' : 'Unread'}</span>
          </div>
          <p class="mb-0 text-muted">${notification.message}</p>
        </div>
      `).join('');
      loading.classList.add('d-none');
      list.classList.remove('d-none');
    } catch (error) {
      loading.classList.add('d-none');
      showAlert(alertContainer, 'danger', error.message);
    }
  };

  loadNotifications();
};

const setupAiChatbotPage = () => {
  const alertContainer = document.getElementById('aiChatbotAlert');
  const chatHistory = document.getElementById('chatHistory');
  const form = document.getElementById('chatbotForm');
  const messageInput = document.getElementById('chatbotMessage');
  const micBtn =document.getElementById("micBtn");
  const loading = document.getElementById("aiLoading");

  const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;

if (SpeechRecognition && micBtn) {

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.interimResults = false;

    recognition.continuous = false;

    micBtn.onclick = () => {

        recognition.start();

    };

    recognition.onresult = (event) => {

        messageInput.value =
        event.results[0][0].transcript;

    };

}
  const appendMessage = (role, text) => {

    const wrapper = document.createElement("div");

    wrapper.className = `d-flex ${
        role === "user"
            ? "justify-content-end"
            : "justify-content-start"
    }`;

    wrapper.innerHTML = `
        <div class="card rounded-4 shadow-sm p-3 mb-2 ${
            role === "user"
                ? "bg-primary text-white"
                : "bg-light"
        }" style="max-width:85%;">

            <strong>
                ${role === "user" ? "You" : "MediAI"}
            </strong>

            <hr>

            <div>
                ${text.replace(/\n/g, "<br>")}
            </div>

        </div>
    `;

    chatHistory.appendChild(wrapper);

    chatHistory.scrollTop = chatHistory.scrollHeight;
};

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;
    appendMessage('user', message);
    messageInput.value = '';
    try {
      clearAlert(alertContainer);
      loading.classList.remove("d-none");
      const response = await apiFetch('/api/ai/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      loading.classList.add("d-none");

appendMessage(
    "assistant",
    response.response || "No response received."
);

const speech = new SpeechSynthesisUtterance(
    response.response
);

speech.lang = "en-US";

speech.rate = 1;

speech.pitch = 1;

speechSynthesis.speak(speech);
    } catch (error) {
      loading.classList.add("d-none");
      showAlert(alertContainer, 'danger', error.message);
    }
  });
};

const setupAiReportSummarizerPage = () => {
  const alertContainer = document.getElementById('aiReportSummarizerAlert');
  const form = document.getElementById('reportSummarizerForm');
  const summarySection = document.getElementById('reportSummaryResult');
  const summaryContent = document.getElementById('reportSummaryContent');
  const loading =
document.getElementById("reportLoading");

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      clearAlert(alertContainer);
      summarySection.classList.add('d-none');
      const formData = new FormData();
      const text = document.getElementById('reportText').value.trim();
      const fileInput = document.getElementById('reportFile');
      if (text) formData.append('text', text);
      if (fileInput.files.length) formData.append('file', fileInput.files[0]);
      if (!text && fileInput.files.length === 0) {
        showAlert(alertContainer, 'warning', 'Please enter report text or upload a PDF file.');
        return;
      }
      loading.classList.remove("d-none");
      const response = await fetch('/api/ai/report-summarizer', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      loading.classList.add("d-none");
      if (!response.ok) throw new Error(result.message || result.error || 'Unable to summarize report.');
      summaryContent.innerHTML = `
<h3>📄 Summary</h3>

<p>${result.summary}</p>

<hr>

<h4>🔍 Findings</h4>

<ul>
${(result.findings || [])
.map(x => `<li>${x}</li>`)
.join("")}
</ul>

<hr>

<h4>📌 Follow Up</h4>

<ul>
${(result.follow_up || [])
.map(x => `<li>${x}</li>`)
.join("")}
</ul>

<hr>

<h4>Severity</h4>

<span class="badge bg-warning">
${result.severity || "Unknown"}
</span>
`;
      summarySection.classList.remove('d-none');
    } catch (error) {
      loading.classList.add("d-none");
      showAlert(alertContainer, 'danger', error.message);
    }
  });
};

const setupAiPrescriptionExplainerPage = () => {
  const alertContainer = document.getElementById('aiPrescriptionExplainerAlert');
  const form = document.getElementById('prescriptionExplainerForm');
  const resultSection = document.getElementById('prescriptionExplanationResult');
  const resultContent = document.getElementById('prescriptionExplanationContent');
  const loading =
document.getElementById("prescriptionLoading");

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      clearAlert(alertContainer);
      resultSection.classList.add('d-none');
      const payload = {
        medicine_name: document.getElementById('explainerMedicine').value.trim(),
        dosage: document.getElementById('explainerDosage').value.trim(),
        instructions: document.getElementById('explainerInstructions').value.trim(),
      };
      if (!payload.medicine_name) {
        showAlert(alertContainer, 'warning', 'Please enter the medicine name.');
        return;
      }
      loading.classList.remove("d-none");
      const response = await apiFetch('/api/ai/prescription-explainer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const d = response.data;
      loading.classList.add("d-none");
resultContent.innerHTML = `
<div class="card shadow-sm">
<div class="card-body">

<h3>${d.medicine}</h3>

<hr>

<h5>💊 Used For</h5>
<p>${d.used_for}</p>

<h5>📌 How to Take</h5>
<p>${d.how_to_take}</p>

<h5>⚠ Side Effects</h5>

<ul>
${d.side_effects.map(x=>`<li>${x}</li>`).join("")}
</ul>

<h5>✅ Precautions</h5>

<ul>
${d.precautions.map(x=>`<li>${x}</li>`).join("")}
</ul>

</div>
</div>
`;
      resultSection.classList.remove('d-none');
    } catch (error) {
      showAlert(alertContainer, 'danger', error.message);
    }
  });
};

const setupAiAppointmentAssistantPage = () => {
  const alertContainer = document.getElementById('aiAppointmentAssistantAlert');
  const form = document.getElementById('appointmentAssistantForm');
  const resultSection = document.getElementById('assistantResult');
  const resultContent = document.getElementById('assistantContent');
  const loading =
document.getElementById(
"appointmentLoading"
);
  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      clearAlert(alertContainer);
      resultSection.classList.add('d-none');
      const symptoms = document.getElementById('assistantSymptoms').value.trim();
      if (!symptoms) {
        showAlert(alertContainer, 'warning', 'Please describe your symptoms.');
        return;
      }
      loading.classList.remove("d-none");
      const response = await apiFetch('/api/ai/appointment-assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms }),
      });
      loading.classList.add("d-none");
      
      resultContent.innerHTML = `

<div class="card shadow rounded-4">

<div class="card-body">

<h3 class="mb-3">
🏥 Recommended Department
</h3>

<p>
${response.department}
</p>

<hr>

<h4>
👨‍⚕️ Doctor
</h4>

<p>
${response.doctor}
</p>

<hr>

<h4>
⚡ Priority
</h4>

<span class="badge bg-danger">

${response.priority}

</span>

<hr>

<h4>
📋 Summary
</h4>

<p>

${response.summary}

</p>

<hr>

<h4>
🛡 Precautions
</h4>

<ul>

${response.precautions
.map(item=>`<li>${item}</li>`)
.join("")}

</ul>

<hr>

<div class="alert alert-warning">

${response.disclaimer}

</div>

</div>

</div>

`;

resultSection.classList.remove("d-none");
    } catch (error) {
      loading.classList.add("d-none");
      showAlert(alertContainer, 'danger', error.message);
    }
  });
};

const setupDashboardChart = () => {
  const ctx = document.getElementById('dashboardChart');
  if (!ctx) return;
  const numbers = Array.from(document.querySelectorAll('.display-6')).map((el) => Number(el.textContent.trim()) || 0);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Doctors', 'Patients', 'Appointments', 'Beds'],
      datasets: [{ label: 'Hospital Overview', data: numbers, backgroundColor: ['#2f80ed', '#56ccf2', '#8bc34a', '#ffb703'] }],
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } },
  });
};

window.addEventListener('DOMContentLoaded', () => {
  setupDashboardChart();
  setupAiDrugInteractionPage();
  whenExists('appointmentsPage', setupAppointmentsPage);
  whenExists('doctorsPage', setupDoctorsPage);
  whenExists('patientsPage', setupPatientsPage);
  whenExists('departmentsPage', setupDepartmentsPage);
  whenExists('bedsPage', setupBedsPage);
  whenExists('medicinesPage', setupMedicinesPage);
  whenExists('reportsPage', setupReportsPage);
  whenExists('prescriptionsPage', setupPrescriptionsPage);
  whenExists('notificationsPage', setupNotificationsPage);
  whenExists('aiChatbotPage', setupAiChatbotPage);
  whenExists('aiReportSummarizerPage', setupAiReportSummarizerPage);
  whenExists('aiPrescriptionExplainerPage', setupAiPrescriptionExplainerPage);
  whenExists('aiAppointmentAssistantPage', setupAiAppointmentAssistantPage);
  whenExists('drugInteractionPage', setupAiDrugInteractionPage);
});
