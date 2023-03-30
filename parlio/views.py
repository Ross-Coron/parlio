from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.http import JsonResponse
from .models import *
import requests
import json


### Visible routes ###

# Default route - shows sitting status of the House of Commons and Lords
def index(request):
    return render(request, "parlio/index.html")


# Annunciator (in-progress)
def annunciator(request):
    return render(request, "parlio/annunciator.html")


# User's profile page - displays notifications and bookmarked questions
# Redirect to login. Route saved in settings.py
@login_required(redirect_field_name='my_redirect_field')
def profile(request, profile):

    # Get list of question IDs corresponding to notifications
    notifications = Notification.objects.filter(user=request.user).values_list('question', flat=True)

    questions = []

    for notification in notifications:
        question = Question.objects.filter(pk=notification).values_list('uniqueId', flat=True).first()
        questions.append(question)

    notifications = []

    # For each question in list, create a dictionary (id, question, etc) then add to list
    for question in questions:
        
        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions/" + str(question)

        response = requests.get(url)
        jsonResponse = response.json()
        questions = jsonResponse
        
        item = {"id": questions['value']['id'], "uIn": questions['value']['uin'], "heading": questions['value']['heading'], "answeredOn": questions['value']
               ['dateAnswered'][0:10], "questionText": questions['value']['questionText'],  "answerText": questions['value']['answerText']}
        
        notifications.append(item)

    print("Debug - notifications: ", notifications)

    # Get bookmarked questions
    bookmarkedQuestions = Question.objects.filter(bookmarkBy=request.user).values_list('uniqueId', flat=True)
    print("Debug - bookmarked question IDs: ", bookmarkedQuestions)

    bookmarks = []

    for bookmarkedQuestion in bookmarkedQuestions:
       
        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions/" + str(bookmarkedQuestion)
    
        response = requests.get(url)
        jsonResponse = response.json()
        questions = jsonResponse

        item = {"id": questions['value']['id'], "uin": questions['value']['uin'], "heading": questions['value']['heading']}
        
        bookmarks.append(item)
    
    print("Debug - bookmarks: ", bookmarks)

    return render(request, "parlio/user.html", {
        "notifications": notifications,
        "bookmarks": bookmarks
    })


# Search, view, and bookmark PQs
@login_required(redirect_field_name='my_redirect_field')
def question(request):

    # Default route (e.g. if accessed via a hyperlink)
    if request.method == "GET":
        return render(request, "parlio/question.html")

    # If accessed via form submission (POST)
    elif request.method == "POST":

        # Search PQs using Parliament's API and user-provided search term (question ID)
        questionId = request.POST["questionId"]

        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions?uIN=" + questionId

        results = []

        response = requests.get(url)
        jsonResponse = response.json()
        questions = jsonResponse["results"]

        # Get list of user's bookmarked questions
        bookmarkedQuestions = Question.objects.filter(bookmarkBy=request.user).values_list('uniqueId', flat=True)

        for question in questions:

            entry = {}

            # Get question's ID and check if bookmarked 
            questionID = int(question['value']['id'])
            if questionID in bookmarkedQuestions:
                print("Debug - question", questionID, "is bookmarked")
                isBookmarked = True
            else:
                print("Debug - question", questionID, "is NOT bookmarked")
                isBookmarked = False

            # Get question's subject
            questionSubject = question['value']['heading']

            # Get date question answered on (if possible)
            try:
                questionAnswered = question['value']['dateAnswered'][0:10]
            except:
                questionAnswered = "Awaiting answer"

            # Add dictionary item to list
            entry.update({'id': questionID, 'subject': questionSubject, 'answered': questionAnswered, 'bookmarked': isBookmarked})
            results.append(entry)

        # If no questions found, display notification. Otherwise, do nothing
        if not results:
            status = "No questions found!"
        else:
            status = ""

        return render(request, "parlio/question.html", {
            "results": results,
            "status": status
        })

    #TODO: delete, redundant?
    else:
        return render(request, "parlio/question.html")


### User handling routes ###

# Log user in
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "parlio/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "parlio/login.html")


# Log user out
@login_required(redirect_field_name='my_redirect_field')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register a new user
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "parlio/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "parlio/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "parlio/register.html")


### API routes: ###


@login_required(redirect_field_name='my_redirect_field')
def onWatchlist(request, questionId):

    # Check if question on watchlist
    watchlistQuestions = Question.objects.filter(watchlistBy=request.user).values_list('uniqueId', flat=True)

    if questionId in watchlistQuestions:
        onWatchlist = True
    else:
        onWatchlist = False

    return JsonResponse({"message": "Question checked", "questionPresent": onWatchlist}, status=201)


