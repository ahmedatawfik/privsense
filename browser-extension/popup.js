document.getElementById('pseudonymizeButton').addEventListener('click', () => {
    const inputText = document.getElementById('inputText').value;
    const outputText = document.getElementById('outputText');
  
    if (!inputText) {
      outputText.value = "Please enter some text.";
      return;
    }
  
    fetch('http://127.0.0.1:5000/pseudonymize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: inputText })
    })
    .then(response => response.json())
    .then(data => {
      if (data.pseudonymized_text) {
        outputText.value = data.pseudonymized_text;
      } else {
        outputText.value = "Error pseudonymizing text.";
      }
    })
    .catch(error => {
      console.error('Error:', error);
      outputText.value = "Error pseudonymizing text.";
    });
  });
  
  document.getElementById('copyButton').addEventListener('click', () => {
    const outputText = document.getElementById('outputText');
    outputText.select();
    document.execCommand('copy');
    alert('Text copied to clipboard!');
  });
  