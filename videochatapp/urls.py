from django.conf.urls import include, url
from . import views

urlpatterns = [

    url(r'^$', views.home, name='home'),
    url(r'^videochat/(?P<roomkey>[a-zA-Z0-9]+)/join$',views.join_videochat,name="joinvideochat"),
    url(r'^videochat/createvideochatroom/$',views.create_videochat_room,name="createvideochatroom"),
    url(r'^videochat/recordconference', views.record_videochat, name="recordconference"),
    url(r'^videochat/(?P<conferenceroomid>\d+)/editconference/', 
                views.edit_videochat_conference, name="editconference"),
    url(r'^videochat/listconferences/$',views.list_videochat,name="listconferences"),
    url(r'^videochat/cancelconference$', views.cancel_videochat, name="cancelconference"),

    url(r'^videochat/start$', views.start_videochat, name="startvideochat"),
    url(r'^videochat/end$', views.end_videochat, name="endvideochat"),
]
