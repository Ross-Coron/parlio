from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

from .models import *
import requests
import json

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

    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        questionId = request.POST["questionId"]

        print(questionId)

        url = "https://writtenquestions-api.parliament.uk/api/writtenquestions/questions?uIN=" + questionId
        print(url)

        results = []

        response = requests.get(url)
        jsonResponse = response.json()
        answer = jsonResponse["results"]

        
        for foo in answer:
            
            entry = {}

            a = foo['value']['id']
            b = foo['value']['heading']
            c = foo['value']['dateAnswered'][0:10]

            print(c)
            print(type(c))
            
            entry.update({'id':a, 'subject':b, 'answered':c})
            

            results.append(entry)
            

        print(results)

      
       
        return render(request, "parlio/question.html", {
                "results": results
            })

    else:

        return render(request, "parlio/question.html")
