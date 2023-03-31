// Check if watchlist question has been answered
async function notifyCheck() {

    fetch('/notifyCheck')
        .then((response) => response.json())
        .then((result) => {

            console.log(result)

            // If notification(s) exist, add number to NavBar user icon as alert
            if (result.notifications >= 1) {
                if (document.getElementById('notifications').innerHTML != result.notifications) {
                    document.getElementById('notifications').innerHTML = result.notifications
                }
            }
        });
}