function setupWebsocket(username, roomId) {
    const socket = io();

    socket.on('connect', () => {
        console.log(`Connected to WebSocket server with \`${roomId}`);
        socket.emit('join', { username: username, room_id: roomId });
    });

    const form = document.querySelector('form');
    form.onsubmit = function() {
        const textInput = document.getElementById('text-box');
        const text = textInput.value;
        if (text.trim() !== '') {
            socket.emit('message', { username: username, text: text, room_id: roomId });
            textInput.value = '';
        }
        return false;
    };

    // socket.emit('join', { username: username});

    socket.on('message', function(msg) {
        console.log(msg)
        const messageList = document.getElementById('message-list');
        const item = document.createElement('li');

        if (typeof msg === 'object' && 'username' in msg && 'text' in msg) {
            if (msg.username === 'Server') {
                item.textContent = `${msg.text}`;
                item.classList.add('server-message');
            } else {
                item.textContent = `${msg.username}: ${msg.text}`;
                if (msg.username === username) {
                    item.classList.add('user-message');
                } else {
                    item.classList.add('other-message');
                }
            }
        } else {
            item.textContent = 'Error: Invalid message format';
        }

        messageList.appendChild(item);
        scrollToBottom();
    });

    const messagesContainer = document.querySelector('#message-list');

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}
