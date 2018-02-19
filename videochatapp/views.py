from django.shortcuts import render

# Create your views here.
def home(request):
	return render(request, 'videochatapp/home.html')


def videochat(request):
	return render(request, 'videochatapp/videochat.html')
