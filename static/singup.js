document.getElementById('submit-button').addEventListener('click', async function(event) {
    event.preventDefault();

    let username = document.getElementById('username').value;
    let password1 = document.getElementById('first-password').value;
    let password2 = document.getElementById('second-password').value;

    const uname_check = await checkUsernameValidity(username)

    if (uname_check){
        document.getElementById('username-error-message').style.display = 'block';
    }
    else{
        document.getElementById('username-error-message').style.display = 'none';

        if (password1 !== password2) {
            document.getElementById('error-message').style.display = 'block';
        }
        else{
            document.getElementById('error-message').style.display = 'none';

            const response = await registerUser(username, password1); // Sending data to finally store in DB

            if (response.success) {
                // Redirecting to main page here
                window.location.href = `/`;
            } else {
                // Display error message
                document.getElementById('registration-error-message').style.display = 'block';
            }
        }
    }
});

async function checkUsernameValidity(username){
    try {
        const response = await fetch('/check_username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username })
        });
        const data = await response.json();
        return data.exists;
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}

async function registerUser(username, password) {
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        });
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return { success: false };
    }
}

document.getElementById('back-button').addEventListener('click', function (e){
    e.preventDefault();
    window.location.href="/";
})
