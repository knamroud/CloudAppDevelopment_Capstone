from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import logging
import os
from .forms import ReviewForm
from .models import CarModel
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
        dealerships = get_dealers_from_cf(url)
        return render(request, 'djangoapp/index.html', {'dealerships': dealerships})

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = os.environ["GET_REVIEW"]
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        dealer = get_dealer_by_id(os.environ["GET_DEALERSHIP"], dealer_id)
        return render(request, 'djangoapp/dealer_details.html', {'reviews': reviews, 'dealer': dealer, 'MEDIA_URL': settings.MEDIA_URL})

@login_required
def add_review(request, dealer_id):
    if request.method == "GET":
        return render(request, 'djangoapp/add_review.html', {'dealer_id': dealer_id,'form': ReviewForm(dealership=dealer_id, name=request.user.username)})
    elif request.method == "POST":
        data = request.POST.copy()
        data["dealership"] = dealer_id
        data["name"] = request.user.username
        form = ReviewForm(data, dealership=dealer_id, name=request.user.username)
        url = os.environ['ADD_REVIEW']
        if form.is_valid():
            print(form.cleaned_data)
            data = form.cleaned_data.copy()
            data["purchase_date"] = data["purchase_date"].strftime("%m/%d/%Y")
            car = CarModel.objects.get(pk=data["car"])
            data["car_make"] = car.make.name
            data["car_model"] = car.name
            data["car_year"] = car.year.year
            print(post_request(url, {"review":data}))
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            print(form.errors)
            return render(request, 'djangoapp/add_review.html', {'dealer_id': dealer_id, 'form': form})