from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ConferenceRoom, ConferenceRoomRoles, ConferenceRoomParticipants
# Create your views here.
def home(request):
    """
    Function to show home page
    """
    return render(request, 'videochatapp/home.html')

@login_required(login_url='/login/')
def join_videochat(request, roomkey):
    """
    Function to show join videochat room
    """
    return render(request, 'videochatapp/videochat.html',{'roomkey':roomkey})

@login_required(login_url='/login/')
def create_videochat_room(request):
    """
    Function to create videochat room
    """
    if request.method == 'POST':
        pass
    else:
        try:
            # Get all participants users excluding current user
            participants = User.objects.all().exclude(id=request.user.id)
        except:
            raise

        # Get all user roles
        participants_roles = ConferenceRoomRoles.objects.all()
        context = {
            'participants': participants,
            'participants_roles' : participants_roles,
        }
        return render(request, 'videochatapp/create_videochat_room.html',context)