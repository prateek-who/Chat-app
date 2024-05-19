function setupWebsocket(username) {
    const socket = io();

    const form = document.querySelector('form');
    form.onsubmit = function() {
        const textInput = document.getElementById('text');
        const text = textInput.value;
        if (text.trim() !== '') {
            socket.emit('message', { username: username, text: text });
            textInput.value = '';
        }
        return false;
    };

    socket.on('message', function(msg) {
        const messageList = document.getElementById('message-list');
        const item = document.createElement('li');

        if (typeof msg === 'object' && 'username' in msg && 'text' in msg) {
            item.textContent = `${msg.username}: ${msg.text}`;
            if (msg.username === username) {
                item.classList.add('user-message');
            } else {
                item.classList.add('other-message');
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

    window.onload = function() {
        socket.emit('join', { username: username });
    };
}