from django.contrib import admin
from .models import ConferenceRoomRoles,ConferenceRoom,ConferenceRoomParticipants
# Register your models here.
admin.site.register(ConferenceRoomRoles)
admin.site.register(ConferenceRoom)
admin.site.register(ConferenceRoomParticipants)


