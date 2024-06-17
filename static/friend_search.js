let name;
function store_name(username){
    name = username;
    sendHeartbeat(name);
}

document.getElementById("chat-room").addEventListener("click", function(e){
    window.location.href = `/general_chat_room/we6Tv77yM70LHhRyIprn`;
})

document.getElementById('find-him').addEventListener('click', function() {
    const searchField = document.getElementById('friend-search');
    const friendName = searchField.value.trim();

    if (friendName) {
        searchFriend(friendName);
    } else {
        displayNotification('Please enter a name to search.');
    }
});

function searchFriend(friendName) {
    fetch('/sending_request_for_username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: friendName , my_name: name})
    })
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                displayButton(`User "${friendName}" found! Click to chat.`, data.roomId);
            } else {
                displayNotification(`User "${friendName}" does not exist.`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayNotification('An error occurred while searching. Please try again later.');
        });
}

function displayNotification(message) {
    const notificationBar = document.getElementById('notification-bar');
    notificationBar.innerHTML = '';

    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerText = message;

    notificationBar.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 2000);
}

function displayButton(message, roomId) {
    const notificationBar = document.getElementById('notification-bar');
    notificationBar.innerHTML = '';

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'button-container';

    const button = document.createElement('button');
    button.className = 'chat-button custom-button';
    button.innerText = message;
    button.onclick = () => {
        window.location.href = `/chatroom/${roomId}`;
    };

    buttonContainer.appendChild(button);
    notificationBar.appendChild(buttonContainer);
}

const socket = io();

// socket.on('connect', () => {
//     console.log('Connected to WebSocket server with SID: ', socket.id);
// });

// Handle friend search notification event
socket.on('friend_search_notification', function(data) {
    const notificationMessage = `${data.username} wants you to join the chat room.`;
    displayButton(notificationMessage, data.roomId);
});
