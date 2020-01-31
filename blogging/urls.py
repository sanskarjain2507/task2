from django.urls import path
from . import views

urlpatterns = [
     path("", views.login_page, name='login'),
     path("login",views.login_page),
     path("homepage",views.homepage),
     path("register",views.register_user,name='register'),
     path("register_success",views.register_success),
     path("on_login_success",views.on_login),
     path("create_blog",views.create_blog),
     path("on_submit_blog",views.submit_blog),
     path("user_search",views.user_search),
     path("user_logout",views.user_logout),
     path("ajax/validate_username/",views.validate_username),

    ]