"""vidu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rooms import views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views

urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^signup/$', accounts_views.signup, name='signup'),
	url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
	url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
	url(r'^settings/$', accounts_views.settings, name='settings'),
	url(r'^settings/password/$', accounts_views.password, name='password'),
	url(r'^settings/update/$', accounts_views.update_username, name='update_username'),
	url(r'^rooms/(?P<pk>\d+)/$', views.show_room, name='show_room'),
	url(r'^shared-rooms/(?P<signed_pk>[0-9]+/[A-Za-z0-9_=-]+)/$', views.show_shared_room, name='shared-room'),
	url(r'^new_room/$', views.new_room, name='new_room'),
	url(r'^update_room/$', views.update_room, name='update_room'),
	url(r'^post_comment/$', views.post_comment, name='post_comment'),
	url(r'^get_comment/$', views.get_comment, name='get_comment'),
	url(r'^invite/$', views.invite, name='invite'),
	url(r'^respond/$', views.respond, name='respond'),
	url(r'^get_connection/$', views.get_connections, name='get_connections'),
	url(r'^delete_room/$', views.delete_room, name='delete_room'),
	url(r'^oauth/', include('social_django.urls', namespace='social')),
	url(r'^admin/', admin.site.urls),
]