# Adds / removes question from watchlist
@login_required(redirect_field_name='my_redirect_field')
def notifyMe(request, questionId):

    # Get user TODO: redundant, can use request.id?
    user = User.objects.filter(id=request.user.id).first()

    # Check if user has question on watchlist
    watchlistQuestions = Question.objects.filter(watchlistBy=request.user).values_list('uniqueId', flat=True)

    print("Debug - questions on watchlist: ", watchlistQuestions)

    # If question on watchlist, remove
    if questionId in watchlistQuestions:

        question = Question.objects.filter(uniqueId=questionId).first()
        user.watchlistQuestion.remove(question)
        notifyMeOutcome = "Question removed from watchlist"

    # If question NOT on watchlist, add
    else:

        question = Question(uniqueId=questionId)
        question.save()
        user.watchlistQuestion.add(question)

        notifyMeOutcome = "Question added to watchlist"

    return JsonResponse({"message": notifyMeOutcome}, status=201)


# Adds / removes question from bookmarks
@login_required(redirect_field_name='my_redirect_field')
def bookmark(request, questionId):

    user = User.objects.get(id=request.user.id)

    if user.bookmarkQuestion.filter(uniqueId=questionId).exists():

        # TODO issue because of get??
        bookmarkedQuestion = Question.objects.get(uniqueId=questionId)
        user.bookmarkQuestion.remove(bookmarkedQuestion)

        return JsonResponse({"message": "Question removed from bookmarks", "star": False}, status=201)

    else:

        newBookmark = Question(uniqueId=questionId)
        newBookmark.save()

        request.user.bookmarkQuestion.add(newBookmark)

        return JsonResponse({"message": "New question added from bookmarks", "star": True}, status=201)


# Check if watchlist question answered. If so, remove from watchlist and create notification
@login_required(redirect_field_name='my_redirect_field')
def notifyCheck(request):

    watchlistQuestions = Question.objects.filter(
        watchlistBy=request.user).values_list('uniqueId', flat=True)
    print("Debug: Questions on watchlist: ", watchlistQuestions)

    # Check if any question on watchlist has been answered
    for question in watchlistQuestions:

        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions/" + \
            str(question) + "?expandMember=true"
        response = requests.get(url)
        jsonResponse = response.json()

        dateAnswered = jsonResponse['value']['dateAnswered']

        if (dateAnswered is None):
            print("Debug: Question remains unanswered...")

        else:
            print("Debug: Question has now been answered!")

            # Create new notification TODO ISSUE WITH GET
            question = Question.objects.get(uniqueId=question)
            notification = Notification(question=question, user=request.user)
            notification.save()

            # Remove question from watchlist
            user = User.objects.get(id=request.user.id)
            user.watchlistQuestion.remove(question)

    # Count notifications
    notifications = Notification.objects.filter(
        is_read=False, user=request.user).count()
    print("Debug: User has", notifications, "notifications.")

    return JsonResponse({"message": "Question checked", "notifications": notifications}, status=201)


# Check if Commons or Lords are sitting
def isSitting(request):

    # Commons API route
    commonsUrl = "https://now-api.parliament.uk/api/Message/message/CommonsMain/current"
    response = requests.get(commonsUrl)
    jsonResponse = response.json()
    # print("Debug: Commons annunciator route: ", jsonResponse)

    # If Commons not sitting or sitting
    if jsonResponse['slides'][0]['type'] == 'BlankSlide':
        commonsSitting = "Not sitting"
        print("Debug: the House of Commons is NOT sitting")

    else:
        commonsSitting = "Sitting"
        print("Debug: the House of Commons is sitting")

    # Lords API route
    lordsUrl = "https://now-api.parliament.uk/api/Message/message/LordsMain/current"
    response = requests.get(lordsUrl)
    jsonResponse = response.json()
    # print("Debug: Lords annunciator route: ", jsonResponse)

    # If Commons not sitting or sitting
    if jsonResponse['slides'][0]['type'] == 'BlankSlide':
        lordsSitting = "Not sitting"
        print("Debug: the House of Lords is NOT sitting")

    else:
        lordsSitting = "Sitting"
        print("Debug: the House of Lords is sitting")

    return JsonResponse({"message": "Sitting checked", "commonsSitting": commonsSitting, "lordsSitting": lordsSitting}, status=201)


def dismissNotification(request, questionId):
    print("DEBUG: dismissNotification -", questionId)

    # Get question to filter notifications by
    question = Question.objects.get(uniqueId=questionId)

    # Get notification
    notification = Notification.objects.get(question=question)
    notification.delete()

    request.user.watchlistQuestion.remove(question)

    return JsonResponse({"message": "Notification dismissed"}, status=201)