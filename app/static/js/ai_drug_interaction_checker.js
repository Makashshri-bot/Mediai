/**
 * AI Drug Interaction Checker Page Script
 * 
 * Handles form submission, API calls, loading states, error handling,
 * and result rendering for the AI-powered drug interaction analysis.
 */

const setupAiDrugInteractionPage = () => {
  const alertContainer = document.getElementById('drugAlert');
  const form = document.getElementById('drugInteractionForm');
  const drug1Input = document.getElementById('drug1Input');
  const drug2Input = document.getElementById('drug2Input');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const resultsSection = document.getElementById("resultSection");
  const checkAgainBtn = document.getElementById('checkAgainBtn');
  const consultBtn = document.getElementById('consultBtn');

  /**
   * Clear existing results and hide results section
   */
  const clearResults = () => {
    console.log(resultsSection);
    resultsSection.classList.add('d-none');
  };

  /**
   * Clear form inputs
   */
  const clearForm = () => {
    form.reset();
    drug1Input.focus();
  };

  /**
   * Display error alert
   */
  const showError = (message) => {
    clearAlert(alertContainer);
    showAlert(alertContainer, 'danger', `❌ ${message}`);
    loadingSpinner.classList.add('d-none');
    analyzeBtn.disabled = false;
  };

  /**
   * Display success result with styling based on risk level
   */
  const displayResult = (response) => {

    const result = response.result;

    document.getElementById("resultDrug1").textContent =
        drug1Input.value;

    document.getElementById("resultDrug2").textContent =
        drug2Input.value;

    const riskColors = {
        Low: { color: "success", icon: "fa-check-circle" },
        Moderate: { color: "warning", icon: "fa-exclamation-circle" },
        High: { color: "danger", icon: "fa-exclamation-triangle" },
        Unknown: { color: "secondary", icon: "fa-question-circle" }
    };

    const level = result.severity || "Unknown";
    const style = riskColors[level] || riskColors.Unknown;

    document.getElementById("resultRiskBadge").innerHTML = `
        <span class="badge bg-${style.color} p-3 fs-6">
            <i class="fa-solid ${style.icon} me-2"></i>
            ${level}
        </span>
    `;

    document.getElementById("resultExplanation").textContent =
        result.interaction;

    document.getElementById("resultRecommendation").innerHTML = `
<h5>✅ Advice</h5>
<ul>
${(result.advice || [])
    .map(item => `<li>${item}</li>`)
    .join("")}
</ul>
`;

    document.getElementById("resultSymptoms").innerHTML = `
<h5>⚠ Possible Symptoms</h5>
<ul>
${(result.symptoms || [])
    .map(item => `<li>${item}</li>`)
    .join("")}
</ul>
`;

    document.getElementById("resultDisclaimer").innerHTML = `
This AI tool provides educational information only.
Always consult your doctor or pharmacist before taking medications together.
`;

    resultsSection.classList.remove("d-none");

    loadingSpinner.classList.add("d-none");

    analyzeBtn.disabled = false;
    
};
  /**
   * Handle form submission
   */
  form?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const drug1 = drug1Input.value.trim();
    const drug2 = drug2Input.value.trim();

    // Validation
    if (!drug1 || !drug2) {
      showError('Please enter both drug names.');
      return;
    }

    if (drug1.length < 2 || drug2.length < 2) {
      showError('Please enter valid drug names (at least 2 characters).');
      return;
    }

    if (drug1.toLowerCase() === drug2.toLowerCase()) {
      showError('Please enter two different drugs.');
      return;
    }

    // Show loading state
    clearResults();
    clearAlert(alertContainer);
    loadingSpinner.classList.remove('d-none');
    analyzeBtn.disabled = true;

    try {

    const response = await apiFetch("/api/ai/drug-interaction-checker", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            drug1,
            drug2
        })
    });

    displayResult(response);

}
    catch (error) {
      showError(error.message || 'Unable to analyze drug interaction. Please try again.');
    }
  });

  /**
   * "Check Another" button handler
   */
  checkAgainBtn?.addEventListener('click', () => {
    clearResults();
    clearForm();
    clearAlert(alertContainer);
  });

  /**
   * "Consult Doctor" button handler - redirect to appointments
   */
  consultBtn?.addEventListener('click', () => {
    // Redirect to book appointment or contact doctor
    window.location.href = '/appointments';
  });
};
