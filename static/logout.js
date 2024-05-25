function setInactiveOnBeforeUnload(username) {
    window.addEventListener('beforeunload', function(event) {
        // const payload = JSON.stringify({ username: username });
        // fetch('/set_inactive', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     body: payload
        // });

        console.log('hello')
        socket.emit('disconnect');
    });
}

socket.on('redirect', function() {
    // redirect user to home page, but not working as of now
    console.log('hello');
    window.location.href = '/';
});

// FIX THIS FFS. I AM SOOOO DONE WITH THIS SHITTTTTT
