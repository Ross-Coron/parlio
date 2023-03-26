// Check if watchlist question answered
async function notifyCheck() {
    fetch('/notifyCheck')
        .then((response) => response.json())
        .then((result) => {
            
            console.log(result)
            
            // If notifications, append user in NavBar with number
            if (result.notifications >= 1){
                document.getElementById('notifications').innerHTML = result.notifications
            }

        });
}