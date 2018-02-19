from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.


class ConferenceRoom(models.Model):
    """
    A class to maintain room conference details
    """
    id = models.AutoField(primary_key=True)
    room_key = models.CharField(max_length=32, blank=False, db_index=True)
    owner = models.ForeignKey(User)
    # metadata id is ref to metadata field
    metadata_id = models.CharField(max_length=255, blank=True, null=True, default=None)
    # json data for metadata field
    metadata_info = models.TextField()
    start_time = models.DateTimeField(default=datetime.now())
    end_time = models.DateTimeField(default=datetime.now())
    STATUS_CHOICES = (
        ('SCH','Scheduled'),
        ('COM','Completed'),
        ('RUN','Running')
        ('CAN','Cancelled')
        ('RES','Rescheduled'),
    )
    status = models.CharField(max_length=3,
                            choices=STATUS_CHOICES,
                            default='SCH')

    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ConferenceRoomParticipants(models.Model):
    """
    A class to maintain room conference participants list
    """
    id = models.AutoField(primary_key=True)
    conferenceroom = models.ForeignKey(ConferenceRoom)
    user = models.ForeignKey(User)
    role = models.ForeignKey(ConferenceRoomRoles)
    STATUS_CHOICES = (
        ('BLK','Blocked'),
        ('ALW','Allowed'),
    )
    status = models.CharField(max_length=3,
                            choices=STATUS_CHOICES,
                            default='ALW')
    last_seen_heartbeat = models.DateTimeField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class ConferenceRoomRoles(models.Model):
    """
    A class to define User role permissions in ConferenceRoom
    """
    id = models.AutoField(primary_key=True)
    ROLE_CHOICES = (
        ('OWN', 'Owner'),
        ('OPA', 'OnlyParticipant'),
        ('SOP', 'ShareOnlyParticipant'),
        ('ROP', 'RecordOnlyParticipant'),
        ('SRP', 'ShareRecordParticipant'),
        ('MOD', 'Moderator'),
    )
    role = models.CharField(max_length=3,
                            choices=ROLE_CHOICES,
                            default='OPA')
    allow_screen_share = models.BooleanField(default=False)
    allow_record_video = models.BooleanField(default=False)
    allow_mute_management = models.BooleanField(default=False)
    allow_remove_user = models.BooleanField(default=False)
    allow_block_user = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
