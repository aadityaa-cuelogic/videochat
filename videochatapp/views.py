import json
import random
import string
import datetime
import pytz
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from .models import (ConferenceRoom, ConferenceRoomRoles,
                    ConferenceRoomPrivileges, ConferenceRoomRolePrivilegeMap,
                    ConferenceRoomParticipants, ConferenceRoomRecording)
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
    conferenceroom = ConferenceRoom.objects.filter(room_key=roomkey)
    is_participant = ConferenceRoomParticipants.objects.filter(conferenceroom=conferenceroom,user=request.user)
    if not is_participant:
        return HttpResponse("Your are not Conference Participant")
    if is_participant[0].role.role == 'OWN' and conferenceroom[0].status != 'RUN':
        conferenceroom[0].status='RUN'
        conferenceroom[0].save()               
    if is_participant[0].role.role !='OWN' and conferenceroom[0].status != 'RUN':
        return HttpResponse("Conference is not started yet.")
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
            conf_title = data['title']
            del data['starttime']
            del data['endtime']
            del data['title']
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
                special_privilege = ','.join(str(e) for e in user_dict['special_privilege'])
                user_role = ConferenceRoomRoles.objects.get(role = user_role)
                if user and user_role:
                    conference_room_participants = ConferenceRoomParticipants(
                                                    conferenceroom=conference_room,
                                                    user=user,
                                                    role=user_role,
                                                    special_privilege=special_privilege
                                                )
                    conference_room_participants.save()

            owner_role = ConferenceRoomRoles.objects.get(role='OWN')        
            conference_room_participants = ConferenceRoomParticipants(
                                                    conferenceroom=conference_room,
                                                    user=request.user,
                                                    role=owner_role
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
        try:
            # Get all user roles
            participants_roles = ConferenceRoomRoles.objects.all().exclude(role='OWN')
            participants_privileges = ConferenceRoomPrivileges.objects.all()
            participants_role_privilege_map = ConferenceRoomRolePrivilegeMap.objects.all()
            new_participants_roles = []
        except:
            raise

        for role in participants_roles:
            default_privileges = []
            temp_default_privileges = role.conferenceroomroleprivilegemap_set.all()
            for privilege in temp_default_privileges:
                default_privileges.append(str(privilege.privilege.privilege_type))
            role.default_privileges = default_privileges
            new_participants_roles.append(role)
            

        context = {
            'participants': participants,
            'participants_roles' : new_participants_roles,
            'participants_privileges' : participants_privileges,
            'participants_role_privilege_map' : participants_role_privilege_map
        }

        return render(request, 'videochatapp/create_videochat_room.html',context)

@login_required(login_url='/login/')
def list_videochat(request):
    """ 
    Function to list all conferences of requested user 
    """
    conference_context = {}
    conference_participants= ConferenceRoomParticipants.objects.filter(user=request.user)
    data_list = list()
    edit_btn_privilege = ['remove_participant', 'block_participant',
                         'add_participant', 'participant_management',
                         'event_management']
    cancel_btn_privilege = ['event_management']
    for conference_participant in conference_participants:
        if conference_participant.special_privilege:
            special_privilege = conference_participant.special_privilege.split(",")
        else:
            special_privilege = []
        if conference_participant.role.role in ['OWN'] or [i for i in special_privilege if i in edit_btn_privilege]:
            show_edit_btn = True
        else:
            show_edit_btn = False

        if conference_participant.role.role in ['OWN'] or [i for i in special_privilege if i in cancel_btn_privilege]:
            show_cancel_btn = True
        else:
            show_cancel_btn = False

        conference_context={
            "conference":conference_participant.conferenceroom,
            "start_time":conference_participant.conferenceroom.start_time,
            "end_time":conference_participant.conferenceroom.end_time,
            "no_participants":ConferenceRoomParticipants.objects.filter(conferenceroom=conference_participant.conferenceroom).count(),
            "role":conference_participant.role,
            "special_privilege":special_privilege,
            "show_edit_btn":show_edit_btn,
            "show_cancel_btn":show_cancel_btn
        }
        data_list.append(conference_context)
    return render(request, 'videochatapp/list_conferences.html',{"data_list":data_list})    

@login_required(login_url='/login/')
def record_videochat(request):
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

@login_required(login_url='/login/')
def edit_videochat_conference(request, conferenceroomid):
    if request.method == 'POST':
        # import pdb;pdb.set_trace()
        data = json.loads(request.POST.get('data'))
        conferenceroomid = data['confereceroomid']
        del data['confereceroomid']
        if conferenceroomid:
            try:
                conferenceroom = ConferenceRoom.objects.get(id=conferenceroomid)
            except:
                return HttpResponse(404)
            # user is owner of event
            if conferenceroom.owner.id == request.user.id:
                try:
                    start_time = data['starttime']
                    start_time = datetime.datetime.strptime(start_time,"%Y/%m/%d %H:%M")
                    start_time = pytz.utc.localize(start_time)
                    end_time = data['endtime']
                    end_time = datetime.datetime.strptime(end_time,"%Y/%m/%d %H:%M")
                    end_time = pytz.utc.localize(end_time)
                    conf_title = data['title']
                    del data['starttime']
                    del data['endtime']
                    del data['title']
                    if conf_title:
                        conferenceroom.title = conf_title
                    conferenceroom.start_time = start_time
                    conferenceroom.end_time = end_time
                    conferenceroom.save()
                except:
                    return HttpResponse(400)
                try:
                    added_users = []
                    for user_id,user_dict in data.iteritems():
                        user = User.objects.get(id=user_id)
                        added_users.append(user)

                    print added_users
                    ConferenceRoomParticipants.objects.filter(conferenceroom=conferenceroom).exclude(user__in=added_users).delete()
                except:
                    return HttpResponse(400)
                try:
                    for user_id,user_dict in data.iteritems():
                        user = User.objects.get(id=user_id)
                        user_role = user_dict['role']
                        special_privilege = ','.join(str(e) for e in user_dict['special_privilege'])
                        user_role = ConferenceRoomRoles.objects.get(role=user_role)
                        if user and user_role:
                            try:
                                conference_room_participants = ConferenceRoomParticipants.objects.get(
                                                                conferenceroom=conferenceroom,
                                                                user=user)
                                conference_room_participants.role=user_role
                                conference_room_participants.special_privilege=special_privilege
                                conference_room_participants.save()
                            except ConferenceRoomParticipants.DoesNotExist:
                                conference_room_participants = ConferenceRoomParticipants.objects.create(
                                                                conferenceroom=conferenceroom,
                                                                user=user,
                                                                role=user_role,
                                                                special_privilege=special_privilege
                                                                )
                except:
                    return HttpResponse(400)
                try:
                    owner_role = ConferenceRoomRoles.objects.get(role='OWN')        
                    conference_room_participants = ConferenceRoomParticipants(
                                                            conferenceroom=conferenceroom,
                                                            user=request.user,
                                                            role=owner_role
                                                    )
                    conference_room_participants.save()
                except:
                    return HttpResponse(400)
            elif data:
                try:
                    current_user = ConferenceRoomParticipants.objects.get(conferenceroom=conferenceroom,
                                                        user=request.user)
                    if current_user.special_privilege:
                        current_user_privileges = current_user.special_privilege.split(",")
                    else:
                        current_user_privileges = []
                except:
                    return HttpResponse(400)
                try:
                    # get current privilege wrt Role
                    for prv in current_user.role.conferenceroomroleprivilegemap_set.all():
                        current_user_privileges.append(prv.privilege.privilege_type)
                except:
                    return HttpResponse(400)
                try:
                    user_add_remove_privilege = ['remove_participant',
                                                'add_participant',
                                                'participant_management']

                    event_schedule_privilege = ['event_management']
                    if [i for i in current_user_privileges if i in event_schedule_privilege]:
                        try:
                            start_time = data['starttime']
                            start_time = datetime.datetime.strptime(start_time,"%Y/%m/%d %H:%M")
                            start_time = pytz.utc.localize(start_time)
                            end_time = data['endtime']
                            end_time = datetime.datetime.strptime(end_time,"%Y/%m/%d %H:%M")
                            end_time = pytz.utc.localize(end_time)
                            conf_title = data['title']
                            del data['starttime']
                            del data['endtime']
                            del data['title']
                            if conf_title:
                                conferenceroom.title = conf_title
                            conferenceroom.start_time = start_time
                            conferenceroom.end_time = end_time
                            conferenceroom.save()
                        except:
                            return HttpResponse(403)

                    if [i for i in current_user_privileges if i in user_add_remove_privilege]:
                        try:
                            added_users = []
                            for user_id,user_dict in data.iteritems():
                                user = User.objects.get(id=user_id)
                                added_users.append(user)
                            # add current user in selected users
                            added_users.append(request.user)
                            # add owner in selected users
                            added_users.append(conferenceroom.owner)
                            ConferenceRoomParticipants.objects.filter(conferenceroom=conferenceroom).exclude(user__in=added_users).delete()
                        except:
                            return HttpResponse(400)
                        try:
                            for user_id,user_dict in data.iteritems():
                                user = User.objects.get(id=user_id)
                                user_role = user_dict['role']
                                if 'special_privilege' in user_dict:
                                    special_privilege = ','.join(str(e) for e in user_dict['special_privilege'])
                                user_role = ConferenceRoomRoles.objects.get(role=user_role)
                                if user and user_role:
                                    try:
                                        conference_room_participants = ConferenceRoomParticipants.objects.get(
                                                                        conferenceroom=conferenceroom,
                                                                        user=user)
                                        conference_room_participants.role=user_role
                                        if 'participant_management' in current_user_privileges:
                                            conference_room_participants.special_privilege=special_privilege
                                        conference_room_participants.save()
                                    except ConferenceRoomParticipants.DoesNotExist:
                                        conference_room_participants = ConferenceRoomParticipants.objects.create(
                                                                        conferenceroom=conferenceroom,
                                                                        user=user,
                                                                        role=user_role,
                                                                        special_privilege=special_privilege
                                                                        )
                        except:
                            return HttpResponse(400)
                except:
                    return HttpResponse(401)
            else:
                return HttpResponse(404)
        else:
            return HttpResponse(404)
        return HttpResponse(200)
    elif request.method == 'GET':
        if conferenceroomid:
            try:
                conferenceroom = ConferenceRoom.objects.get(id=conferenceroomid)
            except:
                return HttpResponseRedirect('/')
            try:
                if conferenceroom.owner.id == request.user.id:
                    # Get all users excluding current user
                    participants = User.objects.all().exclude(id=request.user.id)
                else:
                    participants = User.objects.all().exclude(id__in=[request.user.id, conferenceroom.owner.id])
            except:
                return HttpResponseRedirect('/')
            try:
                # get conferenceroom participants
                conference_room_participants = ConferenceRoomParticipants.objects.filter(conferenceroom=conferenceroom)
            except:
                return HttpResponseRedirect('/')

            new_participants_obj = []
            current_user_privileges = []

            for participant in participants:
                for cnf_p in conference_room_participants:
                    if participant.id == cnf_p.user.id:
                        participant.role = cnf_p.role.role
                        if cnf_p.special_privilege:
                            special_privilege = cnf_p.special_privilege.split(",")
                        else:
                            special_privilege = []
                        participant.special_privilege = special_privilege
                    elif cnf_p.user.id == request.user.id:
                            if cnf_p.special_privilege:
                                current_user_privileges = cnf_p.special_privilege.split(",")
                            else:
                                current_user_privileges = []
                    try:
                        # get current privilege wrt Role
                        for prv in cnf_p.role.conferenceroomroleprivilegemap_set.all():
                            current_user_privileges.append(prv.privilege.privilege_type)
                    except:
                        return HttpResponseRedirect('/')
                new_participants_obj.append(participant)
            event_title_privilege = False
            user_listing_privilege = False
            user_add_remove_privilege = False
            manage_privilege_for_user_privilege = False
            event_schedule_privilege = False
            if conferenceroom.owner.id == request.user.id:
                event_title_privilege = True
                user_listing_privilege = True
                user_add_remove_privilege = True
                manage_privilege_for_user_privilege = True
                event_schedule_privilege = True
            else:
                if 'participant_management' in current_user_privileges:
                    user_listing_privilege = True
                    user_add_remove_privilege = True
                    manage_privilege_for_user_privilege = True
                if 'add_participant' in current_user_privileges:
                    user_listing_privilege = True
                    user_add_remove_privilege = True
                if 'remove_participant' in current_user_privileges:
                    user_listing_privilege = True
                    user_add_remove_privilege = True
                if 'event_management' in current_user_privileges:
                    event_schedule_privilege = True
            # Get all user roles
            participants_roles = ConferenceRoomRoles.objects.all().exclude(role='OWN')
            participants_privileges = ConferenceRoomPrivileges.objects.all()
            participants_role_privilege_map = ConferenceRoomRolePrivilegeMap.objects.all()
            new_participants_roles = []
            for role in participants_roles:
                default_privileges = []
                temp_default_privileges = role.conferenceroomroleprivilegemap_set.all()
                for privilege in temp_default_privileges:
                    default_privileges.append(str(privilege.privilege.privilege_type))
                role.default_privileges = default_privileges
                new_participants_roles.append(role)
            context = {
                'conferenceroom' : conferenceroom,
                'participants': new_participants_obj,
                'participants_roles' : new_participants_roles,
                'participants_privileges' : participants_privileges,
                'participants_role_privilege_map' : participants_role_privilege_map,
                'event_title_privilege':event_title_privilege,
                'user_listing_privilege':user_listing_privilege,
                'user_add_remove_privilege':user_add_remove_privilege,
                'manage_privilege_for_user_privilege':manage_privilege_for_user_privilege,
                'event_schedule_privilege':event_schedule_privilege
            }
            return render(request, 'videochatapp/edit_videochat_room.html',context)
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/login/')
def cancel_videochat(request):
    if request.method == 'POST':
        conf_room_id = request.POST.get('conf_room_id', 0)
        user = request.user
        # get conference
        try:
            conferenceroom = ConferenceRoom.objects.get(id=conf_room_id)
        except:
            return HttpResponse(404)
        # get current user from participants
        try:
            conferenceroom_user = ConferenceRoomParticipants.objects.filter(
                                                    conferenceroom=conferenceroom,
                                                    user=user)
        except:
            return HttpResponse(401)
        # check current user role or privilege
        try:
            if conferenceroom_user.special_privilege:
                special_privilege = conferenceroom_user.special_privilege.split(",")
            else:
                special_privilege = []

            try:
                # get current privilege wrt Role
                for prv in conferenceroom_user.role.conferenceroomroleprivilegemap_set.all():
                    special_privilege.append(prv.privilege.privilege_type)
            except:
                return HttpResponse(400)

            check_privilege = [i for i in special_privilege if i in ['event_management']]

            if user == conferenceroom.owner or check_privilege:
                ConferenceRoomParticipants.objects.filter(conferenceroom=conferenceroom).delete()
                conferenceroom.status = 'CAN'
                conferenceroom.save()
                return HttpResponse(200)
            return HttpResponse(401)
        except:
            pass
    else:
        return HttpResponse(404)