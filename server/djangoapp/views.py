from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import os
from .restapis import post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def about(request):
    return render(request, 'djangoapp/about.html')

def contact(request):
    return render(request, 'djangoapp/contact.html')

def login_request(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("djangoapp:index")
    else:
        messages.error(request, "Invalid username or password.")
        return redirect("djangoapp:index")

def logout_request(request):
    logout(request)
    return redirect("djangoapp:index")

def registration_request(request):
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html')
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']

    user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
    user.save()
    login(request, user)
    return redirect("djangoapp:index")

def get_dealerships(request):
    if request.method == "GET":
        url = os.environ["GET_DEALERSHIP"]
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        return render(request, 'djangoapp/index.html', {'dealerships': dealerships})

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = os.environ["GET_REVIEW"]
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        review_content = '\n'.join([f"{review.name}: {review.review} - {review.sentiment}" for review in reviews])
        return HttpResponse(review_content)
              
@login_required
def add_review(request, dealer_id):
    url = os.environ['ADD_REVIEW']
    review = {} 
    review["time"] = datetime.utcnow().isoformat()
    review["dealership"] = dealer_id
    review["review"] = request.POST.get("content")
    review["purchase"] = request.POST.get("purchasecheck")
    review["purchase_date"] = request.POST.get("purchasedate")
    review["car_make"] = request.POST.get("carmake")
    review["car_model"] = request.POST.get("carmodel")
    review["car_year"] = request.POST.get("caryear")
    review["name"] = request.user.username
    json_payload = {}
    json_payload["review"] = review
    return post_request(url, json_payload, dealerId=dealer_id)