function isSitting() {

    const commonsStatus = document.getElementById('commonsSitting')
    const lordsStatus = document.getElementById('lordsSitting')
    var commonsAlert = new Audio('https://now.parliament.uk/dist/newslide-commons.mp3');
    var LordsAlert = new Audio('https://now.parliament.uk/dist/newslide-lords.mp3');


    fetch('/isSitting')
        .then((response) => response.json())
        .then((result) => {
            console.log(result.message)
""
            if (commonsStatus.innerHTML == "Not sitting" && result['commonsSitting'] == "Sitting"){
                console.log("Commons alert played")
                commonsAlert.play();
            }

            else if (commonsStatus.innerHTML == "Sitting" && result['commonsSitting'] == "Not sitting"){
                console.log("Commons alert played")
                commonsAlert.play();
            }

            if (lordsStatus.innerHTML == "Not sitting" && result['lordsSitting'] == "Sitting"){
                console.log("Lords alert played")
                lordsAlert.play();
            }

            else if (lordsStatus.innerHTML == "Sitting" && result['lordsSitting'] == "Not sitting"){
                console.log("Lords alert played")
                lordsAlert.play();
            }

            //

            if (result['commonsSitting'] == "Not sitting") {
                commonsStatus.innerHTML = "Not sitting"
                document.getElementById('liveCommons').style.animationPlayState = 'initial'
                document.getElementById('liveCommons').style.animationPlayState = 'paused'
            }
            else {
                commonsStatus.innerHTML.innerHTML = "Sitting"
                document.getElementById('liveCommons').style.animationPlayState = 'running'
            }

            if (result['lordsSitting'] == "Not sitting") {
                lordsStatus.innerHTML = "Not sitting"
                document.getElementById('liveLords').style.animationPlayState = 'initial'
                document.getElementById('liveLords').style.animationPlayState = 'paused'
            }
            else {
                lordsStatus.innerHTML = "Sitting"
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