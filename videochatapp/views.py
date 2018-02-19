from django.shortcuts import render
from django.contrib.auth.models import User 
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.contrib.auth.hashers import make_password



# Create your views here.
def home(request):
	return render(request, 'videochatapp/home.html')


def videochat(request):
	return render(request, 'videochatapp/videochat.html')
