const errorMessages = document.querySelectorAll('p');

function hideMessages() {
    errorMessages.forEach(message => {
        setInterval(() => {
            message.style.display = 'none';
        }, 3500);
    });
}

hideMessages();