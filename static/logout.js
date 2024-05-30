function setInactiveOnBeforeUnload(username) {
    window.addEventListener('beforeunload', function(event) {
        // This log confirms that the beforeunload event is triggered
        console.log('beforeunload event triggered');

        // Make sure to execute socket.emit before the page unloads
        socket.emit('disconnect');

        // To redirect on refresh, this needs to be added outside of the beforeunload event
        setTimeout(() => {
            window.location.href = '/';
        }, 0);
    });
}

// Place the socket.on('redirect') listener outside of the beforeunload event handler
socket.on('redirect', function() {
    console.log('Redirected workingwerfgwrefgwrgw');
    window.location.href = '/';
});

// I want to shoot somebody rn.