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
                    ConferenceRoomParticipants,
                    ConferenceRoomRecording)
import subprocess
from django.conf import settings
from django.core.files import File
import os

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
    conferenceroom = ConferenceRoom.objects.filter(room_key = roomkey)
    is_participant = ConferenceRoomParticipants.objects.filter(conferenceroom=conferenceroom,user=request.user)
    if not is_participant:
        return HttpResponse("Your are not Conference Participant")
    # if is_participant[0].role.role !='OWN' and conferenceroom != 'RUN':
    #     return HttpResponse("Conference is not started yet.")
    return render(request, 'videochatapp/videochat.html',{'roomkey':roomkey})

@login_required(login_url='/login/')
def create_videochat_room(request):
    """
    Function to create videochat room
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('data'))
            start_time = data['starttime']
            start_time = datetime.datetime.strptime(start_time,"%Y/%m/%d %H:%M")
            start_time = pytz.utc.localize(start_time)
            end_time = data['endtime']
            end_time = datetime.datetime.strptime(end_time,"%Y/%m/%d %H:%M")
            end_time = pytz.utc.localize(end_time)
            del data['starttime']
            del data['endtime']
            conf_title = data['title']
            if not conf_title:
                conf_title = "Default title"
            key_value = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
            conference_room = ConferenceRoom(room_key = key_value,
                                            title = conf_title,
                                            owner = request.user,
                                            start_time = start_time,
                                            end_time = end_time
                                            )
            conference_room.save()

            for user_id,user_dict in data.iteritems():
                user = User.objects.get(id = user_id)
                user_role = user_dict['role']
                user_role = ConferenceRoomRoles.objects.get(role = user_role)
                if user and user_role:
                    conference_room_participants = ConferenceRoomParticipants(
                                                    conferenceroom = conference_room,
                                                    user = user,
                                                    role = user_role
                                                )
                    conference_room_participants.save()

            owner_role = ConferenceRoomRoles.objects.get(role='OWN')        
            conference_room_participants = ConferenceRoomParticipants(
                                                    conferenceroom = conference_room,
                                                    user = request.user,
                                                    role = owner_role
                                            )
            conference_room_participants.save()
            response = {"message":"Conference room is created successfully."}
            return HttpResponse(json.dumps(response), 
                            content_type='application/json')
        except Exception as e:
            response = {"message":"oops something went wrong..."}
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
def list_conferences(request):
    """ 
        Function to list all conferences of requested user 
    """
    conference_context = {}
    conference_participants= ConferenceRoomParticipants.objects.filter(user=request.user)
    data_list = list()
    for conference_participant in conference_participants:
        conference_context={
            "conference":conference_participant.conferenceroom,
            "start_time":conference_participant.conferenceroom.start_time,
            "end_time":conference_participant.conferenceroom.end_time,
            "no_participants":ConferenceRoomParticipants.objects.filter(conferenceroom=conference_participant.conferenceroom).count(),
            "role":conference_participant.role ,
        }
        data_list.append(conference_context)
    return render(request, 'videochatapp/list_conferences.html',{"data_list":data_list})    


def record_conference(request):
    """
    Function to record video confenrence and conver to mp4
    """
    if request.method == 'POST':
        try:
            input_file = request.FILES.get('file', None)
            room_key = request.POST.get('room', None)
            user = request.user
        except:
            return HttpResponse(400)
        try:
            input_file_name = str(request.FILES['file'].name)
            conferenceroom = ConferenceRoom.objects.get(room_key=room_key)
        except:
            return HttpResponse(404)
        try:
            conferenceroomrecording_obj = ConferenceRoomRecording.objects.create(
                                            name=input_file_name,
                                            user=user,
                                            conferenceroom=conferenceroom,
                                            video_file=input_file
                                        )
        except:
            return HttpResponse(400)
        try:
            output_file_name = conferenceroomrecording_obj.video_file.name.split(".")[0]
            input_file = settings.MEDIA_ROOT+'/'+conferenceroomrecording_obj.video_file.name
            outputfile = settings.MEDIA_ROOT+'/'+output_file_name+'.mp4'
            subprocess.call(['ffmpeg','-i',input_file,'-strict',
                            'experimental',outputfile])
            recorded_file_webm_path = conferenceroomrecording_obj.video_file.path
        except:
            conferenceroomrecording_obj.delete()
            return HttpResponse(400)
        try:
            fileopen = open(outputfile, 'rb')
            conferenceroomrecording_obj.video_file = File(fileopen)
            conferenceroomrecording_obj.save()
            os.remove(recorded_file_webm_path)
            os.remove(outputfile)
        except:
            return HttpResponse(400)
        return HttpResponse(200)
