from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def home(request):
	return render(request, 'videochatapp/home.html')

@login_required(login_url='/login/')
def videochat(request,roomkey):
	return render(request, 'videochatapp/videochat.html',{'roomkey':roomkey})

@login_required(login_url='/login/')
def create_conference(request):

	users = User.objects.all().exclude(id=request.user.id)

	if users:
		return render(request, 'videochatapp/create_conference.html',{"users":users})	

	