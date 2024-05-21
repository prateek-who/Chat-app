function setInactiveOnUnload(username){
    console.log(username));
    window.addEventListener('unload', function (){
        const payload = JSON.stringify({username: username});
        navigator.sendBeacon('/set_inactive', payload)
    })
}


// FIX THIS FFS. I AM SOOOO DONE WITH THIS SHITTTTTT