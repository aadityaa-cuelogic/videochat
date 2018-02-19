from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
	return render(request, 'videochatapp/home.html')

@login_required(login_url='/login/')
def videochat(request,roomkey):
	return render(request, 'videochatapp/videochat.html',{'roomkey':roomkey})
