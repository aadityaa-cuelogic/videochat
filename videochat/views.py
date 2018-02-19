from django.shortcuts import render
from django.contrib.auth.models import User 
from django.contrib import messages
from django.http import HttpResponseRedirect


def register(request):

    if request.method == 'POST':
        user = User.objects.filter(username =request.POST['username'])
        if user:
            messages.error(request,'User Already Exist.')
            return HttpResponseRedirect('/register',{"messages":messages})
        password = make_password(request.POST.get('password'))
        user  = User(username=request.POST.get('username'),
                    email = request.POST.get('email'),
                    password = password,
                    first_name = request.POST.get('firstname'),
                    last_name = request.POST.get('lastname')
                )
        user.save()
        messages.success(request, 'User Register Successfully.')
        return HttpResponseRedirect('/login',{"messages":messages})
    return render(request,'registration/register.html')
