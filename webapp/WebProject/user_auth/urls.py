from django.urls import path

from . import views

urlpatterns = [
    path('', views.signin, name='signin'),
    path('user/register', views.registerPage, name='registerPage'),
]