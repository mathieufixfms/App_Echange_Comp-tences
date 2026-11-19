from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = "exchange"

urlpatterns = [
	path("",views.index,name="index",),
	
	path("login/",auth_views.LoginView.as_view(template_name="exchange/login.html"),name="login",),
	
	path("logout/",auth_views.LogoutView.as_view(),name="logout",),
	
	path("my-skills/",views.my_skills,name="my_skills",),
	
	path( "my-availabilities",views.my_availabilities,name="my_availabilities",),
	
	path("my-help-requests/",views.my_help_requests,name="my_help_requests",),
]