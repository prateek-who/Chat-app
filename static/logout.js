// Entire thing needs fixing!!

let isPageVisible = true;
let isRefreshing = false;

function handleVisibilityChange() {
    isPageVisible = !document.hidden;
}

document.addEventListener('visibilitychange', handleVisibilityChange);

window.addEventListener('beforeunload', async function() {
    // If the page is still visible, it means the user is navigating away within the same tab
    // We don't need to send the request in this case
    if (isPageVisible) return;

    try {
        const response = await fetch('/set_inactive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (!data.success) {
            console.error('Failed to set user inactive:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

window.addEventListener('beforeunload', function() {
    isRefreshing = true;
});
