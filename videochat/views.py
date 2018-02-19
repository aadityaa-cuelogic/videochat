from django.shortcuts import render
from django.contrib.auth.models import User 
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.contrib.auth.hashers import make_password


def register(request):

    if request.method == 'POST':
        user = User.objects.filter(username =request.POST['username'])

        if user:
            messages.error(request,'User Already Exist.')
            return HttpResponseRedirect('/register',{"messages":messages})

        password = make_password(request.POST['password'])

        user  = User(username=request.POST['username'],
                    email = request.POST['email'],
                    password = password,
                    first_name = request.POST['firstname'],
                    last_name = request.POST['lastname']
                )

        user.save()

        messages.success(request, 'User Register Successfully.')
        
        return HttpResponseRedirect('/login',{"messages":messages})

    return render(request,'registration/register.html')
