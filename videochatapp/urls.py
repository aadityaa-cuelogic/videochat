from django.conf.urls import include, url
from . import views

urlpatterns = [

    url(r'^$', views.home, name='home'),
    url(r'^videochat/(?P<roomkey>[a-zA-Z0-9]+)/join$',views.join_videochat,name="joinvideochat"),
    url(r'^videochat/createvideochatroom/$',views.create_videochat_room,name="createvideochatroom")

]
