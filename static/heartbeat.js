let uname;
function sendHeartbeat(username) {
    fetch('/heartbeat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: uname })
    });
}

function store_uname(username){
    uname = username;
    sendHeartbeat(uname);
}

// Send heartbeat every 10 seconds
setInterval(sendHeartbeat, 10_000);
