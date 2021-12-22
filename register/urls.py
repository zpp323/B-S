from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginredirection, name='loginredirection0'),
    path('log/', views.log, name='login'),
    path('reg/', views.reg, name='register'),

]