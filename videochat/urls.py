from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from videochat.views import register

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('videochatapp.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^register/$', register, name='register')
]
