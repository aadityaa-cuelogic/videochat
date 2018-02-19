from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^$', views.home, name='home'),
	# url(r'videochat', views.videochat, name='videochat' ),
	url(r'^videochat/(?P<roomkey>[a-zA-Z0-9]+)/$',views.videochat,name="videochat")
]
