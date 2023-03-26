function isSitting() {

    fetch('/isSitting')
        .then((response) => response.json())
        .then((result) => {
            console.log(result.message)

            if (result['commonsSitting'] == false) {
                document.getElementById('commonsSitting').innerHTML = "Not sitting"
                document.getElementById('liveCommons').style.animationPlayState = 'initial'
                document.getElementById('liveCommons').style.animationPlayState = 'paused'
            }
            else {
                document.getElementById('commonsSitting').innerHTML = "Sitting"
                document.getElementById('liveCommons').style.animationPlayState = 'running'
            }

            if (result['lordsSitting'] == false) {
                document.getElementById('lordsSitting').innerHTML = "Not sitting"
                document.getElementById('liveLords').style.animationPlayState = 'initial'
                document.getElementById('liveLords').style.animationPlayState = 'paused'
            }
            else {
                document.getElementById('lordsSitting').innerHTML = "Sitting"
                document.getElementById('liveLords').style.animationPlayState = 'running'
            }
        });

    setTimeout(isSitting, 60000)
}


function startTime() {

    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    const today = new Date();
    let h = today.getHours();
    let m = today.getMinutes();
    m = checkTime(m);
    document.getElementById('time').innerHTML = h + ":" + m;

    let date = today.getDate()
    let month = today.getMonth()




    let year = today.getFullYear();
    document.getElementById('date').innerHTML = date + " " + monthNames[month] + " " + year


    setTimeout(startTime, 1000);
}

function checkTime(i) {
    if (i < 10) { i = "0" + i };  // add zero in front of numbers < 10
    return i;
}