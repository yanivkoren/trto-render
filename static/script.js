document.querySelectorAll('.gender-button').forEach(button => {
    button.addEventListener('click', () => {
        const level = document.getElementById('level').value;
        const gender = button.getAttribute('data-gender');
        fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ level, gender })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('nousResponse').innerText = 'Nous Response: ' + data.nous_response;
            document.getElementById('grokResponse').innerText = 'Grok Response: ' + data.grok_response;
        })
        .catch(error => console.error('Error:', error));
    });
});
