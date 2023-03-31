const questionTable = document.getElementById("questionTable")
const question = document.getElementById('question')
const askedBy = document.getElementById('askedBy')
const askedOn = document.getElementById('askedOn')
const answeredBy = document.getElementById('answeredBy')
const date = document.getElementById('date')
const answer = document.getElementById('answer')
const answeringBody = document.getElementById('answeringBody')
const dueAnswer = document.getElementById('dueAnswer')
const notifyMe = document.getElementById('watchQuestion')

// Populate PQ search table
async function viewQuestion(id, bookmarked) {
    fetch(`/onWatchlist/${id}`)
        .then((response) => response.json())
        .then((result) => notifyMe.checked = result.questionPresent);

    questionTable.style.visibility = "visible"

    var route = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions/QUESTION?expandMember=true"
    route = route.replace('QUESTION', id)

    const response = await fetch(route);
    const data = await response.json();

    console.log(data)

    question.innerHTML = data['value']['questionText']
    askedBy.innerHTML = data['value']['askingMember']['name']
    askedOn.innerHTML = data['value']['dateTabled'].slice(0, 10)

    try {
        document.getElementById("answeredQuestion").style.visibility = "visible"
        document.getElementById("unansweredQuestion").style.visibility = "hidden"
        date.innerHTML = data['value']['dateAnswered'].slice(0, 10)
        answeredBy.innerHTML = data['value']['answeringMember']['name']
        answer.innerHTML = data['value']['answerText'].replace("<p>", "")

    } catch {
        document.getElementById("answeredQuestion").style.display = "none"
        document.getElementById("unansweredQuestion").style.visibility = "visible"
        dueAnswer.innerHTML = data['value']['dateForAnswer'].slice(0, 10)
        answeringBody.innerHTML = data['value']['answeringBodyName']
    }

    // Function called by clicking 'notify me' checkbox
    document.getElementById('watchQuestion').addEventListener('change', watchQuestion);
    document.getElementById('watchQuestion').dataset.id = id
};


// Add / remove question from user's watchlist
function watchQuestion() {
    id = this.dataset.id
    fetch(`/notifyMe/${id}`)
        .then((response) => response.json())
        .then((result) => console.log(result.message));
}


// Add / remove question from user's bookmarks
function bookmark(questionId) {
    console.log(questionId)

    fetch(`/bookmark/${questionId}`)
        .then((response) => response.json())
        .then((result) => {

            // Update star icon 
            if (result.star == true) {
                document.getElementById(`bookmark_${questionId}`).innerHTML = '&#9733';
            }
            else {
                document.getElementById(`bookmark_${questionId}`).innerHTML = '&#9734';
            }
        });
}