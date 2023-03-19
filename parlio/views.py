from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

from .models import *
import requests
import json
from django.http import JsonResponse

# Create your views here.

def index(request):
    return render(request, "parlio/index.html", {
            "message": "Hello, World!"
        })


def annunciator(request):
    return render(request, "parlio/annunciator.html")


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
# TODO @login_required(redirect_field_name='my_redirect_field')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register a new user
def register(request):
    if request.method == "POST":
        username = request.POST["usernme"]
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

# Test route for fetch functionality
def fetch(request):
    return render(request, "parlio/fetch.html")




def question(request):

    if request.method == "GET":
        return render(request, "parlio/question.html")

    # Check if method is POST
    elif request.method == "POST":

        # Take in the data the user submitted and save it as form
        questionId = request.POST["questionId"]

        #print(questionId)

        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions?uIN=" + questionId
        #print(url)

        results = []

        response = requests.get(url)
        jsonResponse = response.json()
        questions = jsonResponse["results"]

        # Check if user has question bookmarked
        bookmarkedQuestions = Question.objects.filter(bookmarkBy=request.user).values_list('uniqueId', flat=True)
        #print("Bookmarked questions:", bookmarkedQuestions)

        # Check if user has question on watchlist
        #watchlistQuestions = Question.objects.filter(watchlistBy=request.user).values_list('uniqueId', flat=True)
        #print("Watchlisted questions:", watchlistQuestions)
 
        for question in questions:
            
            entry = {}

            questionID = int(question['value']['id'])
            if questionID in bookmarkedQuestions:
                print("It's a match!")
                isBookmarked = True
            else:
                print("It's not a match")
                isBookmarked = False

            #if questionID in watchlistQuestions:
            #    print("It's a match!")
            #    isWatchlisted = True
            #else:
            #    print("It's not a match")
            #    isWatchlisted = False

            questionSubject = question['value']['heading']
            
            try:
                questionAnswered = question['value']['dateAnswered'][0:10]
            except:
                questionAnswered = "Awaiting answer"
            

            entry.update({'id':questionID, 'subject':questionSubject, 'answered':questionAnswered, 'bookmarked': isBookmarked})
            results.append(entry)
            

            print(results)

        if not results:
            status = "No questions found!"
        else:
            status = ""

      
       
        return render(request, "parlio/question.html", {
                "results": results, 
                "questionId": questionId,
                "status": status
            })

    else:

        return render(request, "parlio/question.html")




def onWatchlist(request, questionId):
        
    # Check if user has question on watchlist
    watchlistQuestions = Question.objects.filter(watchlistBy=request.user).values_list('uniqueId', flat=True)

    print(watchlistQuestions)
    print(questionId)
    
    if questionId in watchlistQuestions:
        
        present = True    
        print("yes")
    else:
        present = False
        print("no")

    return JsonResponse({"message": "Question checked", "questionPresent": present}, status=201)




def notifyMe(request, questionId):

    # Check if user has question on watchlist
    watchlistQuestions = Question.objects.filter(watchlistBy=request.user).values_list('uniqueId', flat=True)

    # Debug
    print(watchlistQuestions)
    
    user = User.objects.filter(id=request.user.id).first()
        
    if questionId in watchlistQuestions:
        
        question = Question.objects.filter(uniqueId=questionId).first()
        
        user.watchlistQuestion.remove(question)
        message = "Question removed from your watchlist"

    else:
        
        question = Question(uniqueId=questionId)
        question.save()
        user.watchlistQuestion.add(question)

        message = "Question added to your watchlist"

    return JsonResponse({"message": message}, status=201)


def bookmark(request, questionId):
    print("You are here: ", questionId)
    pass




# Check if watchlist question answered. If so, remove from watchlist and create notification
def notifyCheck(request):

    watchlistQuestions = Question.objects.filter(watchlistBy=request.user).values_list('uniqueId', flat=True)
    
    if not watchlistQuestions:
        print("No questions on watchlist, aborting now...")

        return JsonResponse({"message": "Question checked", "newNotification": False}, status=201)

    
    print("Questions on watchlist: ", watchlistQuestions)

    for question in watchlistQuestions:
        
        # Test url: url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions/1603046?expandMember=true"
        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions/" + str(question) + "?expandMember=true"
        print(url)

        response = requests.get(url)
        jsonResponse = response.json()
        print(jsonResponse)

        dateAnswered = jsonResponse['value']['dateAnswered']
        
        if (dateAnswered is None):
            print("Question remains unanswered")

        else:
            print("Question has now been answered")

            # Create notification
            question = Question.objects.get(uniqueId=question)
            notification = Notification(question=question, user=request.user)
            notification.save()

            # Remove from watchlist
            user = User.objects.get(id=request.user.id)
            user.watchlistQuestion.remove(question)

    notifications = Notification.objects.filter(is_read=False, user=request.user)
    
    if notifications:
        newNotification = True
    else:
        newNotification = False

    return JsonResponse({"message": "Question checked", "newNotification": newNotification}, status=201)


def isSitting(request):

    commonsUrl = "https://now-api.parliament.uk/api/Message/message/CommonsMain/current"
    lordsUrl = "https://now-api.parliament.uk/api/Message/message/LordsMain/current"

    response = requests.get(commonsUrl)
    jsonResponse = response.json()
    print(jsonResponse)

    if jsonResponse['slides'][0]['type'] == 'BlankSlide':
        commonsSitting = False
        # print("The House of Commons is NOT sitting")

    else:
        commonsSitting = True
        # print("The House of Commons is sitting")
        

    response = requests.get(lordsUrl)
    jsonResponse = response.json()
    print(jsonResponse)

    if jsonResponse['slides'][0]['type'] == 'BlankSlide':
        lordsSitting = False
        # print("The House of Lords is NOT sitting")

    else:
        #print("The House of Lords is sitting")
        lordsSitting = True

    print("commonsSitting:", commonsSitting, "lordsSitting:", lordsSitting)

    return JsonResponse({"message": "Sitting checked", "commonsSitting": commonsSitting, "lordsSitting": lordsSitting }, status=201)





