document.addEventListener('DOMContentLoaded', () => {
  const button = document.getElementById('voiceAssistantBtn');
  const output = document.getElementById('voiceOutput');
  if (!button || !output) {
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    output.textContent = 'Voice commands are not available in this browser.';
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = false;

  button.addEventListener('click', () => {
    recognition.start();
    output.textContent = 'Listening...';
  });

  recognition.onresult = (event) => {
    const command = event.results[0][0].transcript;
    output.textContent = `Heard: ${command}`;
    if (command.toLowerCase().includes('book appointment')) {
      window.location.href = '/dashboard';
    } else if (command.toLowerCase().includes('show reports')) {
      window.location.href = '/dashboard';
    } else if (command.toLowerCase().includes('open dashboard')) {
      window.location.href = '/dashboard';
    }
  };

  recognition.onerror = () => {
    output.textContent = 'Unable to capture speech.';
  };
});
