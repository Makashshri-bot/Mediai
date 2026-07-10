/**
 * AI Symptom Checker Page Script
 * 
 * Handles form submission, API calls, loading states, error handling,
 * and result rendering for the AI-powered hospital triage system.
 */

const setupAiSymptomCheckerPage = () => {
  const alertContainer = document.getElementById('symptomCheckerAlert');
  const form = document.getElementById('symptomCheckerForm');
  const symptomInput = document.getElementById('symptomInput');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const resultsSection = document.getElementById('resultsSection');

  /**
   * Clear existing results and hide results section
   */
  const clearResults = () => {
    resultsSection.classList.add('d-none');
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
   * Display success result
   */
  const displayResult = (result) => {
    try {
      // Department
      document.getElementById('resultDepartment').textContent = result.department || '-';
      document.getElementById('resultSummary').textContent = result.summary || 'Please visit the recommended department.';

      // Doctor
      document.getElementById('resultDoctor').textContent = result.doctor || 'Available doctor on duty';
      document.getElementById('resultSpecialty').textContent = result.doctor_specialty || '-';

      // Urgency Badge with color
      const urgencyColor = {
        'Low': 'success',
        'Medium': 'warning',
        'High': 'danger',
        'Urgent': 'danger'
      };
      const urgencyBgClass = urgencyColor[result.urgency] || 'secondary';
      document.getElementById('resultUrgencyBadge').innerHTML =
        `<span class="badge bg-${urgencyBgClass} p-3 fs-6">${result.urgency || 'Unknown'}</span>`;

      // Priority Badge with color
      const priorityColor = {
        'normal': 'info',
        'medium': 'warning',
        'urgent': 'danger'
      };
      const priorityBgClass = priorityColor[result.priority] || 'secondary';
      document.getElementById('resultPriorityBadge').innerHTML =
        `<span class="badge bg-${priorityBgClass} p-3 fs-6">${result.priority || 'Normal'}</span>`;

      // Precautions
      const precautions = result.precautions || [];
      if (precautions.length > 0) {
        document.getElementById('resultPrecautions').innerHTML = precautions
          .map(p => `<li class="list-group-item"><i class="fa-solid fa-check text-success me-2"></i>${p}</li>`)
          .join('');
      } else {
        document.getElementById('resultPrecautions').innerHTML =
          '<li class="list-group-item text-muted">No specific precautions identified.</li>';
      }

      // Disclaimer
      document.getElementById('resultDisclaimer').textContent = result.disclaimer 
        || 'Please consult with a healthcare professional for proper evaluation.';

      // Show results section
      clearAlert(alertContainer);
      resultsSection.classList.remove('d-none');
      loadingSpinner.classList.add('d-none');
      analyzeBtn.disabled = false;

      // Smooth scroll to results
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      console.error('Error displaying result:', error);
      showError('Error displaying results. Please try again.');
    }
  };

  /**
   * Handle form submission
   */
  form?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const symptoms = symptomInput.value.trim();

    // Validation
    if (!symptoms) {
      showError('Please describe your symptoms.');
      return;
    }

    if (symptoms.length < 5) {
      showError('Please provide more details about your symptoms.');
      return;
    }

    // Start loading
    clearResults();
    clearAlert(alertContainer);
    loadingSpinner.classList.remove('d-none');
    analyzeBtn.disabled = true;

    try {
      // Call API
      const response = await apiFetch('/api/ai/symptom-checker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms })
      });

      // Display results
      displayResult(response);
    } catch (error) {
      console.error('Symptom checker error:', error);
      showError(error.message || 'Unable to analyze symptoms. Please try again.');
    }
  });

  // Initialize on page load
  console.log('AI Symptom Checker page initialized');
};

/**
 * Initialize when DOM is ready
 */
window.addEventListener('DOMContentLoaded', () => {
  whenExists('aiSymptomCheckerPage', setupAiSymptomCheckerPage);
});
