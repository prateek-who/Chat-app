let name;
function store_uname(username){
    name = username;
    sendHeartbeat(name);
}

document.getElementById("chat-room").addEventListener("click", function(e){
    window.location.href = '/general_chat_room.html';
})