document.getElementById('submit').addEventListener('click', async function (event){
    event.preventDefault()

    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

    const account_check = await checkAccountValidity(username, password)

    if (!account_check.success) {
        document.getElementById('login-error-message').style.display = 'block';
        document.getElementById('login-error-message').textContent = account_check.message;
    }
    else if (account_check.logged_in) {
        document.getElementById('login-error-message').style.display = 'block';
        document.getElementById('login-error-message').textContent = account_check.message;
    }
    else {
        document.getElementById('login-error-message').style.display = 'none';
        // Redirect to the chat room or another page if login is successful
        window.location.href = `/my_space.html`;
    }
});

async function checkAccountValidity(username, password){
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        });
        return await response.json();
    }
    catch(error){
        console.error('Error:', error);
        return false;
    }
}
