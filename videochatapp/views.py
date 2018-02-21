import uuid
import json
import random
import string
import datetime
import pytz
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from .models import (ConferenceRoom,
                    ConferenceRoomRoles, 
                    ConferenceRoomParticipants)

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
        data = json.loads(request.POST.get('data'))
        start_time = data['starttime']
        start_time = datetime.datetime.strptime(start_time,"%Y/%m/%d %H:%M")
        start_time = pytz.utc.localize(start_time)
        end_time = data['endtime']
        end_time = datetime.datetime.strptime(end_time,"%Y/%m/%d %H:%M")
        end_time = pytz.utc.localize(end_time)
        del data['starttime']
        del data['endtime']
        key_value = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
        conference_room = ConferenceRoom(room_key = key_value,
                                        owner = request.user,
                                        start_time = start_time,
                                        end_time = end_time
                                        )
        conference_room.save()

        for user_id,user_dict in data.iteritems():
            user = User.objects.filter(id = user_id)
            user_role = user_dict['role']
            user_role = ConferenceRoomRoles.objects.filter(role = user_role)
            if user and user_role:
                conference_room_participants = ConferenceRoomParticipants(
                                                conferenceroom = conference_room,
                                                user = user[0],
                                                role = user_role[0]
                                            )
                conference_room_participants.save()

        owner_role = ConferenceRoomRoles.objects.filter(role='OWN')        
        conference_room_participants = ConferenceRoomParticipants(
                                                conferenceroom = conference_room,
                                                user = request.user,
                                                role = owner_role[0]
                                        )
        conference_room_participants.save()
        response = {"message":"Conference room is created successfully."}
        return HttpResponse(json.dumps(response), 
                        content_type='application/json')
    else:
        try:
            # Get all participants users excluding current user
            participants = User.objects.all().exclude(id=request.user.id)
        except:
            raise
        # Get all user roles
        participants_roles = ConferenceRoomRoles.objects.all().exclude(role='OWN')
        context = {
            'participants': participants,
            'participants_roles' : participants_roles,
        }
        return render(request, 'videochatapp/create_videochat_room.html',context)

@login_required(login_url='/login/')
def list_beta(request):
    conferences = ConferenceRoom.objects.filter(owner = request.user).order_by('start_time')
    conferences_list = {}
    for conference in conferences:
        no_count = ConferenceRoomParticipants.objects.filter(conferenceroom=conference).count()
        
    context = {"conferences":conferences}
    return render(request, 'videochatapp/list_beta.html',context)    


