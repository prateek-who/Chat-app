function setInactiveOnBeforeUnload(username) {
    window.addEventListener('beforeunload', function(event) {
        const payload = JSON.stringify({ username: username });
        console.log(username);

        fetch('/set_inactive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: payload
        });

        console.log(username);

        const confirmationMessage = 'Are you sure you want to leave the chat?';
        return confirmationMessage;
    });
}



// FIX THIS FFS. I AM SOOOO DONE WITH THIS SHITTTTTT
